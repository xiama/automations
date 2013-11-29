#!/usr/bin/env python

"""
"""
import rhtest
import database
#### test specific import
import random


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        ### put test specific initialization steps here
        pass

    def record_results(self, resid):
        # put testcase specific storing data to specific tables here.
        pass

    def finalize(self):
        ### put test specific steps 
        pass
    

class Demo01(OpenShiftTest):
    def test_method(self):
        """
        This is a very simple test...but the pattern is the same, the 

        """
        errorCount = ((random.randint(1, 3) % 2) == 0)


        # this will trigger not only print to the console, but also stroed the
        # test run information as PASSED/FAILED/ABORTED
        if errorCount:
            return self.failed("Demo01 test failed.")
        else:
            return self.passed("Demo01 test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo01)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
