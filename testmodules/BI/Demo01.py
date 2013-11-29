#!/usr/bin/env python

"""
"""
import rhtest
import database
import time

import random
PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = "Titan"

    def initialize(self):
        #tb = self.config.testbed
        pass

    def finalize(self):
        pass


class Demo01(OpenShiftTest):
    def test_method(self):
        errorCount = ((random.randint(1, 8) % 8) == 0)

        if errorCount:
            return self.failed("Demo01 test failed.")
        else:
            return self.passed("Demo01 test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo01)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
