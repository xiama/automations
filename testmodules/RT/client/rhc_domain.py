#!/usr/bin/env python

import common
import rhtest


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1317][UI][CLI]rhc wrapper - rhc domain")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.domain_name = common.get_domain_name()

        common.env_setup()


    def finalize(self):
        #if we are interrupted in the middle of destroying domain...
        common.fix_domain(common.getRandomString(10), self.user_email, self.user_passwd)


class RhcDomain(OpenShiftTest):
    def test_method(self):
        self.add_step(
            "Help",
            "rhc help domain",
            expect_description = "Command line should provide the appropriate help message",
            expect_str = [
                "Usage: rhc domain",
                "List of Actions", "\s+create", "\s+show", "\s+update", "\s+status", "\s+delete",
                "Global Options", " -l|--rhlogin", "-p|--password", "-d|--debug", "-h|--help",
                " --config" ])

        # Covering the full domain namespace life cycle
        for action in  [ "show", "update", "delete", "create" ]:
            extra_parameters = ""
            dependency = ""
            # Configuring command line parameters for each action
            if action == "delete":
                extra_parameters = "-n new" + self.domain_name
            if action == "update":
                extra_parameters = "%s new%s" % (self.domain_name, self.domain_name)

            if action == "create":
                extra_parameters = "-n " + self.domain_name
            if action == "status":
                dependency = "eval $(ssh-agent) ; ssh-add ~/.ssh/id_rsa && "
            # Actions are tested with failure and success
            for result in [ "success", "failure"]:
                if result == "success":
                    # Return code must be 0 on success
                    return_value_expected = 0
                elif result == "failure":
                    if action == "show" or action == "status":
                        # Skipping failure testing for actions 'show' and 'status'
                        continue
                    if action == "create" or action == "alter":
                        extra_parameters = extra_parameters + common.getRandomString(20)
                    if action == "show":
                        extra_parameters = extra_parameters + "-n " + self.domain_name
                    return_value_expected = "!0"
                self.add_step(
                    "Action '%s' - %s" % ( action, result.upper() ),
                    "%s rhc domain %s -l %s -p %s %s %s" % ( dependency, action, self.user_email, self.user_passwd, extra_parameters, common.RHTEST_RHC_CLIENT_OPTIONS),
                    expect_description = "The action is performed with %s" % ( result ),
                    expect_return = return_value_expected)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcDomain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
