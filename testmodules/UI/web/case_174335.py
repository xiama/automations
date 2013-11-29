#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174335.py
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


class AddAllCartridgeToJbossEapApp(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        #web.create_app("jbosseap-6.0","jbosseap")
        web.go_to_create_app("jbosseap-6.0")
        web.input_by_id("application_name", "jbosseap")
        web.click_element_by_id("application_submit")
        time.sleep(30)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')

        
        #go to app jbosseap page and add cartridges
        web.add_cartridge("jbosseap", "mongodb-2.2")
        time.sleep(5)
        #web.assert_text_equal_by_xpath("rhc app cartridge remove -a jbosseap -c mongodb-2.2",'''//div[@id='content']/div/div/div/div[2]/div/div[2]/div/pre[3]''')  
        web.assert_text_equal_by_xpath("rhc app cartridge remove -a jbosseap -c mongodb-2.2",'''//pre[3]''')  

        web.add_cartridge("jbosseap", "cron-1.4")
        web.assert_text_equal_by_xpath("Cron 1.4",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("jbosseap", "mysql-5.1")
        web.assert_text_equal_by_xpath("MySQL Database 5.1",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("jbosseap","metrics-0.1")
        web.assert_text_equal_by_xpath("OpenShift Metrics 0.1",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("jbosseap","phpmyadmin-3.4")
        web.assert_text_equal_by_xpath("phpMyAdmin 3.4",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("jbosseap","rockmongo-1.1")
        web.assert_text_equal_by_xpath("RockMongo 1.1",'''//div[@id='cartridge_type_']/h3''')

        web.go_to_app_detail("jbosseap")
        web.click_element_by_xpath('''//a[contains(@href, '/building')]''')
        time.sleep(2)
        web.input_by_id("application_name", "jenkins")
        web.click_element_by_id("application_submit")
        time.sleep(150)  
        web.assert_text_equal_by_xpath("Building your Application",'''//div[@id='content']/div/div/div/div[2]/div/h1''')



        #delete a jbosseap app
        web.delete_app("jbosseap")
        #delete a jenkins app
        web.delete_last_app("jenkins")



        self.tearDown()

        return self.passed(" case_174335--AddAllCartridgeToJbossEapApp passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AddAllCartridgeToJbossEapApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174335.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
