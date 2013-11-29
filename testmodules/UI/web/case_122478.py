#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122478.py
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


class Change_password(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Change password
        web.change_password(web.config.OPENSHIFT_user_passwd, "aaaaaa")
        web.click_element_by_link_text("yujzhang")
        web.click_element_by_link_text("Sign Out")
        time.sleep(10)
        web.login_new(web.config.OPENSHIFT_user_email, "aaaaaa")
        web.change_password("aaaaaa", web.config.OPENSHIFT_user_passwd)
        

        self.tearDown()

        return self.passed("Case 122478 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Change_password)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122478.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
