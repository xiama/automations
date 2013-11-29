#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1178 & US1034] [rhc-cartridge] Negative testing for jenkins cartridge 
https://tcms.engineering.redhat.com/case/122372/
"""
import os,sys,re
import time

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `php` as default")
            self.test_variant= "php"

        self.app_name = self.test_variant.split('-')[0] + "negative"
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        self.output = dict()
        tcms_testcase_id=122372
 
        common.env_setup()

    def finalize(self):
        #OSConf.initial_conf()
        pass

class JenkinsNegativeTesting(OpenShiftTest):
    def test_method(self):
        case=testcase.TestCase("[US1178 & US1034] [rhc-cartridge] Negative testing for jenkins cartridge ", [])
        try:
            # 1.Create an app
            (retcode, self.output[1]) =testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                    common.create_app,
                    function_parameters=[self.app_name, 
                                         self.app_type, 
                                         self.config.OPENSHIFT_user_email, 
                                         self.config.OPENSHIFT_user_passwd],
                    expect_description = "the app should be created successfully",
                    expect_return=0).run()

            # 2.Try to embed jenkins client to the app without jekins server app created
            (retcode, self.output[2]) = testcase.TestCaseStep("2.Try to embed jenkins client to the app without jekins server app created",
                    common.embed,
                    function_parameters=[self.app_name, "add-jenkins-client-1", 
                                         self.config.OPENSHIFT_user_email, 
                                         self.config.OPENSHIFT_user_passwd],
                    expect_description="the jenkins client should not be embedded",
                    expect_return="!0",
                    expect_string_list=["Jenkins server does not exist",],).run()

            # 3.Access app's url to make sure it's still available
            app_url = "https://" + OSConf.get_app_url(self.app_name)
            (retcode, self.output[3]) =testcase.TestCaseStep("3.Access app's url to make sure it's still available",
                    common.grep_web_page,
                    function_parameters=[app_url, "Welcome to OpenShift", "-k -H 'Pragma: no-cache'", 3, 9],
                    expect_description="The app should be available",
                    expect_return=0).run()

            # 4.Create a jenkins server app
            (retcode, self.output[4]) = testcase.TestCaseStep("4. Create an jenkins app",
                    common.create_app,
                    function_parameters=["server", 
                                         "jenkins-1", 
                                         self.config.OPENSHIFT_user_email, 
                                         self.config.OPENSHIFT_user_passwd,
                                         False],
                    expect_description="the jenkins app should be created successfully",
                    expect_return=0).run()
            time.sleep(10)

            # 5.Embed jenkins client to the app
            (retcode, self.output[5]) = testcase.TestCaseStep("5.Embed jenkins client to the app",
                    common.embed,
                    function_parameters=[self.app_name, 
                                         "add-jenkins-client-1", 
                                         self.config.OPENSHIFT_user_email, 
                                         self.config.OPENSHIFT_user_passwd],
                    expect_description="the jenkins client should be embedded successfully",
                    expect_return=0,
                    try_count=3,
                    try_interval=5).run()

            # 6.Make some change in the git repo and git push
            test_html = "my test page"
            type_to_cmd = {     
                "php-5.3"    :  "echo '%s' > %s/php/index.php" % (test_html, self.git_repo),
                "jbossas-7"  :  "echo '%s' > %s/src/main/webapp/index.html" % (test_html, self.git_repo),
                "python-2.6" :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/wsgi/application" % (test_html, self.git_repo),
                "ruby-1.8"   :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/config.ru" % (test_html, self.git_repo),
                "perl-5.10"  :  "sed -i -e 's/Welcome to OpenShift/%s/g' %s/perl/index.pl" % (test_html, self.git_repo)
                        }
            cmd = type_to_cmd[self.app_type]
            (retcode, self.output[6]) = testcase.TestCaseStep("6.Make some changes in the git repo and git push",
                    cmd,
                    expect_description="the git repo is modified successfully and git push succeeds",
                    expect_return=0).run()
            # Trigger jenkins build
            (retcode, self.output[6]) = testcase.TestCaseStep("6.Trigger jenkins build",
                    common.trigger_jenkins_build,
                    function_parameters=[self.git_repo],
                    expect_description="the git repo is modified successfully and git push succeeds",
                    expect_return=True).run()

            # 7.Check if the changes take effect
            (retcode, self.output[7]) = testcase.TestCaseStep("7.Check if the changes take effect",
                        common.grep_web_page,
                        function_parameters=[app_url, test_html, "-k -H 'Pragma: no-cache'", 3, 9],
                        expect_description="'%s' should be found in the web page" % (test_html),
                        expect_return=0).run()

            # 8.remove the jenkins server app
            (retcode, self.output[8]) = testcase.TestCaseStep("8. Destroy the jenkins server app",
                    common.destroy_app,
                    function_parameters=["server", self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                    expect_description="the jenkins app should be destroyed successfully",
                    expect_return=0).run()

            # 9.Do some change to normal app's git repo and git push
            old_html = test_html
            test_html = "This is a test page"
            type_to_cmd = {     
                "php-5.3"       :   "echo '%s' > %s/php/index.php" % (test_html, self.git_repo),
                "jbossas-7"   :   "echo '%s' > %s/src/main/webapp/index.html" % (test_html, self.git_repo),
                "python-2.6"      :   "sed -i -e 's/%s/%s/g' %s/wsgi/application" % (old_html, test_html, self.git_repo),
                "ruby-1.8"      :   "sed -i -e 's/%s/%s/g' %s/config.ru" % (old_html, test_html, self.git_repo),
                "perl-5.10"     :   "sed -i -e 's/%s/%s/g' %s/perl/index.pl" % (old_html, test_html, self.git_repo) }
            cmd = type_to_cmd[self.app_type]
            (retcode, self.output[9]) = testcase.TestCaseStep("9.Make some changes in the git repo and git push again",
                    cmd,
                    expect_description="Git push should succeed",
                    expect_return=0).run()
            # Trigger jenkins build
            (retcode, self.output[9]) = testcase.TestCaseStep("Trigger jenkins build",
                    common.trigger_jenkins_build,
                    function_parameters=[self.git_repo],
                    expect_description="Git push should succeed",
                    expect_return=True).run()

            # 10.Check if the changes take effect
            (retcode, self.output[10]) = testcase.TestCaseStep("10.Check if the changes take effect",
                    common.grep_web_page,
                    function_parameters=[app_url, test_html, "-k -H 'Pragma: no-cache'", 3, 9],
                    expect_description="'%s' should be found in the web page" % (test_html),
                    expect_return=0).run()

            common.destroy_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
         

        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)
  
        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsNegativeTesting)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
