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
        self.app_type = 'php'
        tcms_testcase_id = 145122
        self.steps=[]

        common.env_setup()

    def finalize(self):
        #os.system("rm -rf server; rhc-ctl-app -a %s -c destroy -b -l %s -p %s; rhc-ctl-app -a server -c destroy -b -l %s -p %s;"%(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd))
        pass

class EmbedJenkins2scalableApp(OpenShiftTest):
    def test_method(self):

        def verify(app_name, what):
            url = OSConf.get_app_url(app_name) 
            (status, output) = common.grep_web_page(url, what)
            return status

        self.steps.append(testcase.TestCaseStep("1. Create an scalable app using REST API",
                common.create_scalable_app,
                function_parameters=[self.app_name, 
                                    common.app_types[self.app_type], 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("2. Scale up.",
                common.scale_up,
                function_parameters=[self.app_name, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("3. Create a jenkins server app.",
                common.create_app,
                function_parameters=['server', common.app_types['jenkins'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("4. Embed a jenkins client to scalable app.",
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types["jenkins"]],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("5. Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.$_ENV['OPENSHIFT_GEAR_DNS'] . '<br />';?> </body> </html>" >php/index.php && git commit -m "x" -a && git push'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("6. Scale up.",
                common.scale_up,
                function_parameters=[self.app_name, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("7. Scale down.",
                common.scale_down,
                function_parameters = [self.app_name,
                                       self.config.OPENSHIFT_user_email, 
                                       self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("8. Remove Jenkins client",
                common.embed,
                function_parameters = [self.app_name, "remove-" + common.cartridge_types["jenkins"]],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("9. Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.$_ENV['OPENSHIFT_GEAR_DNS'] . '<br />';?> second chance...</body> </html>" >php/index.php && git commit -m "x" -a && git push'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("10. Embed a jenkins client to scalable app.",
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types["jenkins"]],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("11. Make some changes to the app.",
                '''cd %s && echo "<html><body><?php echo 'App DNS: '.$_ENV['OPENSHIFT_GEAR_DNS'] . '<br />';?> third chance...</body> </html>" >php/index.php && git commit -m "x" -a && git push'''%self.app_name,
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("12. Make some changes to the app.",
                verify,
                function_parameters = [self.app_name, 'third'],
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps)
        case.run()

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
