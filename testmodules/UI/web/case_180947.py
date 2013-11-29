#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180947.py
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


class AddAllCartridgeToRubyOnRailsApp(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        ##web.create_app("rails","rubyonrails")
        web.go_to_create_app("rails")
        web.input_by_id("application_name", "rubyonrails")
        web.click_element_by_id("application_submit")
        time.sleep(40)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')
       
        #go to app rubyonrails page and add cartridges
        web.add_cartridge("rubyonrails", "mongodb-2.2")
        time.sleep(8)
        web.assert_text_equal_by_xpath("rhc app cartridge remove -a rubyonrails -c mongodb-2.2",'''//pre[3]''')  

        web.add_cartridge("rubyonrails", "cron-1.4")
        web.assert_text_equal_by_xpath("Cron 1.4",'''//div[@id='cartridge_type_']/h3''')


        web.add_cartridge("rubyonrails","metrics-0.1")
        web.assert_text_equal_by_xpath("OpenShift Metrics 0.1",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("rubyonrails","phpmyadmin-3.4")
        web.assert_text_equal_by_xpath("phpMyAdmin 3.4",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("rubyonrails","rockmongo-1.1")
        web.assert_text_equal_by_xpath("RockMongo 1.1",'''//div[@id='cartridge_type_']/h3''')

        web.go_to_app_detail("rubyonrails")
        web.click_element_by_xpath('''//a[contains(@href, '/building')]''')
        time.sleep(3)
        web.input_by_id("application_name", "jenkins")
        web.click_element_by_id("application_submit")
        time.sleep(150)  
        web.assert_text_equal_by_xpath("Building your Application",'''//div[@id='content']/div/div/div/div[2]/div/h1''')



        #delete a rubyonrails app
        web.delete_app("rubyonrails")
        #delete a jenkins app
        web.delete_last_app("jenkins")


        self.tearDown()

        return self.passed(" case_180947--AddAllCartridgeToRubyOnRailsApp passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AddAllCartridgeToRubyOnRailsApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_180947.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
