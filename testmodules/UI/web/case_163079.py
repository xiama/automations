#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_163079.py
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


class LoginWithEmailBothRegistedInOenshiftAndRHN(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login_new(web.username_both_registered_openshift_account,web.password_both_registered_openshift_account)
        web.go_to_account_page()
        web.assert_text_equal_by_xpath(web.username_both_registered_openshift_account,"//div[@id='new_web_user']/table/tbody/tr/td")
        web.assert_text_equal_by_xpath("OpenShift","//div[@id='new_web_user']/table/tbody/tr/td[2]")


        self.tearDown()

        return self.passed(" case_163079--LoginWithEmailBothRegistedInOenshiftAndRHN passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LoginWithEmailBothRegistedInOenshiftAndRHN)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_163079.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
