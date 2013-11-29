"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[Security] Delete old files from tmp automatically
https://tcms.engineering.redhat.com/case/122329/?from_plan=4962
"""

import os, sys
import rhtest

import testcase
import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary = "[Security] Delete old files from tmp automatically",
        libra_server = common.get_instance_ip()
        self.app_type = "php-5.3"
        self.app_name = "SecurityTestApp"
        self.steps_list = []
        tcms_testcase_id=122329
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class DeleteOldFilesFromTmpDevenv(OpenShiftTest):
    def test_method(self):
        self.info("Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret,0,"App should be created successfully")

        source_file = "%s/data/delete_old_files_from_tmp_devenv.php" %(WORK_DIR)
        target_file = "%s/php/index.php" %(self.app_name)
        self.info("Copying test files to app git repo")
        ret = common.command_get_status("cp -f %s %s" %(source_file, target_file))
        self.assert_equal(ret,0, "Copy must be done")

        self.info("Do git commit")
        ret = common.command_get_status("cd %s && git add . && git commit -m test && git push" %(self.app_name))
                
        self.assert_equal(ret, 0, "File and directories are added to your git repo successfully")
 
        self.info("Get app url")
        app_url= OSConf.get_app_url(self.app_name)

        self.info("Access app's URL to create files in tmp directory")
        ret = common.grep_web_page("%s/index.php?action=create"%app_url, "RESULT=0")
        self.assert_equal(ret, 0, "RESULT=0 should be seen in output")

        self.info("Log into express server, run /etc/cron.daily/openshift_tmpwatch.sh")
        (ret, output) = common.run_remote_cmd_as_root("/bin/sh /etc/cron.daily/openshift_tmpwatch.sh")

        self.info("Access app's URL to check files in tmp directory")
        ret = common.grep_web_page(app_url, ["RESULT=1", "No such file or directory"])
        self.assert_equal(ret, 0, "RESULT=1 should be seen in output")

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DeleteOldFilesFromTmpDevenv)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
