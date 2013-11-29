#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122254.py
#  Date:      2012/07/24 14:23
#  Author: mgao@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class RegisterWithoutEmail(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()

	#go to the register page
        web.go_to_register()

	#register  without email
        web.input_by_id("web_user_password","redhat")
        web.input_by_id("web_user_password_confirmation","redhat")

        #click to register
        web.click_element_by_xpath('''//input[@id='web_user_submit']''')         
        time.sleep(2)
        web.assert_text_equal_by_xpath('''This field is required.''',
            '''//div[@id='web_user_email_address_input']/div/p''')
		

        self.tearDown()

        return self.passed("Case 122254--register without email test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RegisterWithoutEmail)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122254.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
