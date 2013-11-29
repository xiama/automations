"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]JBoss cartridge: three sample applications test
https://tcms.engineering.redhat.com/case/122280/
"""
import os,sys,re,time

import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge]JBoss cartridge: three sample applications test" 
        # test_name should be among tweetstream,kitchensink
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, using `tweetstream` from [kitchensinkHtml5, tweetstream,kitchensink]")
            self.test_variant = 'tweetstream'

        self.app_name = self.test_variant
        self.app_type = common.app_types["jbossas"]
        self.git_repo = "./%s" % (self.app_name)

        common.env_setup()

        self.steps_list = []

    def finalize(self):
        pass

class JbossSampleApplications(OpenShiftTest):

    def test_method(self):
        # 1.Create an app
        self.steps_list.append( testcase.TestCaseStep(
                "1. Create an jbossas app for %s test" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
    
        # 2.Git remote add and pull
        testname_to_giturl = {  
            "kitchensinkHtml5" : "git://github.com/openshift/kitchensink-html5-mobile-example.git",
            "tweetstream" : "git://github.com/openshift/tweetstream-example.git",
            "kitchensink" : "git://github.com/openshift/kitchensink-example.git"}

        git_url = testname_to_giturl[self.test_variant]
        self.steps_list.append( testcase.TestCaseStep("2.Git remote add and pull",
                "cd %s && git remote add upstream -m master %s && git pull -s recursive -X theirs upstream master" % (self.git_repo, git_url),
                expect_description="the app should be created successfully",
                expect_return=0))

        # 3.Make some changes to the git repo
        if self.test_variant == "kitchensinkHtml5":
            cmd = "touch %s/testemptyfile" % (self.git_repo)
        elif self.test_variant == "tweetstream":
            cmd = "cd %s/tweetstream/src/main/resources/ && sed -i -e 's/consumerKey=/consumerKey=HdPuX8kwhFQtcHesyMlDcQ/' twitter4j.properties && sed -i -e 's/consumerSecret=/consumerSecret=XsMdF9qYCPlQOMxwoAgBJtEumW2DSGtBkABfxj21I/' twitter4j.properties && sed -i -e 's/accessToken=/accessToken=356040597-o6ev08uMGXFuGBlNahwxYwE9IaOBJnoaneUbP7Y/' twitter4j.properties && sed -i -e 's/accessTokenSecret=/accessTokenSecret=x9c1KUQUUp4JZ7cV5X91jfPEqRhFOHhyLGOtIzSFq5A/' twitter4j.properties" % (self.git_repo)
        elif self.test_variant == "kitchensink":
            cmd = "cd %s && echo \"HelloKitchensink\">>testfile.txt" % (self.git_repo)
        else:
            raise Exception("Invalid self.test_variant")

        self.steps_list.append( testcase.TestCaseStep("3.Make some changes to the git repo",
                cmd,
                expect_description="Made changes successfully",
                expect_return=0))

        # 4.Git push all the changes
        self.steps_list.append( testcase.TestCaseStep("2.Git push all the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="the app should be created successfully",
                expect_return=0))

        # 5.Check the app via browser
        def get_app_url(app_name, suffix):
            def get_app_url2():

                return OSConf.get_app_url(app_name)+suffix
            return get_app_url2

        suffix = ""
        if self.test_variant == "kitchensinkHtml5":
            test_html = "HTML5 form element & validation"
        elif self.test_variant == "tweetstream":
            test_html = "Top Tweeters"
            suffix = "/pages/home.jsf"
        elif self.test_variant == "kitchensink":
            test_html = "member"
            suffix += "/rest/members"
        self.steps_list.append( testcase.TestCaseStep("5.Check the app via browser",
                    common.grep_web_page,
                    function_parameters=[get_app_url(self.app_name, suffix), test_html, "-H 'Pragma: no-cache'", 5, 9],
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
    suite.add_test(JbossSampleApplications)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
