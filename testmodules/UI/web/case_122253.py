#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122253.py
#  Date:      2012/07/04 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Register_mismatch_password(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_register()
        #time.sleep(5)
        
        #Register using invalid password.
        web.input_by_id("web_user_email_address", "yujzhang@redhat.com")
        web.input_by_id("web_user_password", "ssssss")
        web.input_by_id("web_user_password_confirmation", "ffffff")
        web.click_element_by_xpath('''//form[@id='new_user_form']/fieldset[2]/div[3]/input''')
        time.sleep(20)
        web.assert_text_equal_by_xpath('Please enter the same value again.',
            '''//div[@id='web_user_password_confirmation_input']/div/p''')

        self.tearDown()

        return self.passed("Case 122253 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Register_mismatch_password)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122253.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
