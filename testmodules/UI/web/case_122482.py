#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122482.py
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


class ResetPasswordWithNonExistingUser(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        web.go_to_home()
        web.go_to_signin()
        #web.login()
        web.click_element_by_xpath('''//div[@id='web_user_password_input']/div/p/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Reset your password''',
            '''//div/h1''')
        web.input_by_id("web_user_login", "")
        web.click_element_by_xpath("//input[@id='web_user_submit']")
        web.assert_text_equal_by_xpath('''Login can't be blank''',
            '''//div[@id='web_user_login_input']/div/p''')

       

        self.tearDown()

        return self.passed(" case_122482--ResetPasswordWithNonExistingUser passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ResetPasswordWithNonExistingUser)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122482.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
