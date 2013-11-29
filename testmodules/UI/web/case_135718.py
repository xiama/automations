#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_135718.py
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


class Add_Invalid_Sshkey(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Change password
        web.go_to_account_page()
        web.input_by_id("key_raw_content", "ffffffff")
        web.click_element_by_id("key_submit")
        time.sleep(10)
        web.assert_text_equal_by_xpath('''Type is required and cannot be blank.''', '''//div[@id='key_raw_content_input']/div/p''')       

        self.tearDown()

        return self.passed("Case 135718 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Add_Invalid_Sshkey)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_135718.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
