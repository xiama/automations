#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_167511.py
#  Date:      2012/08/13 11:23
#  Author: mgao@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckCommunityLinkForUserAppRequest(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
       
        #create a python app
        web.go_to_create_app("")

        web.click_element_by_link_text("suggest or vote for it")
        web.assert_text_equal_by_xpath('''Vote on Features''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')


        self.tearDown()

        return self.passed(" case_167511--CheckCommunityLinkForUserAppRequest passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckCommunityLinkForUserAppRequest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_167511.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
