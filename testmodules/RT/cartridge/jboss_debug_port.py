#
#  File name: jboss_debug_port.py
#  Date:      2012/02/13 07:02
#  Author:    mzimen@redhat.com
#

import sys
import os

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary ="[US1614][Runtime][rhc-cartridge] Enable jboss debug port"
        self.ftcms_testcase_id = 129218
        self.app_name = common.getRandomString(10)

        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class JBossDebugPort(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep("Create a sample JBoss app" ,
                common.create_app,
                function_parameters=[self.app_name,common.app_types['jbossas'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Enable jpda",
                '''
                cd %s &&
                touch .openshift/markers/enable_jpda &&
                git add  .openshift/markers/enable_jpda &&
                git commit . -m 'enable jboss debug' &&
                git push
                '''%(self.app_name),
                expect_return=0))

        pexpect_cmd = [
            ('sendline', 'jdb -attach $OPENSHIFT_JBOSSAS_IP:8787'),
            ('expect', 'Initializing jdb'),
            ('expect', '>'),
            ('sendline', 'version'),
            ('expect', 'This is jdb version.*'),
            ('sendline', 'quit'),
            ('sendline', 'exit')]

        self.steps_list.append(testcase.TestCaseStep("connect app via rhcsh, or forward debug port via rhc-port-forward",
                common.rhcsh,
                function_parameters = [self.app_name, pexpect_cmd],
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossDebugPort)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

# end of jboss_debug_port.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
