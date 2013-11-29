#!/usr/bin/python

#
#  File name: mms_agent_without_mongodb.py
#  Date:      2012/02/27 07:29
#  Author:    mzimen@redhat.com
#

import sys
import os

import testcase, common, OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1352][UI][rhc-client]Embed mms-agent without mongodb embeded"
        self.app_name = common.getRandomString(10)
        self.app_type = 'php'
        self.tcms_testcase_id = 126400
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class MmsAgentWithoutMongodb(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create an app",
                 common.create_app,
                 function_parameters=[self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True],
                 expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Upload settings.php" ,
                '''
                cd %s &&
                mkdir -p .openshift/mms &&
                cat <<EOF >.openshift/mms/settings.php
this is settings.php
EOF
                git add .openshift/mms/settings.php
                git commit -m "settings.php" &&
                git push
                '''%(self.app_name),
                expect_return=0,
                expect_string_list = [], 
                expect_description="Uploading settings.php should pass."))

        self.steps_list.append(testcase.TestCaseStep("Embed with 10gen-mms-agent",
                 common.embed,
                 function_parameters=[self.app_name, 'add-%s'%common.cartridge_types['10gen'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                 expect_string_list = ["MongoDB must be embedded before the 10gen MMS Agent"],
                 expect_return="!0"))

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
    suite.add_test(MmsAgentWithoutMongodb)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of mms_agent_without_mongodb.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
