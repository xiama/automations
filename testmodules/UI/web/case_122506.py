#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122506.py
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


class LoginWithExistingAccount(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        web.go_to_home()
        web.go_to_signin()
        web.login()

        web.assert_text_equal_by_xpath('''yujzhang''','''//a[contains(@href,'/app/account')]''')

       

        self.tearDown()

        return self.passed(" case_122506--LoginWithExistingAccount passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LoginWithExistingAccount)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122482.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
