#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_141707.py
#  Date:      2012/07/04 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckCommunityHeaderFooter(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_community()
        time.sleep(5)
        
        #Assert the header of Community page.
        web.assert_text_equal_by_xpath('JOIN THE OPENSHIFT COMMUNITY',
            '''//div[@id='nav']/div[2]/div/div''')
        web.assert_text_equal_by_xpath('This is the place to learn and engage with OpenShift users and developers. Sign in to participate',
            '''//div[@id='nav']/div[2]/div/div[2]''')

        #Assert all the elements of footer on Community page. 
        web.assert_text_equal_by_xpath('DEVELOPERS',
            '''//div[@id='footer-nav']/div/div/nav/header/h3/a''')
        web.assert_text_equal_by_xpath('Get Started',
            '''//div[@id='footer-nav']/div/div/nav/ul/li/a''')
        web.assert_text_equal_by_xpath('User Guide',
            '''//div[@id='footer-nav']/div/div/nav/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('FAQ',
            '''//div[@id='footer-nav']/div/div/nav/ul/li[3]/a''')
        web.assert_text_equal_by_xpath('Pricing',
            '''//div[@id='footer-nav']/div/div/nav/ul/li[4]/a''')
        web.assert_text_equal_by_xpath('''COMMUNITY''',
            '''//div[@id='footer-nav']/div/div/nav[2]/header/h3/a''')
        web.assert_text_equal_by_xpath('Blog',
            '''//div[@id='footer-nav']/div/div/nav[2]/ul/li/a''')
        web.assert_text_equal_by_xpath('''Forum''',
            '''//div[@id='footer-nav']/div/div/nav[2]/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('IRC Channel',
            '''//div[@id='footer-nav']/div/div/nav[2]/ul/li[3]/a''')
        web.assert_text_equal_by_xpath('Feedback',
            '''//div[@id='footer-nav']/div/div/nav[2]/ul/li[4]/a''')
        web.assert_text_equal_by_xpath('GET INVOLVED',
            '''//div[@id='footer-nav']/div/div/nav[3]/header/h3/a''')
        web.assert_text_equal_by_xpath('Open Source',
            '''//div[@id='footer-nav']/div/div/nav[3]/ul/li/a''')
        web.assert_text_equal_by_xpath('Make it Better',
            '''//div[@id='footer-nav']/div/div/nav[3]/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('OpenShift on GitHub',
            '''//div[@id='footer-nav']/div/div/nav[3]/ul/li[3]/a''')
        web.assert_text_equal_by_xpath('Newsletter sign up',
            '''//div[@id='footer-nav']/div/div/nav[3]/ul/li[4]/a''')
        web.assert_text_equal_by_xpath('''ACCOUNT''',
            '''//div[@id='footer-nav']/div/div/nav[4]/header/h3/a''')
        web.assert_text_equal_by_xpath('Terms of Service',
            '''//div[@id='footer-nav']/div/div/nav[4]/ul/li/a''')
        web.assert_text_equal_by_xpath('Privacy Policy',
            '''//div[@id='footer-nav']/div/div/nav[4]/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('Security Policy',
            '''//div[@id='footer-nav']/div/div/nav[4]/ul/li[3]/a''') 
        web.assert_text_equal_by_xpath('Plans',
            '''//div[@id='footer-nav']/div/div/nav[4]/ul/li[4]/a''')

        #check all the links of footer on Community page.
         #DEVELOPERS
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/header/h3/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Developer Center',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Developers page is missing')

        #GET STARTED
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Get Started with OpenShift',
            '''/html/body/div[@id='content']/div/div/div/div/div/h1''',
            '`LEARN MORE` page is missing')



        #User Guide
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/ul/li[2]/a''')
        time.sleep(2)
        web.check_title("User Guide - Red Hat Customer Portal")

        #FAQ
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/ul/li[3]/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('Frequently Asked Questions',
            '''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div''','FAQ is missing')

        #Pricing
        web.go_to_community()
        web.click_element_by_xpath("//div[@id='footer-nav']/div/div/nav/ul/li[4]/a")
        time.sleep(2)
        web.assert_text_equal_by_xpath('Pricing','''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div''','Get Started page is missing')

        #COMMUNITY
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/header/h3/a''')
        web.sleep(5)
        web.assert_text_equal_by_xpath('Welcome to OpenShift',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div[1]''',
            'Community page is missing')

        #Blog
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift Blog',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Blog page is missing')

        #Forum
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Forums',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Forums page is missing')
       
        #IRC Channel
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li[3]/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('''To connect to freenode IRC and join channel #openshift click 'Connect'.''',
            '''//div[@id='ircui']/div[3]/table/tbody/tr/td/form/table/tbody/tr/td''',
            'IRC Channel page is missing')

        #GET INVOLVED
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/header/h3/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Get Involved',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Get Involved page is missing')
       
        #Open Source
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift is Open Source',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Open Source page is missing')

        #Make it better
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li[2]/a''')
        time.sleep(2)
        web.check_title("Get Involved with OpenShift | OpenShift by Red Hat")

        #OpenShift on GitHub
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li[3]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('openshift',
            '''//div[@id='site-container']/div/div/h1/span''',
            'GitHub page is missing')
 
        #ACCOUNT
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/header/h3/a''')
        time.sleep(2)
        web.check_title("Sign in to OpenShift | OpenShift by Red Hat")
        
        #Terms of service
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift Preview Services Agreement',
            '''//div[@id='content']/div/div/div/div/div/h1''',
            'Terms of Use page is missing')

        #Privacy Policy
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift Privacy Statement',
            '''//div[@id='content']/div/div/div/div/div/h1''',
            'Privacy Policy page is missing')

        #Security Policy
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[3]/a''')
        time.sleep(5)
        web.check_title("Security Information | OpenShift by Red Hat")

        #Plans
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[4]/a''')
        time.sleep(5)
        web.check_title("Pricing | OpenShift by Red Hat")

        self.tearDown()

        return self.passed("Case 141707 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckCommunityHeaderFooter)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_141707.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
