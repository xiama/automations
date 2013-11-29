#
#  File name: embed_jenkins2scalable_app.py
#  Date:      2012/04/05 17:00
#  Author:    mzimen@redhat.com
#

import sys
import os
import time

import rhtest
import testcase
import common
import OSConf


class OpenShiftTest(rhtest.Test):

    def initialize(self):
        self.summary = "[US2091][Runtime][rhc-cartridge]Embed jenkins client to scalable app"
        self.app_name = common.getRandomString(10)
        self.jenkins_name = "js"+common.getRandomString(8)
        self.app_type = 'php'
        tcms_testcase_id = 36316
        self.steps=[]

        common.env_setup()

    def finalize(self):
        try:
            os.system("rm -rf %s %s"%(self.app_name, self.jenkins_name))
            common.destroy_app(self.app_name, 
                               self.config.OPENSHIFT_user_email, 
                               self.config.OPENSHIFT_user_passwd)
            common.destroy_app(self.jenkins_name, 
                               self.config.OPENSHIFT_user_email, 
                               self.config.OPENSHIFT_user_passwd)
        except:
            pass

class EmbedJenkins2scalableApp(OpenShiftTest):
    def verify(self, regex):
        url = OSConf.get_app_url(self.app_name)+"/test.php"
        return common.grep_web_page(url, regex, count=5, delay=7)

    def test_method(self):

        self.steps.append(testcase.TestCaseStep("1. Create an scalable app using REST API",
                common.create_scalable_app,
                function_parameters=[self.app_name, 
                                    common.app_types[self.app_type], 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Scale up.",
                common.scale_up,
                function_parameters=[self.app_name,],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Create a jenkins server app.",
                common.create_app,
                function_parameters=[self.jenkins_name, common.app_types['jenkins']],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Embed a jenkins client to scalable app.",
                common.embed,
                function_parameters=[self.app_name, 
                                     'add-%s'%common.cartridge_types['jenkins'],
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_return=0,
                expect_description="Embedding of jenkins should work.",
                try_count=2))

        self.steps.append(testcase.TestCaseStep("Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.getenv('OPENSHIFT_GEAR_DNS').'<br />';?> </body> </html>" >php/test.php'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Trigger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name,],
                expect_return=True,
                expect_description="Jenkins build should succeed",))


        self.steps.append(testcase.TestCaseStep("Verify recent changes.",
                self.verify,
                function_parameters = ['App DNS'],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Scale up.",
                common.scale_up,
                function_parameters=[self.app_name,],
                expect_return=0))


        self.steps.append(testcase.TestCaseStep("Verify recent changes.",
                self.verify,
                function_parameters = ['App DNS'],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Scale down.",
                common.scale_down,
                function_parameters=[self.app_name,],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Remove Jenkins client",
                common.embed,
                function_parameters=[self.app_name, "remove-"+common.cartridge_types['jenkins'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.getenv('OPENSHIFT_GEAR_DNS') . '<br />';?> second chance...</body> </html>" >php/test.php'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Trigger git push",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name,],
                expect_return=True,
                expect_description="Git push should succeed",))

        self.steps.append(testcase.TestCaseStep("Verify recent changes.",
                self.verify,
                function_parameters = ['second'],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Embed a jenkins client to scalable app.",
                common.embed,
                function_parameters = [self.app_name, "add-" + common.cartridge_types["jenkins"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.getenv('OPENSHIFT_GEAR_DNS').'<br />';?> third chance...</body> </html>" >php/test.php'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Trigger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name,],
                expect_return=True,
                expect_description="Jenkins build should succeed",))

        self.steps.append(testcase.TestCaseStep("Verify recent changes.",
                self.verify,
                function_parameters = ['third'],
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps)
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
    suite.add_test(EmbedJenkins2scalableApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of embed_jenkins2scalable_app.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
