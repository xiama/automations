#!/usr/bin/env python

"""
Demo for UI autotesting
"""
import rhtest
import common 

class OpenShiftTest(rhtest.Test): 
    INTERACTIVE = False

    def initialize(self):
        self.domain_name = common.get_domain_name()
        self.new_domain = common.getRandomString(10)
        common.env_setup()

    def finalize(self):
        pass


class Demo01(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        #1 create an domain via REST
        self.info("Altering domain to %s"%self.new_domain)
        (status, rest) = self.config.rest_api.domain_update(self.new_domain)
        self.assert_equal('OK', status, 'Unable to alter domain to %s'%self.new_domain)

        #2. let's check the domain via UI
        web.go_to_home()
        web.go_to_signin()
        web.login()
        web.go_to_account()
        web.assert_text_equal_by_xpath(self.new_domain, 
            '''id('content')/div/div/div/div[2]/div/div/div[1]/section[2]/div[1]/strong''')

        return self.passed("UI Demo01 test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo01)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
