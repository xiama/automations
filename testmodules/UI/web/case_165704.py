#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_165704.py
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


class CheckGetInvolvedPage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        #web.go_to_home()
        web.go_to_community()
        web.click_element_by_xpath('''//a[contains(@href, '/community/get-involved')]''')
        time.sleep(2)

        #check the "OpenShift" link 
        web.assert_text_equal_by_xpath("OpenShift",'''//div[@id='node-9465']/div/p[2]/a''')
        web.click_element_by_link_text("OpenShift")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift is Red Hat's free, auto-scaling Platform as a Service (PaaS) for applications. As an application platform in the cloud, OpenShift manages the stack so you can focus on your code.''','''//body/header/nav/div[2]/div/h2''') 
        web.go_back() 
        #check the " OpenShift Origin LiveCD" link 
        web.assert_text_equal_by_xpath("OpenShift Origin LiveCD",'''//div[@id='node-9465']/div/p[2]/a[2]''')
        web.click_element_by_link_text("OpenShift Origin LiveCD")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift Origin Source Code''','''//div[@id='content']/div/div/div/div/div/h1''')   
        web.go_back()
        #check the " examples and quickstarts." link 
        web.assert_text_equal_by_xpath("examples and quickstarts",'''//div[@id='node-9465']/div/p[3]/a''')
        web.click_element_by_link_text("examples and quickstarts")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Get Started on OpenShift''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "DIY application " link 
        web.assert_text_equal_by_xpath("DIY application",'''//div[@id='node-9465']/div/p[4]/a''')
        web.click_element_by_link_text("DIY application")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''A PaaS that runs anything HTTP: Getting Started with DIY Applications on OpenShift''','''//div[@id='content']/div/div/div/div[3]/div/section/article/h1''')   
        web.go_back() 
        #check the " Tweet " ,"Facebook" and " Google+." link 
        web.assert_text_equal_by_xpath("Tweet",'''////a[contains(@href, 'https://twitter.com/#!/openshift')]''')
        web.assert_text_equal_by_xpath("Facebook",'''//a[contains(@href, 'https://www.facebook.com/openshift')]''')
        web.assert_text_equal_by_xpath("Google+",'''//a[contains(@href, 'https://plus.google.com/108052331678796731786/posts')]''')

        #check the "forums" link 
        web.assert_text_equal_by_xpath("forums",'''//div[@id='node-9465']/div/p[6]/a''')
        web.click_element_by_link_text("forums")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Forums''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back() 
        #check the "IRC " link 
        web.assert_text_equal_by_xpath("IRC",'''//div[@id='node-9465']/div/p[6]/a[2]''')
        web.click_element_by_link_text("IRC")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Connect to freenode IRC''','''//body/div/div[2]/table/tbody/tr/td/table/tbody/tr/td/h1''')   
        web.go_back() 



        #check the "report bugs" link 
        web.assert_text_equal_by_xpath("report bugs",'''//div[@id='node-9465']/div/p[7]/a''')
        web.assert_text_equal_by_xpath("report bugs",'''//a[contains(@href, 'https://bugzilla.redhat.com/enter_bug.cgi?product=OpenShift')]''')
        web.go_back() 
        #check the "suggest or vote on new features" link 
        web.assert_text_equal_by_xpath("suggest or vote on new features",'''//div[@id='node-9465']/div/p[7]/a[2]''')
        web.click_element_by_link_text("suggest or vote on new features")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Vote on Features''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')    
        web.go_back() 
        #check the "fix bugs" link 
        web.assert_text_equal_by_xpath("fix bugs",'''//div[@id='node-9465']/div/p[8]/a''')
        web.assert_text_equal_by_xpath("fix bugs",'''//a[contains(@href, 'https://bugzilla.redhat.com/buglist.cgi?query_format=specific&order=relevance+desc&bug_status=__open__&product=OpenShift')]''')
        #check the "contribute patches" link 
        web.assert_text_equal_by_xpath("contribute patches",'''//div[@id='node-9465']/div/p[8]/a[2]''')
        web.click_element_by_link_text("contribute patches")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''GitHub workflow for submitting pull requests''','''//div[@id='content']/div/div/div/div[3]/div/section/div[2]/h2''')   
        web.go_back() 
        #check the " write sample applications and quickstarts " link 
        web.assert_text_equal_by_xpath("write sample applications and quickstarts",'''//div[@id='node-9465']/div/p[9]/a''')
        web.click_element_by_link_text("write sample applications and quickstarts")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''How to create an OpenShift github quick start project''','''//div[@id='content']/div/div/div/div[3]/div/section/article/h1''')   
        web.go_back() 

 

       




        self.tearDown()

        return self.passed(" case_165704--CheckGetInvolvedPage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckGetInvolvedPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_165704.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
