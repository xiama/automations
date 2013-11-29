#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122359.py
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


class Create_3_app(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create 3 python applications
        web.create_app("python-2.6", "python2")
        time.sleep(10) 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://python2-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")

        web.create_app("python-2.6", "python3")
        time.sleep(10) 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://python3-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")
 
        web.create_app("python-2.6", "python4") 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://python4-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")

        web.delete_app("python2")
        web.delete_app("python3")
        web.delete_last_app("python4")

        self.tearDown()

        return self.passed("Case 122422 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_3_app)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122422.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
