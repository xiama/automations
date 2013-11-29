"""
Attila Nagy
anagy@redhat.com
Jun 25, 2012

[US1386][Runtime][cartridge]Snapshot and restore PostgreSQL data to new app
https://tcms.engineering.redhat.com/case/128841/
"""

import os
import rhtest
import common
import OSConf

class OpenShiftTest(rhtest.Test):

    def initialize(self):
        self.summary = "[US1386][Runtime][cartridge]Snapshot and restore PostgreSQL-9.2 data to new app"
        self.info(self.summary)
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing self.config.test_variant, using `php` as default")
            self.test_variant='php'

        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        self.info("VARIANT: %s"%self.test_variant)
        self.info("SCALABLE: %s"%self.scalable)
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(7)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        common.env_setup()
        

    def finalize(self):
        #Removing snapshot file
        os.system("rm -f %s.tar.gz"%self.app_name)
        
    def run_sql(self, sql_commands = []):
        command = 'echo "%s" | psql -F, -t -A "dbname=%s host=%s user=%s password=%s port=%s"' % (
                  ";\n".join(sql_commands),
                  self.sql_credentials["database"],
                  self.sql_credentials["url"],
                  self.sql_credentials["username"],
                  self.sql_credentials["password"], 
                  self.sql_credentials["port"])
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
                                    clone_repo = False)

        self.assert_equal(0, ret, "Error creating app.")
        
        self.info("=================================")
        self.info("2. Embed PostgreSQL")
        self.info("=================================")
        #ret = common.embed(self.app_name, "add-" + common.cartridge_types["postgresql"])
        #self.assert_equal(0, ret, "Error embedding app.")
        common.embed(self.app_name, "add-" + common.cartridge_types["postgresql-9.2"])
        #
        # Reading PostgreSQL credentials from local cache
        #
        user = OSConf.OSConf()
        user.load_conf()
        #self.sql_credentials = user.conf["apps"][self.app_name]['embed'][common.cartridge_types["postgresql"]]
        #print user.conf["apps"][self.app_name]['embed']
        self.sql_credentials = user.conf["apps"][self.app_name]['embed'][common.cartridge_types["postgresql-9.2"]]

        
        if self.scalable:
            self.info("=================================")
            self.info("3. Scale up")
            self.info("=================================")
            ret = common.scale_up(self.app_name)
            self.assert_equal(0, ret, "Unable to scale_up.")

        self.info("=================================")
        self.info("4. Write data into PostgreSQL")
        self.info("=================================")
        sql_commands = [
            r"DROP TABLE IF EXISTS testing",
            r"CREATE TABLE testing ( text VARCHAR(50) )"
        ]
        for i in range(0, 10):
            sql_commands.append(r"INSERT INTO testing VALUES ( '%s' )" % common.getRandomString())
        (ret,output) = self.run_sql(sql_commands)
        self.assert_equal(0, ret, "Error executing sql commands.")
            
        self.info("=================================")
        self.info("4. Create snapshot")
        self.info("=================================")
        (ret, output) = common.command_getstatusoutput("rhc snapshot save %s -l %s -p '%s' %s" % ( self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        self.assert_equal(0, ret, "Unable to create a snapshot.")
        
        self.info("=================================")
        self.info("5. Remove app and create another one")
        self.info("=================================")
        ret =common.destroy_app(self.app_name)
        self.assert_equal(0, ret, "Unable to remove app.")
        #self.new_app_name = self.test_variant.split('-')[0] + common.getRandomString(8)
        if self.scalable:
            ret = common.create_scalable_app(self.app_name, self.app_type, clone_repo = True, disable_autoscaling=True)
        else:
            ret = common.create_app(self.app_name, self.app_type, clone_repo = False)
        self.assert_equal(0, ret, "Error creating app.")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["postgresql-9.2"])
        self.assert_equal(0, ret, "Error embedding app with Postgresql.")
        # Updating local cache
        user = OSConf.OSConf()
        user.load_conf()
        self.sql_credentials = user.conf["apps"][self.app_name]['embed'][common.cartridge_types["postgresql-9.2"]]
        #HOT FIX for Bug 912255, obtaining db credentials from env vars, instead of REST API
        #self.sql_credentials = OSConf.get_db_cred('POSTGRESQL')
        
        self.info("=================================")
        self.info("6. Restore from snapshot")
        self.info("=================================")
        (ret, output) = common.command_getstatusoutput("rhc snapshot restore %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        self.assert_equal(0, ret, "Unable to restore app from snapshot.")
        
        self.info("=================================")
        self.info("7. Ensure that data is restored")
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
