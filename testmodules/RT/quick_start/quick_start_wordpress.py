#!/usr/bin/env python
import os, sys, re, time

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf
import rhtest
from quick_start_test import QuickStartTest

# Global variables
CODE = """
$_secure_tokens = array(
  'AUTH_KEY',
  'SECURE_AUTH_KEY',
  'LOGGED_IN_KEY',
  'NONCE_KEY',
  'AUTH_SALT',
  'SECURE_AUTH_SALT',
  'LOGGED_IN_SALT',
  'NONCE_SALT'
);

print "<table>";
foreach ($_secure_tokens as $key) {
  printf ("<tr><td>%s</td><td>%s</td></tr>",$key,eval("return $key;"));
}
print "</table>";
"""

DEFAULT_AUTH = {    "AUTH_KEY"  :   'w*lE&r=t-;!|rhdx5}vlF+b=+D>a)R:nTY1Kdrw[~1,xDQS]L&PA%uyZ2:w6#ec',
                    "SECURE_AUTH_KEY"   :   '}Sd%ePgS5R[KwDxdBt56(DM:0m1^4)-k6_p8}|C:[-ei:&qA)j!X`:7d-krLZM*5',
                    "LOGGED_IN_KEY" :   '$l^J?o)!zhp6s[-x^ckF}|BjU4d+(g1as)n/Q^s+k|,ZZc@E^h%Rx@VTm|0|?]6R',
                    "NONCE_KEY" :   '#f^JM8d^!sVsq]~|4flCZHdaTy.-I.f+1tc[!h?%-+]U}|_8qc K=k;]mXePl-4v',
                    "AUTH_SALT" :   'I_wL2t!|mSw_z_ zyIY:q6{IHw:R1yTPAO^%!5,*bF5^VX`5aO4]D=mtu~6]d}K?',
                    "SECURE_AUTH_SALT"  :   '&%j?6!d<3IR%L[@iz=^OH!oHRXs4W|D,VCD7w%TC.uUa`NpOH_XXpGtL$A]{+pv9',
                    "LOGGED_IN_SALT"    :   'N<mft[~OZp0&Sn#t(IK2px0{KloRcjvIJ1+]:,Ye]>tb*_aM8P&2-bU~_Z>L/n(k',
                    "NONCE_SALT"    :   'u E-DQw%[k7l8SX=fsAVT@|_U/~_CUZesq{v(=y2}#X&lTRL{uOVzw6b!]`frTQ|',
}

class OpenShiftTest(rhtest.Test):
    ITEST = ['DEV', 'STG', 'INT']

    def initialize(self):
        self.steps_list = []
        self.summary = "[Runtime][rhc-cartridge]quick-start example: Wordpress"
        self.app_name = "wordpress"
        self.new_app_name = "wordpress2"
        self.app_type = common.app_types["php"]
        self.git_repo = self.app_name
        self.git_upstream_url = "git://github.com/openshift/wordpress-example.git"
        common.env_setup()

    def finalize(self):
        pass


class QuickStartWordpress(OpenShiftTest):

    def get_auth(self, app_name):
        app_url = OSConf.get_app_url(app_name)
        for i in range(4):
            (ret, output) = common.command_getstatusoutput("curl -H 'Pragma: no-cache' '%s'" % (app_url), True)
            if ret == 0:
                break
            time.sleep(5)
        lst = re.findall(r"(?<=<td>).*?(?=</td>)", output, re.S)
        tokens = dict()
        for i in range(0, len(lst), 2):
            tokens[lst[i]] = lst[i+1]
        return tokens

    def modify_app(self, app_name):
        global CODE
        time.sleep(10)
        cmds = [
            "cd %s" % (app_name),
            "git remote add upstream -m master %s" % (self.git_upstream_url),
            "git pull -s recursive -X theirs upstream master",
        ]
        (ret, output) = common.command_getstatusoutput(" && ".join(cmds))
        if ret != 0:
            return ret
        try:
            f = file("%s/php/index.php" % (app_name), "a")
            f.write(CODE)
            f.close()
        except IOError:
            self.info("Failed to edit %s/php/index.php" % (app_name))
        cmds = [
            "cd %s" % (app_name),
            "git add .",
            "git commit -amt",
            "git push",
        ]
        (ret, output) = common.command_getstatusoutput(" && ".join(cmds))
        return ret

    def verify1(self, app_name):
        global DEFAULT_AUTH
        self.tokens = self.get_auth(app_name)
        (ret, output) = common.command_getstatusoutput("rhc app restart -a %s -l %s -p '%s' -d %s" % (app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS), True)
        self.tokens_restart = self.get_auth(app_name)
        for key in self.tokens.keys():
            if self.tokens[key] == DEFAULT_AUTH[key]:
                return self.failed("%s failed: The auth info is the same as default - %s" % (self.__class__.__name__, key))
        for key in self.tokens.keys():
            if self.tokens[key] != self.tokens_restart[key]:
                return self.failed("%s failed: The auth info becomes different after restarting - %s" % (self.__class__.__name__, key))
        return 0

    def verify2(self, app_name):
        self.tokens2 = self.get_auth(app_name)
        for key in self.tokens.keys():
            if self.tokens[key] == self.tokens2[key]:
                return self.failed("%s failed: The auth info is the same as the previous app - %s" % (self.__class__.__name__, key))
        return 0

    def test_method(self):
        global DEFAULT_AUTH

        # 1. Create app
        self.steps_list.append(testcase.TestCaseStep("Create an %s app: %s" % (self.app_type, self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 2. Embed mysql to the app
        self.steps_list.append(testcase.TestCaseStep("Embed mysql-5.1 to it",
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="mysql should be embedded successfully",
                expect_return=0))
        # 3. Modify the app git repo
        self.steps_list.append(testcase.TestCaseStep("Modify the app git repo",
                self.modify_app,
                function_parameters=[self.app_name,],
                expect_description="git push should succeed",
                expect_return=0))
        # 4. Verify the auth info is different from the default one and restart won't change the auth info
        self.steps_list.append(testcase.TestCaseStep("Modify the app git repo",
                self.verify1,
                function_parameters=[self.app_name,],
                expect_description="git push should succeed",
                expect_return=0))
        # 5. Create a new wordpress app
        self.steps_list.append(testcase.TestCaseStep("Create another %s app: %s" % (self.app_type, self.new_app_name),
                common.create_app,
                function_parameters=[self.new_app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 6. Embed mysql to the app
        self.steps_list.append(testcase.TestCaseStep("Embed mysql-5.1 to the new app",
                common.embed,
                function_parameters=[self.new_app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="mysql should be embedded successfully",
                expect_return=0))
        # 7. Modify the new app git repo
        self.steps_list.append(testcase.TestCaseStep("Modify the new app git repo",
                self.modify_app,
                function_parameters=[self.new_app_name,],
                expect_description="git push should succeed",
                expect_return=0))
        # 8. Verify the auth info is different from the previous app
        self.steps_list.append(testcase.TestCaseStep("Verify the auth info is different from the previous app",
                self.verify2,
                function_parameters=[self.new_app_name,],
                expect_description="git push should succeed",
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
    suite.add_test(QuickStartWordpress)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
