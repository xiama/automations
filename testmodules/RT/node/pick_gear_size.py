"""
Attila Nagy
anagy@redhat.com

[US1373][UI][CLI] Pick gear size
"""

import sys
import subprocess
import os

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    ITEST = [ "DEV" ]
    def initialize(self):
        self.summary = "[US1373][UI][CLI] Pick gear size"
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'jbossas'
        self.app_name = "my%s%s" % ( self.app_type, common.getRandomString() )
        self.steps_list = []

        common.env_setup()
        if self.get_run_mode() == "DEV":
            common.add_gearsize_capability('medium')

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))
        if self.get_run_mode() == "DEV":
            common.remove_gearsize_capability('medium')
    
class PickGearSize(OpenShiftTest):
    #
    # With current framework it's almost impossible to implement
    #
    # In order to create medium / large gear-sized application 
    # I need a devenv instance with medium / large profile
    #
    # Waiting for the final implementation of the new framework
    #
    #for gear_size in [ 'small', 'medium', 'large' ]:
    #    # Creating the application
    #    steps.append(testcase.TestCaseStep(
    #        "Creating application with gear size '%s'" % ( gear_size ),
    #        "rhc app create -a %s -t %s -g %s -l %s -p %s -n" % ( self.app_name, common.self.app_types[self.app_type], gear_size, self.user_email, self.user_passwd ),
    #        expect_description = "The application must be created successfully with the given gear size",
    #        expect_return = 0                               
    #    ))
    #
    #    
    #    # Destroying the application
    #    steps.append(testcase.TestCaseStep(
    #        "Destroying the application with gear size '%s'" % ( gear_size ),
    #        "rhc app destroy -a %s -b -l %s -p %s" % ( self.app_name, self.user_email, self.user_passwd ),
    #        expect_description = "The application must be destroyed successfully",
    #        expect_return = 0                                   
    #    ))
        
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
                "Creating application with a not supported gear size",
                "rhc app create %s %s -g %s -l %s -p %s --no-git %s" 
                     % (self.app_name, 
                        common.app_types[self.app_type],
                        common.get_domain_name(), self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description = "The application must be not created",
                expect_return = "!0"))
    
        case = testcase.TestCase(
            self.summary, 
            self.steps_list,
            clean_up_function_parameters = [ self.config.OPENSHIFT_user_email, False ]) # Reverting to False to not bother other test-cases)

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
    suite.add_test(PickGearSize)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
