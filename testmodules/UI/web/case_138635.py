#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138635.py
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


class CheckAppsListPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        #web.go_to_home()
        #web.go_to_signin()
        #web.input_by_id("web_user_rhlogin", "mgao+stg33@redhat.com")
        #web.input_by_id("web_user_password", "redhat")
        #web.click_element_by_xpath("//input[@id='web_user_submit']")
        web.login()

        #web.delete_app("python")
        #create a python app
        web.create_app("python-2.6","python")


        #check wether the links are correct
        #time.sleep(20)
        #go to the app list page
        web.go_to_app_detail("")

        #check the "app overview" link
        web.click_element_by_xpath('''//section[@id='app-list']/div/div/div/h2/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''PYTHON''','''/html/body/div/div/div/div/div/div/nav/ul/li[2]/a''')
        web.go_back()
        #check the "appurl" link
        web.click_element_by_xpath('''//section[@id='app-list']/div/div/div/div/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Welcome To OpenShift''','''//body/h1''')
        web.go_back()
        #check the " Add Application" link
        web.click_element_by_xpath('''//section[@id='app-list']/div[2]/a/strong''')
        time.sleep(2)
        #web.assert_text_equal_by_xpath('''Create a New Application''','''//div[@id='content']/div/div/div/div[2]/div/h1''')
        web.go_back()
        #check the "Developer Center" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Developer Center''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')
        web.go_back()
        #check the "OpenShift User Guide" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift''','''//div[@id='id2789633']/div/div/div/span''')
        web.go_back()

        #check the "Installing OpenShift client tools on Mac OSX, Linux, and Windows" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li[3]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Get Started with OpenShift''','''//div[@id='content']/div/div/div//div/div/h1''')
        web.go_back()
        #check the "Sync your OpenShift repo with an existing Git repo" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li[4]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Knowledge Base''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')
        web.go_back()
        #check the "More help »" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li[5]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Create''','''//div[@id='content']/div/div/div/div[2]/div/section/div/h2''')
        web.go_back()
        #check the "How do I start a new Forum discussion?" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul[2]/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''How do I start a new Forum discussion?''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')
        web.go_back()
        #check the "How do I install the rhc client tools on Windows?" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul[2]/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''How do I install the rhc client tools on Windows?''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')
        web.go_back()
        #check the "More FAQs »" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul[2]/li[3]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Frequently Asked Questions''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')
               
        #delete a python app
        web.delete_app("python")


        self.tearDown()

        return self.passed(" case_138635--CheckAppsListPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckAppsListPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138635.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
