#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138789.py
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


class Create_duplicate_domain(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create duplicate domain
        web.go_to_account_page()
        time.sleep(10)
        web.click_element_by_link_text("Change your namespace...")
        web.clear_element_value("domain_name")
        web.input_by_id("domain_name", web.domain)        
        web.click_element_by_id("domain_submit")
        time.sleep(10)
        web.assert_text_equal_by_xpath("Namespace '"+web.domain+"' already in use. Please choose another.", "//form[@id='edit_domain_"+web.domain+"']/ul/li")       

        self.tearDown()

        return self.passed("Case 138789 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_duplicate_domain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138789.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
