#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174334.py
#  Date:      2012/07/17 11:23
#  Author: mgao@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CreateJbossEapApp(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        #web.go_to_login()

        #web.input_by_id("web_user_rhlogin", "mgao+stg33@redhat.com")
        #web.input_by_id("web_user_password", "redhat")
        #web.driver.find_element_by_id("web_user_submit").click()
        #time.sleep(5)

                #COMMUNITY
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/header/h3/a''')
        web.assert_text_equal_by_xpath('Welcome to OpenShift',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div[1]''',
            'Community page is missing')


        



        self.tearDown()

        return self.passed(" case_174334--CreateJbossEapApp passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateJbossEapApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174334.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
