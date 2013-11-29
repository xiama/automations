#!/usr/bin/env python

import os
import common
import rhtest


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.get_variant()
        except:
            print "OPENSHIFT_test_name environment variable is not set. Running test with default php"
            self.test_variant = 'php'
        self.app_type = common.app_types[self.test_variant]
        self.app_name = 'my%s%s' % (self.test_variant, common.getRandomString() )
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%self.app_name)


class RhcApp(OpenShiftTest):
    def test_method(self):
        self.info("[US1317][UI][CLI]rhc wrapper - rhc app")

        self.add_step("Help",
            "rhc app --help",
            expect_description = "Command line option --help should provide the appropriate help message",
            expect_str = [
                "List of Actions", "\s+create",
                "\s+git-clone", "\s+delete", "\s+start", "\s+stop", "\s+restart", "\s+reload", "\s+status",
                "\s+force-stop", "\s+tidy", 
                "Global Options", "-l|--rhlogin", "-p|--password", 
                "--noprompt", "-d|--debug", "-h|--help", "--config", "--timeout", 
            ])
    # Covering the full application life cycle
        for action in  [ "create", "start", "stop", "force-stop", "restart", "reload", "show", "tidy", "delete"]:
            # Special parameters for some of the commands
            extra_options = ""
            if action == "add-alias" or action == "remove-alias":
                extra_options = "--alias www.example.com"
            elif action == "create":
                extra_options = "-t %s" % ( self.app_type )
            elif action == "delete":
                extra_options = "--confirm"
            elif action.startswith("snapshot"):
                extra_options = "--filepath=/tmp/%s.tar.gz" % ( self.app_name )
            
            # Actions are tested with failure and success
            for result in [ "success", "failure"]:
                extra_options_suffix = ""
                app_name_suffix = ""
                if result == "success":
                    return_value_expected = 0
                elif result == "failure":
                    return_value_expected = "!0"
                    if action == "create":
                        extra_options_suffix = common.getRandomString()
                    else:
                        app_name_suffix = common.getRandomString()
                self.add_step("Action '%s' - %s" % ( action, result.upper() ),
                    "rhc app %s -a %s%s -l %s -p %s %s%s %s" % ( action, self.app_name, app_name_suffix, self.user_email, self.user_passwd, extra_options, extra_options_suffix, common.RHTEST_RHC_CLIENT_OPTIONS),
                    expect_description = "The action is performed with %s" % ( result ),
                    expect_return = return_value_expected)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
