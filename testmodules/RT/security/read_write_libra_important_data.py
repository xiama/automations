#!/usr/bin/python
"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[security]Security - Write or modify libra important data
https://tcms.engineering.redhat.com/case/122336/?from_plan=4962
"""

import os
import sys

import rhtest
import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary = "[security]Security - Write or modify libra important data on devenv instance"
        self.app_type = common.app_types["php"]
        self.app_name = "SecurityTestApp"

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class ReadWriteLibraImportantData(OpenShiftTest):
    def test_method(self):
        self.info("Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name, self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
                                  
                                  
        self.assert_equal(ret, 0, "%s app should be created successfully" %(self.app_name))

        if (self.config.options.run_mode in ("STG")):
            file_name1 = "read_write_libra_important_data_stage.php"
            file_name2 = "read_write_libra_important_data_stage.sh"
        elif (self.config.options.run_mode == "DEV"):
            file_name1 = "read_write_libra_important_data_devenv.php"
            file_name2 = "read_write_libra_important_data_devenv.sh"
        else:
            raise TestSuiteAbort("unknown run mode: %s"%self.config.run_mode)
        source_file1 = "%s/data/%s" %(WORK_DIR, file_name1)
        source_file2 =  "%s/data/%s" %(WORK_DIR, file_name2)
        target_file1 = "%s/php/index.php" %(self.app_name)
        target_file2 = "%s/php/%s" %(self.app_name, file_name2)
        self.info("Copying test files to app git repo")
        ret = common.command_get_status("cp -f %s %s && cp -f %s %s" %(source_file1, target_file1, source_file2, target_file2)) 
        self.assert_equal(ret, 0,"File and directories are added to your git repo successfully")

        self.info("Do git commit")
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name))
        self.assert_equal(ret, 0, "File and directories are added to your git repo successfully")


        self.info("Get app url") 
        app_url = OSConf.get_app_url(self.app_name)

        self.info("Access app's URL to tigger test")
        ret = common.grep_web_page(app_url, "###RESULT###: PASS")
        self.assert_equal(ret, 0)

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ReadWriteLibraImportantData)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
