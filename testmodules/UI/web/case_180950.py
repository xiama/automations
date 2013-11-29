#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180950.py
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


class CreateSpringeap6App(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a springeap6 app
        #web.create_app("springeap6","springeap")
        web.go_to_create_app("springeap6")
        web.input_by_id("application_name", "springeap")
        web.click_element_by_id("application_submit")
        time.sleep(50)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')
     
        #check the "appurl" link
        time.sleep(300)
        web.go_to_app_detail("springeap")
        web.click_element_by_xpath('''//div[@id='content']/div/div/div/div[2]/nav/div/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath("Spring MVC Starter Application",'''//title''')  

        #delete a springeap app
        web.go_to_app_detail("springeap")
        time.sleep(2)
        web.click_element_by_link_text("Delete this application")
        time.sleep(1)
        web.click_element_by_id("application_submit")
        time.sleep(40)
        web.go_to_app_detail("springeap")
        web.assert_text_equal_by_xpath("Sorry, but the page you were trying to view does not exist.", '''//article/div/p''')


        self.tearDown()

        return self.passed(" case_180950--CreateSpringeap6App passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateSpringeap6App)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_180950.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
