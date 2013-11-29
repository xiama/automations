#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_165723.py
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


class CheckWikiIndexPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        #web.go_to_home()
        web.go_to_community()
        web.click_element_by_xpath('''//a[contains(@href, '/community/open-source')]''')
        web.click_element_by_xpath('''//a[contains(@href, '/community/wiki/index')]''')
        time.sleep(2)

        #check the "architecture-overview" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[2]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Architecture Overview''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()  
        #check the "Build Multi-node PaaS from scratch" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[3]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Multi-node PaaS from scratch''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Build Your Own PaaS" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[4]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own PaaS''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Build Your Own Paas from the OpenShift Origin LiveCD using liveinst" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[5]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own Paas from the OpenShift Origin LiveCD using liveinst''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Build Your Own PaaS: Base Operating System and Configuration" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[6]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own PaaS: Base Operating System and Configuration''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Build Your Own PaaS: Installing the Broker" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[7]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own PaaS: Installing the Broker''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "build-your-own" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[8]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''build-your-own''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Build-your-own/prepare-the-base-os" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[9]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build-your-own/prepare-the-base-os''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Community Process" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[10]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Community Process''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "Connect to Openshift Origin installation with JBoss Tools" link 
        web.click_element_by_xpath('''//div[@id='node-9485']/div/table/tbody/tr[11]/td/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Connect to Openshift Origin installation with JBoss Tools''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  

        self.tearDown()

        return self.passed(" case_165723--CheckWikiIndexPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckWikiIndexPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_165723.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
