#!/usr/bin/env python
import os
import common, OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info(("[US566][rhc-client] Archive/Restore app with embeded "
                   "mysql db data to updated application\n"
                   "[US569][rhc-cartridge] embed MySQL instance to an app"))
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing variant. Running test with default zend")
            self.test_variant = "jbossews"

        self.info("VARIANT: %s"%self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)

        if self.test_variant == "perl":
            file_name = "index.pl"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, 
                                                                     file_name)
            target_file = "%s/perl/index.pl" %(self.app_name)
            url_path1 = "index.pl?action=create"
            url_path2 = "index.pl?action=modify"
            url_path3 = "index.pl"
        elif self.test_variant in ("php", "zend"):
            file_name = "index.php"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, 
                                                                     file_name)
            target_file = "%s/php/index.php" %(self.app_name)
            url_path1 = "index.php?action=create"
            url_path2 = "index.php?action=modify"
            url_path3 = "index.php"
        elif self.test_variant in ("rack", "ruby", "ruby-1.9"):
            file_name = "rack/*"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, 
                                                                     file_name)
            target_file = "%s/" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("wsgi", "python"):
            file_name = "application.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR, 
                                                                     file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-2.7"):
            file_name = "applicationpython-2.7.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR,
                                                                     file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-3.3"):
            file_name = "applicationpython-3.3.py"
            source_file = "%s/data/snapshot_restore_mysql_data/%s" %(WORK_DIR,
                                                                     file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("jbossews", "jbossews2"):
            file_name = "test_ews.jsp"
            source_file = "%s/data/snapshot_restore_mysql_data/%s"% (WORK_DIR,
                                                                     file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        elif self.test_variant in ("jbossas", "jbosseap"):
            file_name = "test.jsp"
            source_file = "%s/data/snapshot_restore_mysql_data/%s"% (WORK_DIR,
                                                                     file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        else:
            raise rhtest.TestIncompleteError("Unknown variant:%s"%self.test_variant)

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


class SnapshotRestoreMysqlDataToExistingApp(OpenShiftTest):
    def test_method(self):
        self.add_step("Create a %s application" %(self.app_type),
                      common.create_app,
                      function_parameters = [self.app_name, self.app_type, 
                                           self.user_email, self.user_passwd],
                      expect_return = 0,
                      expect_description = "App should be created successfully")
	
        self.add_step("Get app url",
                      OSConf.get_app_url,
                      function_parameters = [self.app_name])

        self.add_step("Add mysql to this app",
                      common.embed,
                      function_parameters = [self.app_name, "add-mysql-5.1", 
                                           self.user_email, self.user_passwd],
                      expect_return = 0)

        self.add_step("Copying test files to app git repo",
                      "cp -f %s %s" %(self.source_file, self.target_file),
                      expect_return = 0)

        self.add_step("Get embeded mysql info - password",
                      OSConf.get_embed_info,
                      function_parameters = [self.app_name, 
                                             "mysql-5.1", 
                                             "password"])
        self.add_step("Get embeded mysql info - url",
                                  OSConf.get_embed_info,
                                  function_parameters = [self.app_name,
                                                       "mysql-5.1",
                                                       "url"])
        self.add_step("Get embeded mysql info - username",
                                  OSConf.get_embed_info,
                                  function_parameters = [self.app_name,
                                                       "mysql-5.1",
                                                       "username"])
        if self.test_variant in ("rack", "ruby-1.9", "ruby"):
            modify_file = "%s/config.ru" %(self.app_name)
        else:
            modify_file = self.target_file
        if self.test_variant in ("jbossas","jbosseap"):
            command = ("echo 'Skip this step for jbossas app, because "
                       "these are done automatcially by jboss server "
                       "at server side'")
        elif self.test_variant in ("jbossews", "jbossews2"):
            command = ( "cd %s/src/main/webapp/ && "
                        " mkdir -p WEB-INF/lib && "
                        " cp %s/../cartridge/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar WEB-INF/lib/ "
                        ) % (self.app_name, WORK_DIR)
        elif self.test_variant == "python-2.7":
            command = ("cp -f %s/../client/data/snapshot_restore_mysql_data/setupmysql.py %s/setup.py && "
                       #"sed -i -e \"s/^.*install_requires.*$/      install_requires=['MySQL-python'],/g\" %s/setup.py && "
                       "sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' "
                       " -e '{s/changeme_password/__OUTPUT__[5]/}'"
                       " -e '{s/changeme_url/__OUTPUT__[6]/}' "
                       " -e '{s/changeme_db/%s/}' %s" )%(WORK_DIR,self.app_name, 
                                                         self.app_name,
                                                         modify_file)
        elif self.test_variant == "python-3.3":
            command = ("cp -f  %s/../client/data/snapshot_restore_mysql_data/setupmysql33.py %s/setup.py && "
			#"sed -i -e \"s/^.*install_requires.*$/      install_requires=['mysql-connector-python'],/g\" %s/setup.py && "
                       "sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' "
                       " -e '{s/changeme_password/__OUTPUT__[5]/}'"
                       " -e '{s/changeme_url/__OUTPUT__[6]/}' "
                       " -e '{s/changeme_db/%s/}' %s" )%(WORK_DIR,self.app_name,self.app_name,
                                                         modify_file)
        else:
            command = ("sed -i -e '{s/changeme_username/__OUTPUT__[7]/}' "
                       " -e '{s/changeme_password/__OUTPUT__[5]/}'"
                       " -e '{s/changeme_url/__OUTPUT__[6]/}' "
                       " -e '{s/changeme_db/%s/}' %s" )%(self.app_name, 
                                                         modify_file)
        self.add_step("Modify test files according to mysql info",
                      command,
                      expect_return = 0)
        self.add_step("Do git commit",
                      ("cd %s && git add . && git commit -m test "
                       " && git push")% (self.app_name),
                      expect_description = ("File and directories are added "
                                            "to your git repo successfully"),
                      expect_return = 0)
        self.add_step("Access app's URL to create mysql data",
                      "curl -s -H 'Pragma:no-cache' __OUTPUT__[2]/%s" %(self.url_path1),
                      expect_str = ["Welcome", self.key_string1],
                      try_interval = 12,
                      try_count = 10,
                      expect_return = 0)
        self.add_step("Take snapshot",
                      ("rhc snapshot save %s -f %s %s "
                       " -l %s -p '%s'")% ( self.app_name, 
                                            "%s.tar.gz"%(self.app_name),
                                            common.RHTEST_RHC_CLIENT_OPTIONS,
                                            self.user_email, 
                                            self.user_passwd),
                      expect_return = 0)
        self.add_step("Access app's URL to create modify mysql data",
                      "curl -s -H 'Pragma:no-cache' __OUTPUT__[2]/%s" %(self.url_path2),
                      expect_return = 0,
                      expect_str = ["Welcome", self.key_string2],
                      try_interval = 12,
                      try_count = 10)
        self.add_step("Restore app from snapshot", 
                      ("rhc snapshot restore %s -f %s %s "
                       "-l %s -p '%s'") %(  self.app_name, 
                                            "%s.tar.gz"%(self.app_name), 
                                            common.RHTEST_RHC_CLIENT_OPTIONS,
                                            self.user_email, 
                                            self.user_passwd),
                      expect_return = 0)
        self.add_step("Access app's URL to check mysql data is restored",
                      "curl -s -H 'Pragma:no-cache' __OUTPUT__[2]/%s" %(self.url_path3),
                      expect_str = ["Welcome", self.key_string1],
                      try_interval = 12,
                      try_count = 10,
                      expect_return = 0)
        self.add_step("Remove mysql from this app",
                      common.embed,
                      function_parameters = [self.app_name, "remove-mysql-5.1", 
                                             self.user_email, self.user_passwd],
                      expect_return = 0)
        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreMysqlDataToExistingApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
