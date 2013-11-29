#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138790.py
#  Date:      2012/07/25 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Create_Long_domain(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create duplicate domain
        web.go_to_account_page()
        time.sleep(10)
        web.click_element_by_link_text("Change your namespace...")
        time.sleep(5)
        web.clear_element_value("domain_name")
        web.input_by_id("domain_name", "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")        
        web.click_element_by_id("domain_submit")
        time.sleep(10)
        web.assert_text_equal_by_xpath("Namespace is too long. Maximum length is 16 characters.", '''//form/ul/li''')       

        self.tearDown()

        return self.passed("Case 138790 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_Long_domain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138790.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
