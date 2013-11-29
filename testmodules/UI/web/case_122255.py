#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122255.py
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


class RegisterWithoutPasswd(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()

	#go to the register page
        web.go_to_register()

	#register without password
        web.input_by_id("web_user_email_address",'''mgao+stg42@redhat.com''')

        #click to register
        web.click_element_by_xpath('''//input[@id='web_user_submit']''')         
        time.sleep(2)
        web.assert_text_equal_by_xpath('''This field is required.''',
            '''//div[@id='web_user_password_input']/div/p''')
		

        self.tearDown()

        return self.passed("Case 122255--register without password test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RegisterWithoutPasswd)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122255.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
