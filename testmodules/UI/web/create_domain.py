#!/usr/bin/env python
# coding=utf-8
#
#  File name: create_domain.py
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


class Create_Domain(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
        time.sleep(5)
        
        #Create domain name
        web.go_to_domain_edit()
        time.sleep(3)
        web.input_by_id("domain_name", web.config.OPENSHIFT_user_email)
        web.click_element_by_id("domain_submit)
        time.sleep(20)
        web.assert_text_equal_by_xpath('Your domain has been created',
            '''//div[@id='flash']/div''')

        self.tearDown()

        return self.passed("Create domain name finished.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Create_Domain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of create_domain.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
