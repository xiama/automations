#!/usr/bin/env python

import os
import testcase, common, OSConf
import rhtest


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            print "variant is not set. Running test with default `php`"
            self.test_variant = 'jbossews'
        self.info("VARIANT: %s"%self.test_variant)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.git_repo = self.app_name
        if self.test_variant == "jenkins":
            self.good_str = "<script>window.location.replace"
            self.bad_str = "Service Temporarily Unavailable"
        elif self.test_variant == "diy":
            self.good_str = ""
            self.bad_str = ""
        else:
            self.good_str = "Welcome to"
            self.bad_str = "Service Temporarily Unavailable"
        tcms_testcase_id=146360,122407, 122371, 122315
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%self.app_name)


class CreateControlApp(OpenShiftTest):
    def test_method(self):
        step = testcase.TestCaseStep("Create a %s application" %(self.app_type),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                expect_return=0,
                expect_description="App should be created successfully")
        self.steps_list.append(step)

        def verify(exp_str):
            if self.test_variant == "jenkins":
                proto = "https"
            else:
                proto = "http"
            url=OSConf.get_app_url(self.app_name)
            return common.grep_web_page("%s://%s"%(proto,url), exp_str, options="-k -H 'Pragma: no-cache' -L ", count=4, delay=7)

        step = testcase.TestCaseStep("Check this app is available",
                verify,
                function_parameters=[self.good_str],
                expect_return=0)
        self.steps_list.append(step)

        test_html = "Welcome to OpenShift~_~"
        type_to_cmd = {
            "php-5.3"       :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/php/index.php" % (test_html, self.git_repo),
            "jbossas-7"     :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/src/main/webapp/index.html" % (test_html, self.git_repo),
            "jbosseap-6"  :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/src/main/webapp/index.html" % (test_html, self.git_repo),
            "jbossews-1.0"  :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/src/main/webapp/index.html" % (test_html, self.git_repo),
            "jbossews-2.0"  :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/src/main/webapp/index.html" % (test_html, self.git_repo),
            "nodejs-0.6"    :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/index.html" % (test_html, self.git_repo),
            "python-2.6"    :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/wsgi/application" % (test_html, self.git_repo),
            "ruby-1.8"      :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/config.ru" % (test_html, self.git_repo),
            "perl-5.10"     :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/perl/index.pl" % (test_html, self.git_repo),
            "diy-0.1"       :  "echo %s >%s/testfile" % (test_html, self.git_repo),
            "zend-5.6"      :  "echo %s >%s/testfile" % (test_html, self.git_repo),
            "jenkins-1"   :  "echo %s >%s/testfile" % (test_html, self.git_repo),
            "python-2.7"    :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/wsgi/application" % (test_html, self.git_repo),
            "python-3.3"    :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/wsgi/application" % (test_html, self.git_repo)
                      }
        type_to_cmd["ruby-1.9"] = type_to_cmd["ruby-1.8"]
        cmd = type_to_cmd[self.app_type] + " && cd %s && git add . && git commit -am t && git push" % (self.git_repo)
        step = testcase.TestCaseStep("Make some changes in the git repo and git push",
                    cmd,
                    expect_description="the git repo is modified successfully and git push succeeds",
                    expect_return=0)
        self.steps_list.append(step)


        step = testcase.TestCaseStep("Check your change take effect",
                verify,
                function_parameters=[test_html],
                expect_return=0)
        if self.test_variant in ("diy", "jenkins", "zend"):
            pass
        else:
            self.steps_list.append(step)


        step = testcase.TestCaseStep("Stop this app",
                "rhc app stop %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be stopped successfully",
                expect_return=0,
                expect_string_list=["%s stopped" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Stop this app again",
                "rhc app stop %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be stopped successfully",
                expect_return=0,
                expect_string_list=["%s stopped" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is NOT available",
                                  verify,
                                  function_parameters=[self.bad_str],
                                  expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Start this app",
                "rhc app start %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be started successfully",
                expect_return=0,
                expect_string_list=["%s started" % (self.app_name)],
                try_count=3)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is available",
                verify,
                function_parameters=[self.good_str],
                expect_return=0,
                try_count=10,
                try_interval=12)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Restart this app",
                "rhc app restart %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be restarted successfully",
                expect_return=0,
                expect_string_list=["%s restarted" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is available",
                verify,
                function_parameters=[self.good_str],
                expect_return=0,
                try_count=10,
                try_interval=12)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Force stop this app",
                "rhc app force-stop %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be force stopped successfully",
                expect_return=0,
                expect_string_list=["%s force stopped" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is NOT available",
                verify,
                function_parameters=[self.bad_str],
                expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Restart this app",
                "rhc app restart %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be restarted successfully",
                expect_return=0,
                expect_string_list=["%s restarted" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is available",
                verify,
                expect_return=0,
                function_parameters=[self.good_str],
                try_count=10,
                try_interval=12)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Reload this app",
                "rhc app reload %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The app should be reloaded successfully",
                expect_return=0,
                expect_string_list=["%s config reloaded" % (self.app_name)])
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app is available",
                verify,
                function_parameters=[self.good_str],
                expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Check this app's status",
                "rhc app show --state %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Delete this app",
                common.destroy_app,
                function_parameters=[self.app_name, self.user_email, self.user_passwd],
                expect_description="The app should be deleted successfully",
                expect_return=0)
        self.steps_list.append(step)

        step = testcase.TestCaseStep("Try to start this non-existing app",
                "rhc app start %s -l %s -p '%s' %s" % (self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return="!0")
        self.steps_list.append(step)

        case = testcase.TestCase("Control %s application - start/restart/reload/stop/destroy/force-stop" %(self.app_type), self.steps_list)

        try:
            case.run()
        except testcase.TestCaseStepFail as e:
            return self.failed(str(e))

        if case.testcase_status == 'PASSED':
            return self.passed()
        if case.testcase_status == 'FAILED':
            return self.failed()


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateControlApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

