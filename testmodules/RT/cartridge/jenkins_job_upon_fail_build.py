#!/usr/bin/python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1178 & US1034] [rhc-cartridge] check jenkins functionality upon failed build
https://tcms.engineering.redhat.com/case/122368/
"""
import os, sys
import rhtest
import testcase, common, OSConf


class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary ="[US1178 & US1034] [rhc-cartridge] check jenkins functionality upon failed build"
        try:
            test_name = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `php`")
            test_name='zend'

        testname_to_file = {    "php"       :   "php/index.php",
                                "rack"      :   "config.ru",
                                "wsgi"      :   "wsgi/application",
                                "python"    :   "wsgi/application",
                                "perl"      :   "perl/index.pl",
                                "jbossas"   :   "src/main/webapp/index.html"}
        testname_to_file["zend"] = testname_to_file["php"]
        testname_to_file["ruby-1.9"] = testname_to_file["rack"]

        self.app_type = common.app_types[test_name]
        self.target_file = testname_to_file[test_name]
        self.app_name = test_name + "jenkinsfail"
        self.jenkins_name = "jenkins"

        common.env_setup()
        self.steps_list =  []

    def finalize(self):
        pass

class JenkinsJobUponFailBuild(OpenShiftTest):
    def test_method(self):
        # 1.
        self.steps_list.append(testcase.TestCaseStep("Create a jenkins app",
                common.create_app,
                function_parameters=[self.jenkins_name, 
                                     "jenkins-1", 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd, 
                                     False],
                expect_description="Jenkins app created success",
                expect_return=0,
                expect_string_list=['Jenkins created successfully']))
        
        # 2.
        self.steps_list.append(testcase.TestCaseStep("Create an application of %s type" %(self.app_type),
                common.create_app,
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="app created success",
                expect_return=0))

        # 3.
        self.steps_list.append(testcase.TestCaseStep("Embed jenkins client to app",
                common.embed,
                function_parameters=[self.app_name, 'add-jenkins-client-1', self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_string_list=['Jenkins client 1.4 has been added to %s' %(self.app_name)],
                expect_description="Embed jenkins to app success",
                expect_return=0,
                try_count=3,
                try_interval=5))
        # 4.
        self.steps_list.append(testcase.TestCaseStep("Got jenkins app url",
                 OSConf.get_app_url,
                 function_parameters=[self.jenkins_name]))

        # 5.
        self.steps_list.append(testcase.TestCaseStep("Got app url",
                OSConf.get_app_url,
                function_parameters=[self.app_name]))

        # 6.
        self.steps_list.append(testcase.TestCaseStep("Do some change to app's index page",
                "sed -i 's/Welcome to OpenShift/Welcome~~~/g' %s/%s " %(self.app_name, self.target_file),
                expect_return=0,))

        # 7.
        self.steps_list.append(testcase.TestCaseStep("Modify .openshift/action_hooks/pre-build",
                                  """echo -e '#! /bin/bash\necho "----Pre_Build Fail Test----"\nexit 1' >%s/.openshift/action_hooks/pre_build; \n chmod +x %s/.openshift/action_hooks/pre_build""" %(self.app_name, self.app_name),
                                  expect_return=0))
        # 8.
        self.steps_list.append(testcase.TestCaseStep("Triger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name, 1],
                expect_return=False))

        # 9.
        self.steps_list.append(testcase.TestCaseStep("Get jenkins username and password",
                self.get_jenkins_username_password,
                function_parameters=[OSConf.default, self.jenkins_name]))
        # 10.
        self.steps_list.append(testcase.TestCaseStep("Check output console of jenkins job",
                "curl -s -k -u __OUTPUT__[9][0]:__OUTPUT__[9][1] -H 'Pragma: no-cache' https://__OUTPUT__[4]/job/%s-build/1/console" %(self.app_name),
                expect_return=0,
                expect_string_list=['----Pre_Build Fail Test----'],
                try_count=4,
                try_interval=10))
        # 11.
        self.steps_list.append(testcase.TestCaseStep("Check output of app",
                "curl -s -H 'Pragma: no-cache' __OUTPUT__[5]",
                expect_return=0,
                expect_string_list=['Welcome to OpenShift'],
                unexpect_string_list=['Welcome~~~'],
                try_count=4,
                try_interval=10))

        # 12.
        self.steps_list.append(testcase.TestCaseStep("Restore .openshift/action_hooks/pre_build",
                "rm %s/.openshift/action_hooks/pre_build" %(self.app_name),
                expect_return=0))

        # 13.
        self.steps_list.append(testcase.TestCaseStep("Modify .openshift/action_hooks/build",
                """echo -e '#/bin/bash\necho "----Build Fail Test----"\nexit 1' >%s/.openshift/action_hooks/build; \n chmod +x %s/.openshift/action_hooks/build""" %(self.app_name, self.app_name),
                expect_return=0))

        # 14.
        self.steps_list.append(testcase.TestCaseStep("Triger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name, 1],
                expect_return=False))

        # 15.
        self.steps_list.append(testcase.TestCaseStep("Check output console of jenkins job",
                "curl -s -k -u __OUTPUT__[9][0]:__OUTPUT__[9][1] -H 'Pragma: no-cache' https://__OUTPUT__[4]/job/%s-build/2/console" %(self.app_name),
                expect_return=0,
                expect_string_list=['----Build Fail Test----'],
                try_count=4,
                try_interval=10))

        # 16.
        self.steps_list.append(testcase.TestCaseStep("Check output of app",
                "curl -s -H 'Pragma: no-cache' __OUTPUT__[5]",
                expect_return=0,
                expect_string_list=['Welcome to OpenShift'],
                unexpect_string_list=['Welcome~~~'],
                try_count=4,
                try_interval=10))

        # 17.
        self.steps_list.append(testcase.TestCaseStep("Restore .openshift/action_hooks/build",
                "rm %s/.openshift/action_hooks/build" %(self.app_name),
                expect_return=0))

        # 18.
        self.steps_list.append(testcase.TestCaseStep("Modify .openshift/action_hooks/deploy",
                """echo -e '#!/bin/bash\necho "----Deploy Fail Test----"\nexit 1' >%s/.openshift/action_hooks/deploy; \n chmod +x %s/.openshift/action_hooks/deploy""" %(self.app_name, self.app_name),
                expect_return=0,))

        # 19.
        self.steps_list.append(testcase.TestCaseStep("Triger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name, 1],
                expect_return=False))

        # 20.
        self.steps_list.append(testcase.TestCaseStep("Check output console of jenkins job",
                "curl -s -k -u __OUTPUT__[9][0]:__OUTPUT__[9][1] -H 'Pragma: no-cache' https://__OUTPUT__[4]/job/%s-build/3/console" %(self.app_name),
                expect_return=0,
                expect_string_list=['----Deploy Fail Test----'],
                try_count=4,
                try_interval=10))

        # 21.
        self.steps_list.append(testcase.TestCaseStep("Check output of app",
                "curl -s -H 'Pragma: no-cache' __OUTPUT__[5]",
                expect_return=0,
                expect_string_list=['503 Service Temporarily Unavailable'],
                unexpect_string_list=['Welcome~~~', 'Welcome to OpenShift'],
                try_count=4,
                try_interval=10))
        # 22.
        self.steps_list.append(testcase.TestCaseStep("Restore .openshift/action_hooks/deploy",
                "rm %s/.openshift/action_hooks/deploy" %(self.app_name),
                expect_return=0))

        # 23.
        self.steps_list.append(testcase.TestCaseStep("Modify .openshift/action_hooks/post_deploy",
                """echo -e '#!/bin/bash\necho "----Post_Deploy Fail Test----"\nexit 1' >%s/.openshift/action_hooks/post_deploy; \n chmod +x %s/.openshift/action_hooks/post_deploy""" %(self.app_name, self.app_name),
                expect_return=0))

        # 24.
        self.steps_list.append(testcase.TestCaseStep("Triger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name, 1],
                expect_return=False))
        # 25.
        self.steps_list.append(testcase.TestCaseStep("Check output console of jenkins job",
                "curl -s -k -u __OUTPUT__[9][0]:__OUTPUT__[9][1] -H 'Pragma: no-cache' https://__OUTPUT__[4]/job/%s-build/4/console" %(self.app_name),
                expect_return=0,
                expect_string_list=['----Post_Deploy Fail Test----'],
                try_count=4,
                try_interval=10))

        # 26.
        self.steps_list.append(testcase.TestCaseStep("Check output of app",
                "curl -s -H 'Pragma: no-cache' __OUTPUT__[5]",
                expect_return=0,
                expect_string_list=['Welcome~~~'],
                unexpect_string_list=['Welcome to OpenShift'],
                try_count=4,
                try_interval=30))

        # 27.
        self.steps_list.append(testcase.TestCaseStep("Restore .openshift/action_hooks/post_deploy",
                "rm %s/.openshift/action_hooks/post_deploy" %(self.app_name),
                expect_return=0))

        # 28.
        self.steps_list.append(testcase.TestCaseStep("Triger jenkins build",
                common.trigger_jenkins_build,
                function_parameters=[self.app_name,],
                expect_return=True))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def get_jenkins_username_password(self, user, jenkins_name):
        return (user.conf["apps"][jenkins_name]["username"], user.conf["apps"][jenkins_name]["password"])


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsJobUponFailBuild)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
