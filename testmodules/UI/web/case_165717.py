#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_165717.py
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


class CheckOpensourcePage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        #web.go_to_home()
        web.go_to_community()
        web.click_element_by_xpath('''//a[contains(@href, '/community/open-source')]''')
        time.sleep(2)

        #check the "OpenShift" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/p/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''BUZZ''','''//body/div[2]/div/div/div/div/h2/strong''')
        web.go_back() 
        #check the "architecture-overview" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Architecture Overview''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()  
        #check the "Community Process" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[2]/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Community Process''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')     
        web.go_back()  
        #check the "OpenShift Origin" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[2]/li[2]/a''')
        time.sleep(2)
        web.check_title("Browse:")        
        web.go_back()  
        #check the "Project Bug Reporting" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[2]/li[3]/a''')
        time.sleep(2)
        web.check_title("Log in to Red Hat Bugzilla")        
        web.go_back()  
        #check the "Git-hub" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[2]/li[4]/a''')
        time.sleep(4)
        web.assert_text_equal_by_xpath('''openshift''','''//body/div/div[2]/div/div/div/h1/span''')  
        web.go_back()
        time.sleep(2)
        #check the "Invitation for public review process for Cartridges" link 
        web.assert_text_equal_by_xpath("Invitation for public review process for Cartridges",'''//div[@id='node-9475']/div/ul[3]/li/a''')
        web.click_element_by_link_text("Invitation for public review process for Cartridges")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Invitation for public review process for Cartridges''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Workflow for Cartridge review and inclusion" link 
        web.assert_text_equal_by_xpath("Workflow for Cartridge review and inclusion",'''//div[@id='node-9475']/div/ul[3]/li[2]/a''')
        web.assert_text_equal_by_xpath("Workflow for Cartridge review and inclusion",'''//a[contains(@href, '/community/node/add/wiki_page?edit[title]=Workflow+for+Cartridge+review+and+inclusion')]''')




        #check the "Getting started with Openshift Origin LiveCD" link 
        web.assert_text_equal_by_xpath("Getting started with Openshift Origin LiveCD",'''//div[@id='node-9475']/div/ul[4]/li/a''')
        web.click_element_by_link_text("Getting started with Openshift Origin LiveCD")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Getting started with Openshift Origin LiveCD''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the " Build Your Own Paas from the OpenShift Origin LiveCD using liveinst " link 
        web.assert_text_equal_by_xpath("Build Your Own Paas from the OpenShift Origin LiveCD using liveinst",'''//div[@id='node-9475']/div/ul[4]/li[2]/a''')
        web.click_element_by_link_text("Build Your Own Paas from the OpenShift Origin LiveCD using liveinst")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own Paas from the OpenShift Origin LiveCD using liveinst''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Connect to Openshift Origin installation with JBoss Tools" link 
        web.assert_text_equal_by_xpath("Connect to Openshift Origin installation with JBoss Tools",'''//div[@id='node-9475']/div/ul[4]/li[3]/a''')
        web.click_element_by_link_text("Connect to Openshift Origin installation with JBoss Tools")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Connect to Openshift Origin installation with JBoss Tools''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Rebuild Openshift Origin Packages" link 
        web.assert_text_equal_by_xpath("Rebuild Openshift Origin Packages",'''//div[@id='node-9475']/div/ul[4]/li[4]/a''')
        web.click_element_by_link_text("Rebuild Openshift Origin Packages")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Rebuild Openshift Origin Packages''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Build Your Own PaaS" link 
        web.assert_text_equal_by_xpath("Build Your Own PaaS",'''//div[@id='node-9475']/div/ul[4]/li[5]/a''')
        web.click_element_by_link_text("Build Your Own PaaS")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Your Own PaaS''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Build Multi-node PaaS from scratch" link 
        web.assert_text_equal_by_xpath("Build Multi-node PaaS from scratch",'''//div[@id='node-9475']/div/ul[4]/li[6]/a''')
        web.click_element_by_link_text("Build Multi-node PaaS from scratch")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Build Multi-node PaaS from scratch''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Local Dynamic DNS Service" link 
        web.assert_text_equal_by_xpath("Local Dynamic DNS Service",'''//div[@id='node-9475']/div/ul[4]/li[7]/a''')
        web.click_element_by_link_text("Local Dynamic DNS Service")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Local Dynamic DNS Service''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "Introduction to Cartridge Building" link 
        web.assert_text_equal_by_xpath("Introduction to Cartridge Building",'''//div[@id='node-9475']/div/ul[4]/li[8]/a''')
        web.click_element_by_link_text("Introduction to Cartridge Building")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Introduction to Cartridge Building''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        #check the "GitHub workflow for submitting pull requests" link 
        web.assert_text_equal_by_xpath("GitHub workflow for submitting pull requests",'''//div[@id='node-9475']/div/ul[4]/li[9]/a''')
        web.click_element_by_link_text("GitHub workflow for submitting pull requests")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''GitHub workflow for submitting pull requests''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()




        #check the "Mailing Lists" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Below is a listing of all the public mailing lists on lists.openshift.redhat.com. Click on a list name to get more information about the list, or to subscribe, unsubscribe, and change the preferences on your subscription. To visit the general information page for an unadvertised list, open a URL similar to this one, but with a '/' and the list name appended.''','''//body/table/tbody/tr[2]/td/p''')  
        web.go_back()
        time.sleep(2)
        #check the "For Developers" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''dev -- Developer discussions around OpenShift and OpenShift Origin''','''//body/p/table/tbody/tr/td/b/font''')  
        web.go_back()
        time.sleep(2)
        #check the "For Users" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''users -- User discussions around OpenShift and OpenShift Origin''','''//body/p/table/tbody/tr/td/b/font''') 
        web.go_back()
        time.sleep(2)
        #check the "Community Forums" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Recent Threads''','''//div[@id='content']/div/div/div/div[3]/div/section/h3''')  
        web.go_back()
        time.sleep(2)
        #check the "Community Blogs" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li[3]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Blogs''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')  
        web.go_back()
        time.sleep(2)
        #check the "#openshift on the irc.freenode.net IRC server" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li[4]/a''')
        time.sleep(2)
        web.check_title('''Connection details - freenode Web IRC''')
        web.go_back()
        time.sleep(2)
        #check the "#openshift-dev on the irc.freenode.net IRC server" link 
        web.click_element_by_xpath('''//div[@id='node-9475']/div/ul[5]/li[5]/a''')
        time.sleep(2)
        web.check_title('''Connection details - freenode Web IRC''')
        web.go_back()
        time.sleep(2)




        #check the "FAQ: Frequently Asked Questions" link 
        web.assert_text_equal_by_xpath("FAQ: Frequently Asked Questions",'''//div[@id='node-9475']/div/ul[6]/li/a''')
        web.click_element_by_link_text("FAQ: Frequently Asked Questions")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''FAQ: Frequently Asked Questions''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back()
        




        self.tearDown()

        return self.passed(" case_165717--CheckOpensourcePage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckOpensourcePage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_165717.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
