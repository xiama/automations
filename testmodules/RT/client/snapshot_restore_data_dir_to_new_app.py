#!/usr/bin/env python
import os
import common, OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info(("[US566][rhc-client] Archive an existing app "
                   "and restore data to new created application"))
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing variant, using `php` as default.")
            self.test_variant = "jbossews"

        self.info("VARIANT: %s"%self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        if self.test_variant == "perl":
            file_name = "index.pl"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/perl/index.pl" %(self.app_name)
            url_path1 = "index.pl?action=create"
            url_path2 = "index.pl?action=modify"
            url_path3 = "index.pl"
        elif self.test_variant in ("php", "zend"):
            file_name = "index.php"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/php/index.php" %(self.app_name)
            url_path1 = "index.php?action=create"
            url_path2 = "index.php?action=modify"
            url_path3 = "index.php"
        elif self.test_variant in ("rack", "ruby", "ruby-1.9"):
            file_name = "rack/*"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("wsgi", "python"):
            file_name = "application.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-2.7"):
            file_name = "applicationpython-2.7.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name)
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("python-3.3"):
            file_name = "applicationpython-3.3.py"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/wsgi/application" %(self.app_name) 
            url_path1 = "create"
            url_path2 = "modify"
            url_path3 = "show"
        elif self.test_variant in ("jbossas", "jbosseap", "jbossews", "jbossews-2.0"):
            file_name = "test.jsp"
            source_file = "%s/data/snapshot_restore_data_dir/%s" %(WORK_DIR, file_name)
            target_file = "%s/src/main/webapp/%s" %(self.app_name, file_name)
            url_path1 = "%s?action=create" %(file_name)
            url_path2 = "%s?action=modify" %(file_name)
            url_path3 = "%s" %(file_name)
        else:
            raise rhtest.TestIncompleteError("Unknown variant: %s."%self.test_variant)

        self.file_name = file_name
        self.target_file = target_file
        self.source_file = source_file
        self.url_path1 = url_path1
        self.url_path2 = url_path2
        self.url_path3 = url_path3
        common.env_setup()

    def finalize(self):
        pass


class SnapshotRestoreDataDirToNewApp(OpenShiftTest):
    def test_method(self):
        self.add_step("Create a %s application" %(self.app_type),
                      common.create_app,
                      function_parameters=[self.app_name, self.app_type, 
                                           self.user_email, self.user_passwd],
                      expect_return=0,
                      expect_description="App should be created successfully")

        self.add_step("Copying test files to app git repo",
                      "cp -f %s %s" %(self.source_file, self.target_file),
                      expect_return=0)

        self.add_step("Do git commit",
                      "cd %s && git add . && git commit -m test && git push" %(self.app_name),
                      expect_return=0,
                      expect_description="File and directories are added to your git repo successfully")

        self.add_step("Access app's URL to create files in OPENSHIFT_DATA_DIR directory",
                      self.verify,
                      function_parameters = [self.url_path1, 
                                             ["Welcome", "RESULT=0"]],
                      expect_return=0,
                      try_interval=12,
                      try_count=10)

        self.add_step("Take snapshot",
                      "rhc snapshot save %s -f %s -l %s -p '%s' %s" %(
                            self.app_name,
                            "%s.tar.gz"%(self.app_name),
                            self.user_email, 
                            self.user_passwd,
                            common.RHTEST_RHC_CLIENT_OPTIONS),
                      expect_return=0)

        self.add_step("Destroy app",
                      common.destroy_app,
                      function_parameters=[self.app_name, 
                                           self.user_email, 
                                           self.user_passwd, 
                                           True],
                      expect_return=0)

        self.add_step("Re-create this application",
                      common.create_app,
                      function_parameters=[self.app_name, 
                                           self.app_type, 
                                           self.user_email, 
                                           self.user_passwd],
                      expect_return=0,
                      expect_description="App should be created successfully")

        self.add_step("Restore app from snapshot",
                      "rhc snapshot restore %s -f %s -l %s -p '%s' %s" %(
                            self.app_name,
                            "%s.tar.gz"%(self.app_name),
                            self.user_email, 
                            self.user_passwd,
                            common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_return=0)

        self.add_step("Access app's URL to check OPENSHIFT_DATA_DIR dir is restored",
                      self.verify,
                      function_parameters=[self.url_path3, 
                                           ["Welcome", "snapshot_restore_data_dir_test1"]],
                      expect_return=0,
                      try_interval=12,
                      try_count=10)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


    def verify(self, suffix, str_l):
        url=OSConf.get_app_url(self.app_name)
        return common.grep_web_page("%s/%s"%(url,suffix), str_l )


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreDataDirToNewApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
