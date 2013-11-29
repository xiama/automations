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

        web.login()
        #web.delete_app("ruby19")
        #create a ruby1.9 app
        web.create_app("jbosseap-6.0","jbosseap")
     
        #check the "appurl" link
        #web.click_element_by_xpath('''//div[@id='content']/div/div/div/div[2]/div/section[2]/div/p[2]/a''')
        #web.assert_text_equal_by_xpath("OpenShift by Red Hat",'''//title''')  

        web.go_to_app_detail("jbosseap")
        web.click_element_by_xpath('''//div[@id='content']/div/div/div/div[2]/nav/div/a''')
        web.assert_text_equal_by_xpath("Welcome To OpenShift, JBossEAP6.0 Cartridge",'''//h1''')  

        #delete a python app
        web.go_to_app_detail("jbosseap")
        time.sleep(2)
        web.click_element_by_link_text("Delete this application")
        time.sleep(1)
        web.click_element_by_id("application_submit")
        time.sleep(40)
        web.go_to_app_detail("jbosseap")
        web.assert_text_equal_by_xpath("Sorry, but the page you were trying to view does not exist.", '''//article/div/p''')


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
