#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_147640.py
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


class Check_wiki_page(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Check wiki page
        web.go_to_community()
        time.sleep(5)
        web.click_element_by_link_text("Open Source")
        time.sleep(5)
        web.click_element_by_link_text("Index")
        time.sleep(5)
        web.check_title("Wiki Index | OpenShift by Red Hat")    
      
        self.tearDown()

        return self.passed("Case 147640 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Check_wiki_page)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_147640.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
