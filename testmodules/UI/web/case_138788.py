#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138788.py
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


class Create_app_max_name(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create python application
        web.create_app("python-2.6", "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        time.sleep(10) 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")
        web.delete_last_app("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
  
        self.tearDown()

        return self.passed("Case 138788 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_app_max_name)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138788.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
