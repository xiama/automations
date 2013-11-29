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
    ITEST = ['DEV', 'STG']

    def initialize(self):
        self.msg = self.config.msg

    def finalize(self):
        pass


class TestPreReqPass(OpenShiftTest):
    def test_method(self):
        self.info("%s" % self.msg)
        return self.passed("test passed.")

class DependentParent(OpenShiftTest):
    PREREQUISITES = [rhtest.PreReq("TestPreReqPass")]

    def test_method(self):
        self.info("This is the parent...")
        return self.passed("test passed.")

class DependentOne(OpenShiftTest):
    PREREQUISITES = [rhtest.PreReq("DependentParent")]
    
    def test_method(self):
        self.info("This is the child #1...")
        return self.passed("test passed.")

class DependentTwo(OpenShiftTest):
    PREREQUISITES = [rhtest.PreReq("DependentParent")]
    
    def test_method(self):
        self.info("This is the child #2...")
        return self.failed("test failed.")

class DependentThree(OpenShiftTest):
    PREREQUISITES = [rhtest.PreReq("DependentOne"), rhtest.PreReq("DependentTwo") ]
    
    def test_method(self):
        # this test will NOT be executed unless DependentOne & DependentTwo passed
        self.info("This is the child #3, you shouldn't NEVER see this message...")
        return self.passed("test passed.")


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(TestPreReqPass)
    suite.add_test(DependentParent)
    suite.add_test(DependentOne)
    suite.add_test(DependentTwo)
    suite.add_test(DependentThree)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
