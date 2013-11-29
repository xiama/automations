#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Feb 20, 2012

[rhc-cartridge][US1651] Idea: Customized raw cartridges
https://tcms.engineering.redhat.com/case/135842/
"""

import os
import sys
import shutil
import commands

import rhtest
import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_type = 'diy'
        self.summary = "[rhc-cartridge][US1651] Idea: Customized raw cartridges"
        self.app_name = 'my%s%s' % ( self.app_type, common.getRandomString() )
        self.git_repo = './' + self.app_name
        self.steps = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class RawCustomized(OpenShiftTest):
    def test_method(self):
        self.steps.append(testcase.TestCaseStep(
            'Creating an application',
            common.create_app,
            function_parameters = [ self.app_name, 
                                    common.app_types[self.app_type],
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd, 
                                    True, self.git_repo ],
            expect_description = 'The app should be created successfully',
            expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
            "Checking the new welcome message",
            self.check_webpage_output,
            function_parameters = [ self.app_name, 
                                    "", 
                                    "Do-It-Yourself cartridge" ],
            expect_description = 'The proxy error-message should be customized, OpenShift branded',
            expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
            "Setting up custom Django application",
            self.custom_app_setup,
            expect_description = "Our custom Django app should be installed succesfully",
            expect_return = 0))
        
        self.steps.append(testcase.TestCaseStep(
            "Cheking the output of our Django project",
            common.grep_web_page,
            function_parameters = [self.get_app_url("/version/"), "131final0", "-H 'Pragma: no-cache'", 5, 4],
            expect_description = "The output of your Django project should show the right version number",
            expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
            "Stopping the application",
            common.stop_app,
            function_parameters = [ self.app_name, 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd ],
            expect_description = "The application should be stopped successfully",
            expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
            "Checking the output of the stopping Django project",
            common.grep_web_page,
            function_parameters = [self.get_app_url("/version/"), "Service Temporarily Unavailable", "-H 'Pragma: no-cache'", 5, 4],
            expect_description = 'The proxy error-message should be customized, OpenShift branded',
            expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
            "Starting the application",
            common.start_app,
            function_parameters = [ self.app_name, 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd ],
            expect_description = "The application should be started successfully",
            expect_return = 0))


        self.steps.append(testcase.TestCaseStep(
            "Cheking the output of our Django project",
            common.grep_web_page,
            function_parameters = [self.get_app_url("/version/"), 
                                   "131final0", 
                                   "-H 'Pragma: no-cache'", 25, 4],
            expect_description = "The output of your Django project should show the right version number",
            expect_return = 0))


        case = testcase.TestCase(self.summary, self.steps)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def get_app_url(self, suffix=""):
        def closure():
            return OSConf.get_app_url(self.app_name)+suffix
        return closure


    def custom_app_setup(self, remote_download=False):
        tmp_dir = os.path.expanduser("~")
        django_tarball_name = "django-1.3.1.tar.gz"
        django_tarball_dir = django_tarball_name.capitalize().replace(".tar.gz", "")
        django_download_url = "http://www.djangoproject.com/download/1.3.1/tarball/"
        if remote_download:
            download_step = [
                "rm -rf %s/%s" %(tmp_dir, django_tarball_name),
                "wget %s -O %s/%s" % ( django_download_url, tmp_dir, django_tarball_name )
            ]
        else:
            download_step = [
                "rm -rf %s/%s" %(tmp_dir, django_tarball_name),
                "cp %s/app_template/%s %s/%s" % (WORK_DIR, django_tarball_name, tmp_dir, django_tarball_name)
            ]
 
        app_setup_steps =  download_step + [
            "cd %s" % ( tmp_dir ),
            "tar -xvzf %s" % ( django_tarball_name ),
            "cd -",
            "cp -Rf %s/%s/django/ %s/diy/" % ( tmp_dir, django_tarball_dir, self.git_repo ),
            "cp -Rf %s/app_template/django_custom/mydiyapp/ %s/diy/" % ( WORK_DIR, self.git_repo ),
            "cp -fv %s/app_template/django_custom/{start,stop} %s/.openshift/action_hooks/" % ( WORK_DIR, self.git_repo ),
            "cd %s" % ( self.git_repo ),
            "git add .",
            "git commit -a -m deployment",
            "git push",
            "rm -Rfv %s/{D,d}jango*" % ( tmp_dir ) # cleaning up
        ]

        ( ret_code, ret_output) = commands.getstatusoutput(" && ".join(app_setup_steps))
        print ret_output
        return ret_code

    def check_webpage_output(self, app_name, path, pattern, delay = 20):
        app_url = OSConf.get_app_url(app_name)
        return common.grep_web_page( "http://%s/%s" % ( app_url, path ), pattern, delay=delay )


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RawCustomized)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
