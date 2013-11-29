#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_135712.py
#  Date:      2012/07/24 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Change_password_invalid(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Change password using invalid new password
        web.go_to_account()       
        web.click_element_by_xpath('''//section/div/div/a''')
        time.sleep(5)
        web.input_by_id('web_user_old_password',web.config.OPENSHIFT_user_passwd)
        web.input_by_id('web_user_password','ss')
        web.input_by_id('web_user_password_confirmation','ss')
        web.click_element_by_xpath('''//form[@id='new_web_user']/fieldset[2]/input''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Passwords must be at least 6 characters''',
            '''//div[@id='web_user_password_input']/div/p''')        

        self.tearDown()

        return self.passed("Case 135712 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Change_password_invalid)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_135712.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
