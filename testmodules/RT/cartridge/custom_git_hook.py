#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[rhc-cartridge] Custom git post-receive hook
https://tcms.engineering.redhat.com/case/122274/
"""
import sys,os
import testcase,common
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge] Custom git post-receive hook"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing test_variant, used `php` as default")
            self.test_variant = 'php'

        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(7)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        tcms_testcase_id=122274
        common.env_setup()
        common.clean_up(self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)

        self.steps_list = []

    def finalize(self):
        pass

class CustomGitHook(OpenShiftTest):
    def test_method(self):

        # 1. Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Custom git hook
        def add_build_hook():
            target_file_part = "README.md"
            hook_file_path = "%s/.openshift/action_hooks/build" % (self.app_name)
            try:
                f = open(hook_file_path,"a") #append ...
                f.write("""
#!/bin/bash
function list_file(){
    command = "ls -l $1"
    echo "Command: $command"
    eval "$command"
}

test_file="${OPENSHIFT_REPO_DIR}%s"
if [ -f $test_file ]; then
    list_file "$test_file"
else
    echo "$test_file does not exist"
    echo "RESULT=1"
    exit 1
fi

if [ ! -x $test_file ]; then
    echo "$test_file does not have execute permission"
    command="chmod +x $test_file"
    echo "Command: $command"
    eval "$command"

    list_file "$test_file"

    if [ -x $test_file ]; then
        echo "$test_file own execute permission now"
        echo "RESULT=0"
        exit 0
    else
        "$test_file still does not have execute permission"
        echo "RESULT=1"
        exit 1
    fi
else
    echo "$test_file already own execute permission!!!"
    echo "RESULT=1"
    exit 1
fi""" %(target_file_part))
                f.close()
            except:
                return 1

            return 0

        #cmd = "echo '%s' >> %s" % (testcode, hook_file_path)
        self.steps_list.append( testcase.TestCaseStep("2.Custom git hook",
                add_build_hook,
                expect_description="git repo is modified successfully",
                expect_return=0))
        self.steps_list.append( testcase.TestCaseStep("2.chomod +x for build",
                "chmod +x %s/.openshift/action_hooks/build" % (self.app_name),
                expect_return=0))


        # 3.Git push all the changes and check the output
        self.steps_list.append( testcase.TestCaseStep("3.Git push all the changes and check the output",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="Git push should succeed",
                expect_return=0,
                expect_string_list=["RESULT=0"]))

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
    suite.add_test(CustomGitHook)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
