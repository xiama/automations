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

    def initialize(self):
        self.msg = self.config.msg

    def finalize(self):
        pass


class Demo03(OpenShiftTest):
    def test_method(self):
        self.info("This is demo03")
        time.sleep(3)
        return self.passed("test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo03)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
