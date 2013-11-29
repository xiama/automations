#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_135715.py
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


class Change_oldpassword_invalid(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Change password using wrong old password
        web.go_to_account()       
        web.click_element_by_xpath('''//section/div/div/a''')
        time.sleep(5)
        web.input_by_id('web_user_old_password','adfasdf')
        web.input_by_id('web_user_password','ssssss')
        web.input_by_id('web_user_password_confirmation','ssssss')
        web.click_element_by_xpath('''//form[@id='new_web_user']/fieldset[2]/input''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Your old password was incorrect''',
            '''//div[@id='web_user_old_password_input']/div/p''')        

        self.tearDown()

        return self.passed("Case 135715 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Change_oldpassword_invalid)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_135715.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
