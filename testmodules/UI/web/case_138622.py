#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_138622.py
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


class CheckAppGetstartedPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
       
        #create a python app
        #web.create_app("python-2.6","python2")
        web.go_to_create_app("python-2.6")
        web.input_by_id("application_name", "python2")
        web.click_element_by_id("application_submit")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''') 

        #check wether the links are correct
        time.sleep(5)

        #check the "Git version control system" link
        web.assert_element_present_by_link_text("Git version control system")   
 
        #check the "Learn more about uploading code" link
        web.click_element_by_link_text("Learn more about uploading code")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''2.5. Editing and Deploying Applications''','''//h2[@id='sect-User_Guide-OpenShift_Web_Interface-Editing_and_Deploying_Applications']''')
        web.go_back()

        #check the "Add a cartridge" link
        web.click_element_by_link_text("Adding a cartridge")
        time.sleep(3)
        web.assert_text_equal_by_xpath('''ADD A CARTRIDGE''','''//div[@id='content']/div/div/div/div/div/nav/ul/li[3]''')
        web.go_back()

        #check the "Mysql" link
        web.click_element_by_link_text("MySQL")
        time.sleep(3)
        web.check_title("Add a Cartridge | OpenShift by Red Hat")
        web.go_back()

        #check the "MongoDB" link
        web.click_element_by_link_text("MongoDB")
        time.sleep(3)
        web.check_title("Add a Cartridge | OpenShift by Red Hat")
        web.go_back()

        #check the "Add a cartridge to your application now" link
        web.click_element_by_link_text("Add a cartridge to your application now")
        time.sleep(3)
        web.assert_text_equal_by_xpath('''ADD A CARTRIDGE''','''//div[@id='content']/div/div/div/div/div/nav/ul/li[3]''')
        web.go_back()

        #check the "Follow these steps to install the client" link
        web.click_element_by_link_text("Follow these steps to install the client")
        time.sleep(3)
        web.assert_text_equal_by_xpath('''Get Started with OpenShift''','''//div[@id='content']/div/div/div/div/div/h1''')
        web.go_back()

        #check the "on how to manage your application from the command line" link
        web.click_element_by_link_text("on how to manage your application from the command line")
        time.sleep(3)
        web.check_title("Chapter 3. OpenShift Command Line Interface - Red Hat Customer Portal")
        web.go_back()

        #check the "JBoss Developer Studio tools page." link
        web.click_element_by_link_text("JBoss Developer Studio tools page.")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''OpenShift Client Tools''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''',"Jboss Develop center is missing")
        web.go_back()

        #check the "application overview page" link
        web.click_element_by_link_text('''application overview page''')
        time.sleep(3)
        web.assert_text_equal_by_xpath('''PYTHON2''','''/html/body/div/div/div/div/div/div/nav/ul/li[2]/a''')
        web.go_back()
                      
        #delete a python app
        web.delete_last_app("python2")


        self.tearDown()

        return self.passed(" case_138622--CheckAppGetstartedPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckAppGetstartedPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_138622.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
