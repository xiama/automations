#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122222.py
#  Date:      2012/07/03 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckHomeFooter(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()
        
        #Assert all the elements of footer 
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

        #check all the links of footer
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
        #web.go_to_home()
        #web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/ul/li[2]/a''')
        #time.sleep(2)
        #web.assert_text_equal_by_xpath('User Guide',
         #   '''//div[@id='id1407351']/div/div/div[2]/h1''',
          #  'User Guide is missing')

        #FAQ
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav/ul/li[3]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Frequently Asked Questions',
            '''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div''','FAQ is missing')

        #Pricing
        web.go_to_home()
        web.click_element_by_xpath("//div[@id='footer-nav']/div/div/nav/ul/li[4]/a")
        time.sleep(2)
        web.assert_text_equal_by_xpath('Pricing','''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div''','Get Started page is missing')

        #COMMUNITY
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/header/h3/a''')
        web.sleep(5)
        web.assert_text_equal_by_xpath('Welcome to OpenShift',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div[1]''',
            'Community page is missing')

        #Blog
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift Blog',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Blog page is missing')

        #Forum
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Forums',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Forums page is missing')
       
        #IRC Channel
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[2]/ul/li[3]/a''')
        time.sleep(5)
        web.check_title("Connection details - freenode Web IRC")



        #GET INVOLVED
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/header/h3/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Get Involved',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Get Involved page is missing')
       
        #Open Source
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('OpenShift is Open Source',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Open Source page is missing')
        
        #Make it better
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Get Involved with OpenShift',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Get Involved with Openshift page is missing')

        #OpenShift on GitHub
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li[3]/a''')
        time.sleep(2)
        web.assert_element_present_by_link_text("crankcase")

        #Newsletter Sign Up
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[3]/ul/li[4]/a''')
        time.sleep(2)
        web.check_title("OpenShift Newsletter Signup")
 
        #ACCOUNT
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/header/h3/a''')
        time.sleep(2)
        web.check_title("Sign in to OpenShift | OpenShift by Red Hat")
        
        #Terms of service
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li/a''')
        time.sleep(2)
        web.check_title("Terms of Use | OpenShift by Red Hat")

        #Privacy Policy
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[2]/a''')
        time.sleep(2)
        web.check_title("OpenShift Privacy Statement | OpenShift by Red Hat")

        #Security Policy
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[3]/a''')
        time.sleep(5)
        web.check_title("Security Information | OpenShift by Red Hat")

        #Plans
        web.go_to_home()
        web.click_element_by_xpath('''//div[@id='footer-nav']/div/div/nav[4]/ul/li[4]/a''')
        time.sleep(5)
        web.check_title("Pricing | OpenShift by Red Hat")

        self.tearDown()

        return self.passed("Case 122222 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckHomeFooter)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of CheckHomeContent.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
