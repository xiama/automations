#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_145621.py
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


class CheckSignInLink(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.go_to_home()
        web.click_element_by_link_text("SIGN IN")
        time.sleep(3)
        web.assert_text_equal_by_xpath("Sign in to OpenShift","//div[@id='content']/div/div/div/div/div/h1")
        web.assert_text_equal_by_xpath("Login","//div[@id='web_user_rhlogin_input']/label")
        web.assert_text_equal_by_xpath("Password","//div[@id='web_user_password_input']/label")


        self.tearDown()

        return self.passed(" case_145621--CheckSignInLink passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckSignInLink)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_145621.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
