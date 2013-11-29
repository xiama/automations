#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138623.py
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


class CheckAppPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
        web.create_app("python-2.6","python")

        #check wether the links are correct
        time.sleep(20)
        #go to the app details page
        web.go_to_app_detail("python")

        #check the " add an SSH public key to your account" link
        web.click_element_by_xpath('''//section[@id='app-cartridges']/div/div/div/div/p/a''')
        web.assert_text_equal_by_xpath('''My Account''','''//div[@id='content']/div/div/div/div[2]/div/h1''')
        web.go_back()
        #check the "Enable Jenkins builds" link
        web.click_element_by_xpath('''//section[@id='app-cartridges']/div/div/div/div/div[2]/div/a''')
        web.assert_text_equal_by_xpath('''Enable Jenkins Builds''','''//div[@id='content']/div/div/div/div[2]/div/h1''')
        web.go_back()
        #check the "See the getting started tips for this app →" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul/li/a''')
        web.assert_text_equal_by_xpath('''GET STARTED''','''//div[@id='content']/div/div/div/div/div/nav/ul/li[3]''')
        web.go_back()

        #check the "OpenShift User Guide" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul[2]/li/a''')
        time.sleep(3)
        web.check_title("User Guide - Red Hat Customer Portal")
        web.go_back()
        #check the "Sync your OpenShift repo with an existing Git repo" link
        web.click_element_by_xpath('''//div[@id='assistance']/ul[2]/li[2]/a''')
        web.assert_text_equal_by_xpath('''Knowledge Base''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')
        web.go_back()
        #check the "Delete this application" link
        web.click_element_by_xpath('''//aside[@id='app-unique-info']/div[2]/a''')
        web.assert_text_equal_by_xpath('''Delete Application''','''//div[@id='content']/div/div/div/div[2]/div/h1''')
        web.go_back()
        #check the "Add Cartridge" link
        web.click_element_by_xpath('''//section[@id='app-cartridges']/div[2]/a/strong''')
        web.assert_text_equal_by_xpath('''ADD A CARTRIDGE''','''//div[@id='content']/div/div/div/div/div/nav/ul/li[3]''')
               
        #delete a python app
        web.delete_last_app("python")


        self.tearDown()

        return self.passed(" case_138623--CheckAppGetstartedPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckAppPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138623.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
