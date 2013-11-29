#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122425.py
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


class Create_app_nonalphametic_name(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create app with non alphametic name
        web.assert_text_equal_by_xpath('''MANAGEMENT CONSOLE''',
            '''//div/span''')
        web.go_to_create_drupal()
        web.input_by_id('application_name','##')
        web.click_element_by_id('application_submit')
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Invalid name specified''',
            '''//form[@id='new_application']/ul/li''') 

        self.tearDown()

        return self.passed("Case 122425 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_app_nonalphametic_name)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122425.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
