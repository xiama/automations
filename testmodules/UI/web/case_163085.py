#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_163080.py
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


class LoginWithEmailOfRHNAccount(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login_new(web.username_email_of_RHN_account,web.password_email_of_RHN_account)

        web.assert_text_equal_by_xpath(web.username_RHN_account,"//li[3]/a")



        self.tearDown()

        return self.passed(" case_163085--LoginWithEmailOfRHNAccount passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LoginWithEmailOfRHNAccount)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_163080.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
