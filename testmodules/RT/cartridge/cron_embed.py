#
#  File name: cron_embed.py
#  Date:      2012/02/13 10:32
#  Author:    mzimen@redhat.com
#

import sys
import os
import time
import pexpect

import testcase, common, OSConf
import rhtest
# user defined packages
import openshift

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary="[US648][Runtime][rhc-cartridge] Embedded Cron support"
        self.app_name = common.getRandomString(10)
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `python` as default")
            self.test_variant = 'python'
        self.app_type = common.app_types[self.test_variant]
        self.tcms_testcase_id = 130918
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        pass

class CronEmbed(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep("Create a sample application" ,
                common.create_app,
                function_parameters = [self.app_name, 
                                       self.app_type, 
                                       self.config.OPENSHIFT_user_email, 
                                       self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Embed cron",
                common.embed,
                function_parameters = [self.app_name, 
                                       "add-%s"%(common.cartridge_types['cron']), 
                                       self.config.OPENSHIFT_user_email, 
                                       self.config.OPENSHIFT_user_passwd],
                expect_return = 0,
                expect_description = "Embedding Cron should work."))

        self.steps_list.append(testcase.TestCaseStep("Create a new cron job",
                '''
                cd %s &&
                mkdir -p .openshift/cron/minutely &&
                echo 'date +%%T@%%F >> $OPENSHIFT_DATA_DIR/date.txt' > .openshift/cron/minutely/date.sh &&
                git add .openshift/cron/minutely/date.sh &&
                git commit -m "added new cron job" -a &&
                git push
                '''%self.app_name,
                expect_description="Definying new cron task should work.",
                expect_return = 0))

        def check_the_cron(self):
            self.info("Waiting for a minute to get some results from cron...")
            uuid = OSConf.get_app_uuid(self.app_name)
            app_url = OSConf.get_app_url(self.app_name)
            time.sleep(65)
            p = pexpect.spawn('ssh -t -o ConnectTimeout=20 %s@%s "cat $OPENSHIFT_DATA_DIR/date.txt"' % (uuid, app_url))
            p.wait()
            try:
                ret = p.expect("\d{2}:\d{2}:\d{2}@\d{4}-\d{2}-\d{2}")
                return ret
            except pexpect.TIMEOUT, e:
                print "Failed to find data generated by cron job. %s" % (e)
            except pexpect.EOF, e:
                print "Failed to find data generated by cron job. %s" % (e)
            return 1

        self.steps_list.append(testcase.TestCaseStep("Verify it",
                check_the_cron,
                function_parameters = [self],
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep("Stop cron...",
                "rhc cartridge stop %s -a %s -l %s -p '%s' %s"
                    %(common.cartridge_types['cron'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep("Start cron...",
                "rhc cartridge start %s -a %s -l %s -p '%s' %s"
                    %(common.cartridge_types['cron'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return = 0))


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
    suite.add_test(CronEmbed)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of cron_embed.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 