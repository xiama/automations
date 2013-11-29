#!/usr/bin/env python

import os

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import common, OSConf
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US566][rhc-client]Archive an existing app with embedded mysql db and restore data to new created application")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = "jbossews"

        self.info("VARIANT: %s"%self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.new_app_name = common.getRandomString(9)
        if self.test_variant == "perl":
            file_name = "index.pl"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/perl/index.pl" %(self.app_name)
            url_path1 = "index.pl?action=create"
            url_path2 = "index.pl?action=modify"
            url_path3 = "index.pl"
        elif self.test_variant in ("php", "zend"):
            file_name = "index.php"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/php/index.php" %(self.app_name)
            url_path1 = "index.php?action=create"
            url_path2 = "index.php?action=modify"
            url_path3 = "index.php"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            file_name = "rack/*"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python", "wsgi"):
            file_name = "application.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-2.7"):
            file_name = "applicationpython-2.7.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-3.3"):
            file_name = "applicationpython-3.3.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("jbosseap", "jbossas"):
            file_name = "test.jsp"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        elif self.test_variant in ("jbossews", "jbossews2"):
            file_name = "test_ews.jsp"
            source_file = "%s/data/snapshot_restore_mysql_data/%s"% (WORK_DIR,
                                                                     file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        else:
            raise rhtest.TestIncompleteError("Unknown variant: %s"%self.test_variant)

        self.file_name = file_name
        self.target_file = target_file
        self.source_file = source_file
        self.url_path1 = url_path1
        self.url_path2 = url_path2
        self.url_path3 = url_path3
        self.key_string1 = "speaker1, title1"
        self.key_string2 = "speaker2, title2"

        common.env_setup()

    def finalize(self):
        pass

class SnapshotRestoreMysqlDataToNewApp(OpenShiftTest):
    def test_method(self):
        # 1
        self.add_step("Create a %s application" %(self.app_type),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                expect_return=0,
                expect_description="App should be created successfully")

        # 2
        self.add_step("Get app url",
                OSConf.get_app_url,
                function_parameters = [self.app_name])
        # 3
        self.add_step("Enable embeded mysql for this app",
                common.embed,
                function_parameters=[self.app_name, "add-mysql-5.1", self.user_email, self.user_passwd],
                expect_return=0)
        # 4
        self.add_step("Copying test files to app git repo",
                "cp -f %s %s" %(self.source_file, self.target_file),
                expect_return=0)
        # 5
        self.add_step("Get embeded mysql info - password",
                OSConf.get_embed_info,
                function_parameters=[self.app_name, "mysql-5.1", "password"])
        # 6
        self.add_step("Get embeded mysql info - url",
                OSConf.get_embed_info,
                function_parameters=[self.app_name, "mysql-5.1", "url"])
        # 7
        self.add_step("Get embeded mysql info - username",
                OSConf.get_embed_info,
                function_parameters=[self.app_name, "mysql-5.1", "username"])

        if self.test_variant in ("rack", "ruby", "ruby-1.9"):
            modify_file = "%s/config.ru" %(self.app_name)
        else:
            modify_file = self.target_file
        if self.test_variant in ("jbosseap", "jbossas"):
            command = "echo 'Skip this step for jbossas app, because these are done automatcially by jboss server at server side'"
        elif self.test_variant in ("jbossews", "jbossews2"):
            command = ( "cd %s/src/main/webapp/ && "
                        " mkdir -p WEB-INF/lib && "
                        " cp %s/../cartridge/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar WEB-INF/lib/ "
                        ) % (self.app_name, WORK_DIR)
        elif self.test_variant == "python-2.7":
            command=("cp -f  %s/../client/data/snapshot_restore_mysql_data/setupmysql.py %s/setup.py &&"
                    "sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' -e '{s/changeme_password/__OUTPUT__[5]/}' -e '{s/changeme_url/__OUTPUT__[6]/}' -e '{s/changeme_db/%s/}' %s") %(WORK_DIR,self.app_name,self.app_name, modify_file)
        elif self.test_variant == "python-3.3":
            command=("cp -f  %s/../client/data/snapshot_restore_mysql_data/setupmysql33.py %s/setup.py && "
                    "sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' -e '{s/changeme_password/__OUTPUT__[5]/}' -e '{s/changeme_url/__OUTPUT__[6]/}' -e '{s/changeme_db/%s/}' %s" )%(WORK_DIR,self.app_name,self.app_name, modify_file)
        else:
            command="sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' -e '{s/changeme_password/__OUTPUT__[5]/}' -e '{s/changeme_url/__OUTPUT__[6]/}' -e '{s/changeme_db/%s/}' %s" %(self.app_name, modify_file)
        # 8
        self.add_step("Modify test files according to mysql info",
                command,
                expect_return=0)

        # 9
        self.add_step("Do git commit",
                "cd %s && git add . && git commit -m test && git push" %(self.app_name),
                expect_return=0,
                expect_description="File and directories are added to your git repo successfully")
        # 10
        self.add_step("Access app's URL to create mysql data",
                "curl -H 'Pragma: no-cache' __OUTPUT__[2]/%s" %(self.url_path1),
                expect_return=0,
                expect_str = ["Welcome", self.key_string1],
                try_interval=12,
                try_count=10)
        # 11
        self.add_step("Take snapshot",
                "rhc snapshot save %s -f %s -l %s -p '%s' %s" 
                            %(self.app_name,
                            "%s.tar.gz"%(self.app_name),
                            self.user_email, 
                            self.user_passwd,
                            common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0)
        # 12
        self.add_step("Destroy app",
                common.destroy_app,
                function_parameters=[self.app_name, 
                                     self.user_email, 
                                     self.user_passwd,
                                     True],
                expect_return=0)
        # 13
        self.add_step("Re-create this application",
                common.create_app,
                function_parameters=[self.new_app_name, 
                                     self.app_type, 
                                     self.user_email, 
                                     self.user_passwd, 
                                     False],
                expect_return=0,
                expect_description="App should be created successfully")
        # 14
        self.add_step("Re-enable embeded mysql for this app",
                common.embed,
                function_parameters=[self.new_app_name, 
                                    "add-mysql-5.1", 
                                    self.user_email, 
                                    self.user_passwd],
                expect_return=0)
        # 15
        self.add_step("Get embeded mysql info - password",
                OSConf.get_embed_info,
                function_parameters=[self.new_app_name, 
                                    "mysql-5.1", 
                                    "password"])
        # 16
        self.add_step("Get embeded mysql info - url",
                OSConf.get_embed_info,
                function_parameters=[self.new_app_name, 
                                     "mysql-5.1", 
                                     "url"])
        # 17
        self.add_step("Get new app git repo url",
                OSConf.get_git_url,
                function_parameters=[self.new_app_name])
        # 18
        self.add_step("Get embeded mysql info - username",
                OSConf.get_embed_info,
                function_parameters=[self.new_app_name, "mysql-5.1", "username"])
        # 19
        self.add_step("Restore app from snapshot",
                "rhc snapshot restore %s -f %s -l %s -p '%s' %s" 
                        %(self.new_app_name,
                        "%s.tar.gz"%(self.app_name),
                        self.user_email, 
                        self.user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0)
        # 20
        self.add_step("Git clone restored app repo",
                "git clone __OUTPUT__[17]", 
                expect_return=0)

        if self.test_variant in ("rack", "ruby-1.9", "ruby"):
            modify_file = "%s/config.ru" %(self.new_app_name)
        else:
            modify_file = self.target_file.replace(self.app_name, self.new_app_name)
        if self.test_variant in ("jbossas", "jbosseap", "jbossews", "jbossews2"):
            command = "echo 'Skip this step for jbossas app, because these are done automatcially by jboss server at server side'"
        
        else:
            command = "sed -i -e '{s/__OUTPUT__[7]/__OUTPUT__[18]/}' -e '{s/__OUTPUT__[5]/__OUTPUT__[15]/}' -e '{s/__OUTPUT__[6]/__OUTPUT__[16]/}' %s" %(modify_file)
        # 21
        self.add_step("Modify test files according to new mysql info",
                command,
                expect_return=0)

        if self.test_variant in ("jbosseap", "jbossas", "jbossews", "jbossews2"):
            command = "echo 'Skip this step for jbossas app, because no new change to commit'"
        else:
            command="cd %s && pwd; git add . && git commit -a -m test && git push" %(self.new_app_name)
        # 22
        self.add_step("Do git commit",
                command,
                expect_return=0)

        # 23
        self.add_step("Get app url",
                OSConf.get_app_url,
                function_parameters = [self.new_app_name])
        # 24
        self.add_step("Access app's URL to check mysql data is restored",
                "curl -H 'Pragma: no-cache' __OUTPUT__[23]/%s" %(self.url_path3),
                expect_return=0,
                expect_str = ["Welcome", self.key_string1],
                try_interval=12,
                try_count=10)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreMysqlDataToNewApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
