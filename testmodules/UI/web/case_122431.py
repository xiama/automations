#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122431.py
#  Date:      2012/07/25 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Create_python_app(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create python application
        web.create_app("python-2.6", "python2")
        time.sleep(10) 
        web.click_element_by_link_text('''My Applications''')
        time.sleep(2)
        web.click_element_by_link_text('''http://python2-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")
        web.delete_last_app("python2")

        self.tearDown()

        return self.passed("Case 122431 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_python_app)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122431.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
