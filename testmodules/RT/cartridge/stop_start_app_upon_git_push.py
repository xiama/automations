
import os,sys,re,time,subprocess

import proc
import OSConf
import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "Stop Start appliaction upon git push"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `php` as default")
            self.test_variant = 'php'

        self.app_name = self.test_variant.split('-')[0] + "stopstart"
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        self.app_type = common.app_types[self.test_variant]

        self.steps_list = []

        common.env_setup()
        common.clean_up(self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)

    def finalize(self):
        pass

class StopStartAppUponGitPush(OpenShiftTest):

    def test_method(self):
        # 1. Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 2.Custom git hook
        hook_file_path = "%s/.openshift/action_hooks/build" % (self.git_repo)
        key_string = "sleep 30"
        testcode = """
echo "%s"
%s
""" %(key_string, key_string)
        cmd = "echo '%s' >> %s && chmod +x %s" % (testcode, hook_file_path, hook_file_path)
        self.steps_list.append(testcase.TestCaseStep("2.Custom git hook",
                cmd,
                expect_description=".openshift/action_hooks/build modified successfully",
                expect_return=0))

        def create_proc(self, cmd):
            self.proc = proc.Proc(cmd)


        # 3.Git push in a subprocess
        self.steps_list.append(testcase.TestCaseStep("3.Git push in a subprocess(No Check)",
                create_proc,
                function_parameters=[self, "cd %s && git add . && git commit -am t && git push" % (self.git_repo),],
                expect_description="Git push should be started"))

        # 4.Waiting for stop to finish
        def grep_output(self, t, x, y):
            return self.proc.grep_output(t, x, y)

        self.steps_list.append(testcase.TestCaseStep("4.Waiting for stop to finish",
                grep_output,
                function_parameters=[self, r"Waiting for stop to finish", 2 ,20],
                expect_description="app stop should succeed",
                expect_return=0))

        # 5.Check if the key_string exists in the output
        self.steps_list.append(testcase.TestCaseStep("5.Check if the '%s' exists in the output" % (key_string),
                grep_output,
                function_parameters=[self, key_string, 2, 20],
                expect_description="'%s' should be found in the output" % (key_string),
                expect_return=0))

        # 6.Check app is unavailable before git push finish
        test_html = "Service Temporarily Unavailable"
        self.steps_list.append(testcase.TestCaseStep("6.Check app is unavailable before git push finish",
                    common.grep_web_page,
                    function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 2, 9],
                    expect_description="'%s' should be found in the web page" % (test_html),
                    expect_return=0))

        # 7.Wait for git push to finish
        def wait(self, x, y):
            return self.proc.wait(x,y)

        self.steps_list.append(testcase.TestCaseStep("7.Wait for git push to finish",
                    wait,
                    function_parameters=[self, 5, 10],
                    expect_description="git push should finish within given time and return 0",
                    expect_return=0))

        # 8.Check app is available after git push
        test_html = "Welcome to OpenShift"
        self.steps_list.append(testcase.TestCaseStep("8.Check app is available after git push",
                    common.grep_web_page,
                    function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 5, 8],
                    expect_description="'%s' should be found in the web page" % (test_html),
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
    suite.add_test(StopStartAppUponGitPush)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
