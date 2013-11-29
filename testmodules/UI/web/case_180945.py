#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180945.py
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


class CreateRubyAndRailsApp(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
        #web.delete_app("ruby19")
        #create a ruby1.9 app
        #web.create_app("rails","rubyonrails")
        web.go_to_create_app("rails")
        web.input_by_id("application_name", "rubyonrails")
        web.click_element_by_id("application_submit")
        time.sleep(50)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')
     
        #check the "appurl" link
        time.sleep(500)
        web.go_to_app_detail("rubyonrails")
        web.click_element_by_xpath('''//div[@id='content']/div/div/div/div[2]/nav/div/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath("OpenShift - Rails 3.2",'''//h1''') 

        #delete a rubyonrails app
        web.go_to_app_detail("rubyonrails")
        time.sleep(2)
        web.click_element_by_link_text("Delete this application")
        time.sleep(1)
        web.click_element_by_id("application_submit")
        time.sleep(40)
        web.go_to_app_detail("rubyonrails")
        web.assert_text_equal_by_xpath("Sorry, but the page you were trying to view does not exist.", '''//article/div/p''')


        self.tearDown()

        return self.passed(" case_180945--CreateRubyAndRailsApp passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateRubyAndRailsApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_180945.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
