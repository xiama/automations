#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge]Rack / Rails Framework Support
https://tcms.engineering.redhat.com/case/122285/
"""
import os,sys,re,time,stat
import testcase,common,OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge]Rack / Rails Framework Support"
        self.app_name = "rackframework"
        self.app_type = common.app_types["rack"]
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        tcms_testcase_id=122285
        self.deploy_rails_file = "%s/deploy_rails_app.sh" % (self.git_repo)
        common.env_setup()

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class RackFrameworkSupport(OpenShiftTest):    

    def create_script(self):
        context = """#!/bin/sh
set -x 
rails new %s -f
cd %s 
echo "gem 'execjs'" >>Gemfile
echo "gem 'therubyracer'" >>Gemfile
bundle install
rails generate controller home index
echo '<h1>Hello, Rails</h1>' >> app/views/home/index.html.erb
rm -rf public/index.html
sed -i '5 iroot :to => "home#index"' config/routes.rb
sed -i -E 's/config.assets.compile = false/config.assets.compile = true/g' config/environments/production.rb
bundle install --deployment
git add . && git add -f .bundle && git commit -m "test" && git push""" %(self.git_repo, self.git_repo)
        try:
            f = open(self.deploy_rails_file, 'w')
            f.write(context)
            f.close()
            os.chmod(self.deploy_rails_file, 0777)
        except Exception as e:
            self.info("Failed to create deploy_rails_app.sh under local git repo: %s"%str(e))
            return 1

        self.info("Successfully created deploy_rails_app.sh under local git repo")
        return 0


    def test_method(self):
        # 1.Create an app
        self.steps_list.append(testcase.TestCaseStep("1. Create an rack app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        
        # 2.Create deploy_rails_app.sh under local git repo
        self.steps_list.append(testcase.TestCaseStep("2.Create deploy_rails_app.sh under local git repo",
                self.create_script,
                expect_description="Successfully created deploy_rails_app.sh under local git repo",
                expect_return=0))

        # 3.Run deploy_rails_app.sh
        self.steps_list.append(testcase.TestCaseStep("3.Run deploy_rails_app.sh",
                "bash %s" % (self.deploy_rails_file),
                expect_description="Script executed successfully",
                expect_return=0))

        # 4.Check app via browser
        test_html = "Hello, Rails"
        self.steps_list.append(testcase.TestCaseStep("4.Check the app via browser",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 3, 9],
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
    suite.add_test(RackFrameworkSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
