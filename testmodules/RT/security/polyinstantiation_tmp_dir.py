#!/usr/bin/python
"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[Security] Polyinstantiation of /tmp and /var/tmp for new application by using pam_namespace
https://tcms.engineering.redhat.com/case/122331/?from_plan=4962
"""

import os
import sys

import rhtest
import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[Security] Polyinstantiation of /tmp and /var/tmp for new application by using pam_namespace"
        self.info(self.summary)
        try:
            test_name = self.config.test_variant
        except:
            self.info("WARN: Missing OPENSHIFT_test_name, used `php` as default.")
            test_name= "php"

        self.app_type = common.app_types[test_name]
        self.app_name1 = test_name + "1"
        self.app_name2 = test_name + "2"

        if test_name == "php":
            file_name = "polyinstantiation_tmp_dir_index.php"
            self.source_file = "%s/data/%s" %(WORK_DIR, file_name)
            self.target_file1 = "%s/php/index.php" %(self.app_name1)
            self.target_file2 = "%s/php/index.php" %(self.app_name2)
            self.url_path1 = "index.php?action=create"
            self.url_path2 = "index.php"
        elif test_name == "wsgi":
            file_name = "polyinstantiation_tmp_dir_application.py"
            self.source_file = "%s/data/%s" %(WORK_DIR, file_name)
            self.target_file1 = "%s/wsgi/application" %(self.app_name1)
            self.target_file2 = "%s/wsgi/application" %(self.app_name2)
            self.url_path1 = "create"
            self.url_path2 = "show"
        elif test_name == "perl":
            file_name = "polyinstantiation_tmp_dir_index.pl"
            self.source_file = "%s/data/%s" %(WORK_DIR, file_name)
            self.target_file1 = "%s/perl/index.pl" %(self.app_name1)
            self.target_file2 = "%s/perl/index.pl" %(self.app_name2)
            self.url_path1 = "index.pl?action=create"
            self.url_path2 = "index.pl"
        elif test_name == "rack":
            file_name = "polyinstantiation_tmp_dir_rack/*"
            self.source_file = "%s/data/%s" %(WORK_DIR, file_name)
            self.target_file1 = "%s/"  %(self.app_name1)
            self.target_file2 = "%s/"  %(self.app_name2)
            self.url_path1 = "create"
            self.url_path2 = "show" 
        else:
            raise TestSuiteAbort("unknown variant: %s"%self.test_variant)

        tcms_testcase_id=122331
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name1, self.app_name2))

class PolyinstantiantionTmpDir(OpenShiftTest):
    def test_method(self):
        self.info("1. Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name1, self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
        self.assert_equal(0, ret, "App#1 should be created successfully")  

        self.info("2. Copying test files to app git repo")
        ret = common.command_get_status("cp -f %s %s" %(self.source_file, self.target_file1))
        self.assert_equal(0, ret)

        self.info("3. Do git commit")
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name1))
        self.assert_equal(0, ret, "File and directories are added to your git repo successfully")

        app_url = OSConf.get_app_url(self.app_name1)

        self.info("4. Access app's URL to create files in tmp directory")
        ret = common.grep_web_page("%s/%s" %(app_url, self.url_path1), ["RESULT=0"])

        self.assert_equal(0, ret, "RESULT=0 should be seen in output of %s"%app_url)

        self.info("5. Create another %s application" %(self.app_type))
        ret = common.create_app(self.app_name2, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
        self.assert_equal(0, ret, "App#2 should be created successfully")

        self.info("6. Copying test files to app git repo")
        common.command_get_status("cp -f %s %s" %(self.source_file, self.target_file2))
        self.assert_equal(0, ret, "Copy should be done.")


        self.info("7. Do git commit")
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name2))
        self.assert_equal(0, ret, "File and directories are added to your git repo successfully")

        self.info("8. Get app url")
        app_url = OSConf.get_app_url(self.app_name2)
        
        self.info("9. Access app's URL to check files in tmp directory")
        common.grep_web_page("%s/%s" %(app_url, self.url_path2), 
                             ["RESULT=1", "No such file or directory"])
        self.assert_equal(ret, 0,"Files is created in tmp directory")

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PolyinstantiantionTmpDir)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
