"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[security]Security - Execute risky system binaries
https://tcms.engineering.redhat.com/case/122334/?from_plan=4962
"""

import os, sys

import rhtest
import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary="Execute risky system binaries on stage/devenv instance"
        self.app_type = common.app_types["php"]
        self.app_name = "SecurityTestApp"

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class ExecuteRiskySystemBinaries(OpenShiftTest):
    def test_method(self):
        self.info("1. Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0,"%s app should be created successfully" %(self.app_name))

        file_name1 = "execute_risky_system_binaries.php"
        file_name2 = "execute_risky_system_binaries.sh"
        source_file1 = "%s/data/%s" %(WORK_DIR, file_name1)
        source_file2 =  "%s/data/%s" %(WORK_DIR, file_name2)
        target_file1 = "%s/php/index.php" %(self.app_name)
        target_file2 = "%s/php/%s" %(self.app_name, file_name2)
        self.info("2. Copying test files to app git repo")
        ret = common.command_get_status("cp -f %s %s && cp -f %s %s" %(source_file1, target_file1, source_file2, target_file2))
                                  
        self.assert_equal(ret, 0,"File and directories are added to your git repo successfully")

        self.info("3. Do git commit")
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name))
                                  
        self.assert_equal(ret, 0, "File and directories are added to your git repo successfully")

        app_url = OSConf.get_app_url(self.app_name)

        self.info("4. Access app's URL to tigger test")
        ret = common.grep_web_page(app_url, "###RESULT###: PASS")
        self.assert_equal(ret, 0, "###RESULT###: PASS must be in %s"%app_url)

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ExecuteRiskySystemBinaries)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
