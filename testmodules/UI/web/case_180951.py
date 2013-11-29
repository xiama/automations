#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180951.py
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


class AddAllCartridgeTospringeap(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        #web.create_app("springeap6","springeap")
        web.go_to_create_app("springeap6")
        web.input_by_id("application_name", "springeap")
        web.click_element_by_id("application_submit")
        time.sleep(40)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')

        
        #go to app springeap page and add cartridges
        web.add_cartridge("springeap", "mongodb-2.2")
        time.sleep(8)
        web.assert_text_equal_by_xpath("rhc app cartridge remove -a springeap -c mongodb-2.2",'''//pre[3]''')  

        web.add_cartridge("springeap", "cron-1.4")
        web.assert_text_equal_by_xpath("Cron 1.4",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("springeap", "mysql-5.1")
        web.assert_text_equal_by_xpath("rhc app cartridge remove -a springeap -c mysql-5.1",'''//pre[3]''') 

        web.add_cartridge("springeap","metrics-0.1")
        web.assert_text_equal_by_xpath("OpenShift Metrics 0.1",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("springeap","phpmyadmin-3.4")
        web.assert_text_equal_by_xpath("phpMyAdmin 3.4",'''//div[@id='cartridge_type_']/h3''')

        web.add_cartridge("springeap","rockmongo-1.1")
        web.assert_text_equal_by_xpath("rhc app cartridge remove -a springeap -c rockmongo-1.1",'''//pre[3]''') 

        web.go_to_app_detail("springeap")
        web.click_element_by_xpath('''//a[contains(@href, '/building')]''')
        web.input_by_id("application_name", "jenkins")
        web.click_element_by_id("application_submit")
        time.sleep(150)  
        web.assert_text_equal_by_xpath("Building your Application",'''//div[@id='content']/div/div/div/div[2]/div/h1''')


        #delete a springeap app
        web.delete_app("springeap")
        #delete a jenkins app
        web.delete_last_app("jenkins")


        self.tearDown()

        return self.passed(" case_180951--AddAllCartridgeTospringeap passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AddAllCartridgeTospringeap)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_180951.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
