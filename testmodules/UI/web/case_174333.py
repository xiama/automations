#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174333.py
#  Date:      2012/07/17 11:23
#  Author: mgao@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckEapInTechnologyPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.go_to_home()
        web.click_element_by_link_text("DEVELOPERS")
        web.click_element_by_link_text("Platform Features")
       
        #check whether the EAP is added in this page.
        web.assert_element_present_by_link_text("JBoss Enterpise Application Platform 6.0")  
        web.assert_text_equal_by_xpath('''Market-leading open source enterprise platform for next-generation, highly transactional enterprise Java applications. Build and deploy enterprise Java in the cloud.''','''//div[@id='node-10863']/div/table/tbody/tr/td[2]''') 
       

        self.tearDown()

        return self.passed(" case_174333--CheckEapInTechnologyPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckEapInTechnologyPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174333.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
