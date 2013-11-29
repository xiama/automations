#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122417.py
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


class Create_nonalphametic_domain(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create domain with non alphametic domain
        web.assert_text_equal_by_xpath('''MANAGEMENT CONSOLE''',
            '''//div/span''')
        web.go_to_domain_edit()
        web.input_by_id('domain_name','##')
        web.click_element_by_id('domain_submit')
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Invalid namespace. Namespace must only contain alphanumeric characters.''',
            '''//form[@id='edit_domain_##']/ul/li''') 

        self.tearDown()

        return self.passed("Case 122417 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_nonalphametic_domain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122417.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
