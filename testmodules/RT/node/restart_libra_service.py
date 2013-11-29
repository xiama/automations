"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[rhc-node] All created applications will restart when restart libra service as root
https://tcms.engineering.redhat.com/case/122333/?from_plan=4962
"""

import sys
import os

import testcase, common, OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary = "[rhc-node] All created applications will restart when restart libra service as root"
        self.libra_server = common.get_instance_ip()
        self.app_name = "myapp"
        self.app_type = common.app_types["php"]
        self.steps_list = []
        common.env_setup()
        tcms_testcase_id=122333

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class RestartLibraServiceDevenv(OpenShiftTest):
    def test_method(self):
        testcase.TestCaseStep("Create an app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd, False],
                expect_return=0).run()
   
        def get_pgrep_command():
            uuid = OSConf.get_app_uuid(self.app_name)
            return 'pgrep -u %s -P 1'%uuid

        self.info("Log into express server, get app's process ID")
        (status, output) = common.run_remote_cmd_as_root(get_pgrep_command())
        self.assert_equal(status,0, "SSH Command must be run successfully")
        pid1=output
        self.assert_equal(status,0, "SSH Command must be run successfully")

        self.info("Log into express server, restart libra service")
        (status, output) = common.run_remote_cmd_as_root('/etc/init.d/libra restart')
        self.assert_equal(status,0, "SSH Command must be run successfully")

        self.info("Log into express server, get app's process ID")
        (status, output) = common.run_remote_cmd_as_root(get_pgrep_command()) 
        self.assert_equal(status,0, "SSH Command must be run successfully")
        pid2=output


        testcase.TestCaseStep("Access app's URL to confirm it is running fine",
                "curl -H 'Pragma: no-cache' %s",
                string_parameters = [OSConf.get_app_url_X(self.app_name)],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift"],
                expect_description="Access page successfully").run()

        if pid1 == pid2:
            self.info("App's process id before and after restart libra service does not have any change.")
            return self.failed("%s failed" % self.__class__.__name__)
        else:
            return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RestartLibraServiceDevenv)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
