#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122239.py
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


class Login_valid_account(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()
        time.sleep(5)
        
        #Login using valid account and existing session.
        web.assert_text_equal_by_xpath('SIGN IN',
            '''//div[@id='top']/div/div[2]/a''')
        web.click_element_by_xpath('''//div[@id='top']/div/div[2]/a''')
        web.input_by_id("web_user_rhlogin", "yujzhang")
        web.input_by_id("web_user_password", "111111")
        web.click_element_by_xpath('''//form[@id='login_form']/fieldset/input''')
        time.sleep(10)
        web.assert_text_equal_by_xpath('MANAGEMENT CONSOLE',
            '''//div/span''')
        web.click_element_by_xpath('''//ul[@id='utility-nav']/li[3]/a''')
        web.click_element_by_xpath('''//ul[@id='utility-nav']/li[3]/ul/li[2]/a''')
        time.sleep(10)
        web.assert_text_equal_by_xpath('SIGN IN',
            '''//div[@id='top']/div/div[2]/a''')
        web.click_element_by_xpath('''//div[@id='top']/div/div[2]/a''')
        web.input_by_id("web_user_rhlogin", "yujzhang")
        web.input_by_id("web_user_password", "111111")
        web.click_element_by_xpath('''//form[@id='login_form']/fieldset/input''')
        time.sleep(10)
        web.assert_text_equal_by_xpath('MANAGEMENT CONSOLE',
            '''//div/span''')



        self.tearDown()

        return self.passed("Case 122239 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Login_valid_account)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122239.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
