#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1277][rhc-cartridge]Custom DNS names
https://tcms.engineering.redhat.com/case/122390/
"""
import os,sys,re,time

import rhtest
#import database
import random
# user defined packages
import openshift
import testcase,common,OSConf

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US1277][rhc-cartridge]Custom DNS names"
        self.domain_name = common.get_domain_name()
        if len(self.domain_name)==0:
            raise Exception("Empty domain name")

        self.new_domain_name = common.getRandomString(10)
        self.app_name = "phpdns"
        self.app_type = common.app_types['php']
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        tcms_testcase_id = 122389, 122390, 122391
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        common.env_setup()

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s* "%(self.app_name))

class CustomDnsNames(OpenShiftTest):

    def get_app_ip(self):
        app_url = OSConf.get_app_url(self.app_name)
        (status, output) = common.command_getstatusoutput("ping -c 3 %s"%app_url)

        obj = re.search(r"(?<=\()(\d{1,3}.){3}\d{1,3}(?=\))", output)
        if obj:
            app_ip = obj.group(0)
            print "Got ip: %s" %(app_ip)
            return app_ip
        else:
            raise Exception("ERROR Unable to get IP address of app")


    def test_method(self):

        # Create an php app
        self.steps_list.append(testcase.TestCaseStep("Create an php app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # Get the ip address of the app
        self.steps_list.append(testcase.TestCaseStep("Get the ip address of the app",
                self.get_app_ip,
                expect_description="app's ip address should be got"))

        aliases = ["%s.bar.com" %(common.getRandomString(3)),"%s.bar.com" %(common.getRandomString(3))]

        for alias in aliases:
            # Add an alias to the app
            self.steps_list.append(testcase.TestCaseStep("Add an alias to the app",
                    "rhc alias add %s %s -l %s -p '%s' %s"
                        % (self.app_name, alias, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                    expect_description="alias: %s should be added" % (alias),
                    expect_return=0))

            # Try to add the same alias to the app
            self.steps_list.append(testcase.TestCaseStep("Add the same alias again to the app",
                        "rhc alias add %s %s -l %s -p '%s' %s"
                            % (self.app_name, alias, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description="alias: %s should be added" % (alias),
                        expect_return="!0"))

            # Make some changes in the git repo and git push 
            test_html = "Welcome to %s test page" % (alias)
            self.steps_list.append(testcase.TestCaseStep(
                    "Make some changes in the git repo and git push",
                    "cd %s && echo '%s' > php/index.php && git commit -am t && git push" % (self.git_repo, test_html),
                    expect_description="Successfully changed git repo and git push",
                    expect_return=0))

            # sleep to wait it takes effect
            self.steps_list.append(testcase.TestCaseStep("Waiting.. 5 seconds",
                    common.sleep,
                    function_parameters=[5]))

            # Access the app using custom DNS to see if changes have taken effect
            self.steps_list.append(testcase.TestCaseStep(
                                "Access the app using custom DNS to see if changes have taken effect",
                                "http_proxy='' curl -s -H 'Host: %s' -H 'Pragma: no-cache' __OUTPUT__[2] | grep '%s'" % (alias, test_html),
                                expect_description="'%s' should be found in the web page" % (test_html),
                                expect_return=0))

        # Remove one of the aliases
        self.steps_list.append(testcase.TestCaseStep("Remove one of the aliases",
                "rhc alias remove %s %s -l %s -p '%s' %s" % (self.app_name, aliases[0], self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="alias: %s should be removed" % (aliases[0]),
                expect_return=0))

        # Access the app using the custom DNS again to see it's unavailable
        self.steps_list.append( testcase.TestCaseStep("Access the app using the custom DNS again to see it's unavailable",
                                "http_proxy='' curl -s -H 'Host: %s' -H 'Pragma: no-cache' __OUTPUT__[2] | grep '%s'" % (aliases[0], test_html),
                                expect_description="The custom DNS: %s should be unavailable" % (aliases[0]),
                                expect_return="!0"))

        # Access the other alias to see it's available
        self.steps_list.append(testcase.TestCaseStep(
                "Access the other alias to see it's available",
                "http_proxy='' curl -s -H 'Host: %s' -H 'Pragma: no-cache' __OUTPUT__[2] | grep '%s'" % (aliases[1], test_html),
                expect_description="The custom DNS: %s should be available" % (aliases[1]),
                expect_return=0))

        # Remove the other alias
        self.steps_list.append(testcase.TestCaseStep("Remove the other alias",
                "rhc alias remove %s %s -l %s -p '%s' %s" % (self.app_name, aliases[1], self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="alias: %s should be removed" % (aliases[1]),
                expect_return=0))

        # Access the app using the custom DNS again to see it's unavailable
        self.steps_list.append(testcase.TestCaseStep("Access the app using the custom DNS again to see it's unavailable",
                "http_proxy='' curl -s -H 'Host: %s' -H 'Pragma: no-cache' __OUTPUT__[2] | grep '%s'" % (aliases[1], test_html),
                expect_description="The custom DNS: %s should be unavailable" % (aliases[1]),
                expect_return="!0"))

        # Access the app using the rhcloud.com url to see it's available
        self.steps_list.append(testcase.TestCaseStep(
                "Access the app using the rhcloud.com url to see it's available",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 5, 9],
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
    suite.add_test(CustomDnsNames)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
