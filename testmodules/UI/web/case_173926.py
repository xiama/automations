#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_173926.py
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


class CheckPricingLink(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        web.go_to_pricing()
        web.assert_text_equal_by_xpath('''Pricing''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')


       

        self.tearDown()

        return self.passed(" case_173926--CheckPricingLink passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckPricingLink)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_173926.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
