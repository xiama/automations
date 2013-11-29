#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_145623.py
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


class SignInFirstTime(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login_new(web.username_not_accept_terms_account,web.password_not_accept_terms_account)
        web.assert_text_equal_by_xpath("Legal terms","//div[@id='content']/div/div/div/div/div/h1")
        web.assert_text_equal_by_xpath('''Please Accept the Following Terms\nBefore participating in the OpenShift Preview Program and receiving the Preview Services, Preview Software and access to online properties, you need to accept certain terms and conditions. The link below contains a list of the terms that will apply to your use.\nOpenShift Legal Terms and Conditions\nClicking I accept means that you agree to the above terms.''',"//div[@id='content']/div/div/div/div/div/section")

        
        self.tearDown()

        return self.passed(" case_145623--SignInFirstTime passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SignInFirstTime)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_145623.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
