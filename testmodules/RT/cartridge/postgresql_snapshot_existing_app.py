"""
Attila Nagy
anagy@redhat.com
Jun 25, 2012

[US1386][Runtime][cartridge]Snapshot and restore PostgreSQL data to existing app
https://tcms.engineering.redhat.com/case/128840/
"""

import os
import rhtest
import common
import OSConf

class OpenShiftTest(rhtest.Test):

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing self.config.test_variant, using `php` as default")
            self.test_variant='ruby'

        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False

        self.info("VARIANT: %s"%self.test_variant)
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(7)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        common.env_setup()
        self.summary = "[US1386][Runtime][cartridge]Snapshot and restore PostgreSQL data to existing app"
        

    def finalize(self):
        #Removing snapshot file
        os.remove("./" + self.app_name + ".tar.gz")
        
    def run_sql(self, sql_commands = []):
        command = 'echo "%s" | psql -F, -t -A "dbname=%s host=%s user=%s password=%s port=%s"' % (
                  ";\n".join(sql_commands),
                  self.sql_credentials["database"],
                  self.sql_credentials["url"],
                  self.sql_credentials["username"],
                  self.sql_credentials["password"],
                  self.sql_credentials["port"]                                                                            
        )
        return common.run_remote_cmd(self.app_name, command)

class PostgresqlSnapshotExistingApp(OpenShiftTest):
    
    def test_method(self):
        self.info("=================================")
        self.info("1. Create an application")
        self.info("=================================")
        if self.scalable:
            ret = common.create_scalable_app(self.app_name,
                                             self.app_type,
                                             clone_repo = True,
                                             disable_autoscaling=True)
        else:
            ret = common.create_app(self.app_name,
                                    self.app_type,
                                    clone_repo = True)
        self.assert_equal(0, ret, "Error creating app.")
        
        self.info("=================================")
        self.info("2. Embed PostgreSQL")
        self.info("=================================")
        common.embed(self.app_name, "add-" + common.cartridge_types["postgresql"])
        #
        # Reading PostgreSQL credentials from local cache
        #
        user = OSConf.OSConf()
        user.load_conf()
	
        #self.sql_credentials = user.conf["apps"][self.app_name]['embed'][common.cartridge_types["postgresql"]]
        #print user.conf["apps"][self.app_name]['embed']
        self.sql_credentials = user.conf["apps"][self.app_name]['embed']["postgresql-8.4"]
	
        self.info("=================================")
        self.info("3. Write data into PostgreSQL")
        self.info("=================================")
        sql_commands = [
            "DROP TABLE IF EXISTS testing",
            "CREATE TABLE testing ( text VARCHAR(50) )"
        ]
        for i in range(0, 10):
            sql_commands.append("INSERT INTO testing VALUES ( '%s' )" % common.getRandomString())
        self.assert_true(self.run_sql(sql_commands)[0] == 0)
            
        self.info("=================================")
        self.info("4. Create snapshot")
        self.info("=================================")
        common.command_getstatusoutput("rhc snapshot save %s -l %s -p '%s' %s" % ( self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        
        self.info("=================================")
        self.info("5. Write additional data into PostgreSQL")
        self.info("=================================")
        sql_commands = []
        for i in range(0, 10):
            sql_commands.append("INSERT INTO testing VALUES ( '%s' )" % common.getRandomString())
        self.assert_true(self.run_sql(sql_commands)[0] == 0)
        
        self.info("=================================")
        self.info("5. Restore from snapshot")
        self.info("=================================")
        common.command_getstatusoutput("rhc snapshot restore %s -l %s -p '%s' %s" % ( self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        
        self.info("=================================")
        self.info("6. Ensure that data is restored")
        self.info("=================================")
        # It means that there should be only 10 rows in the database
        ( ret_code, ret_output ) = self.run_sql(["SELECT 'Number of records', count(*) FROM testing"])
        self.assert_true(ret_output.find("Number of records,10") != -1)
         
        return self.passed(self.summary)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PostgresqlSnapshotExistingApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
