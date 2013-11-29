#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122427.py
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


class Create_jboss_app(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create jboss application
        web.create_app("jbossas-7", "jboss2")
        time.sleep(10)
        web.click_element_by_link_text('''My Applications''')
        time.sleep(5)
        web.click_element_by_link_text('''http://jboss2-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(5)
        web.check_title("Welcome to OpenShift")
 
        web.delete_last_app("jboss2")

        self.tearDown()

        return self.passed("Case 122427 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_jboss_app)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122427.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
