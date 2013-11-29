#!/usr/bin/env python

"""
"""
import rhtest
import database
import time
import common

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):

    def initialize(self):
        self.msg = self.config.msg
        self.cart_type = self.config.tc_arguments['cart_type']
        self.variants = self.config.tc_arguments['variants']
        self.app_name = self.config.app_name + self.cart_type
        print "############################"
        #self.info("%s" % self.config.tc_args.keys())

    def finalize(self):
        pass


class Demo01(OpenShiftTest):
    def test_method(self, args=None):
        #cart_type = common.app_types[self.cart_type]
        #self.info("Creating app for cartridge type '%s'" % cart_type)
        # create an app
        #status, res = self.config.rest_api.app_create(self.app_name, cart_type, scale=False)
        #if status[0] == 'Created':
        return self.passed("Test passed.")
        #else:
        #return self.failed("Test failed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo01)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
