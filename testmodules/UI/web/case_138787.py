#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138787.py
#  Date:      2012/08/06 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Create_duplicate_app(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create python2 application
        web.create_app("python-2.6", "python2")
        time.sleep(10) 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://python2-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")

        #Create a duplicate python2 application
        web.go_to_create_app("python-2.6")
        web.input_by_id("application_name", "python2")
        web.click_element_by_id("application_submit")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''The supplied application name 'python2' already exists''', '''//form[@id='new_application']/ul/li''') 

        web.delete_last_app("python2")
  
        self.tearDown()

        return self.passed("Case 138787 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_duplicate_app)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138787.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
