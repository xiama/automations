#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_173928.py
#  Date:      2012/08/07 13:23
#  Author: mgao@redhat.com   
#

import rhtest
import time


class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckPricingPageLayout(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        web.go_to_home()
        #web.click_element_by_xpath("//nav[@id='nav']/div/div/ul/li[4]/a/span")
        web.click_element_by_xpath("//a[@href='/community/developers']")
        web.click_element_by_xpath("//a[@href='/community/developers/pricing']")
        web.assert_text_equal_by_xpath('''Pricing''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')

        web.assert_text_equal_by_xpath('''Our free Developer Preview version of OpenShift is currently available. We are planning to expand the OpenShift offering to provide users the ability to purchase increased capacity, functionality and support. The details below provide our pricing plans, which may be subject to change as we continue to fine tune the offering to address our customers needs. Sign up for the Developer Preview.''','''//div[@id='node-11187']/div/article/p''')
        
        #check the example part
        web.assert_text_equal_by_xpath('''What's a gear?''','''//div[@id='node-11187']/div/article/section[2]/h2''')
        web.assert_text_equal_by_xpath('''A gear is a resource constrained container that runs one or more user-specified software stacks, also known as cartridges. Each gear has a limited amount of RAM and disk space. If an application needs more resources, it can use multiple gears.''','''//div[@id='node-11187']/div/article/section[2]/div/div/p''')
        web.assert_text_equal_by_xpath('''Gears come in multiple sizes to suit the needs of various software stacks.''','''//div[@id='node-11187']/div/article/section[2]/div/div/p[2]''')
        web.assert_text_equal_by_xpath('''Let's look at an example app running on OpenShift''','''//div[@id='node-11187']/div/article/section[2]/h3''')
        web.assert_text_equal_by_xpath('''We can estimate the needs and costs of the app at different stages.''','''//div[@id='node-11187']/div/article/section[2]/p''')
        web.assert_text_equal_by_xpath('''Drupal-based Site''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div/h3''')
        web.assert_text_equal_by_xpath('''Standard Drupal 7 install with normal caching, mostly anonymous traffic, and a 2% update rate.''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div/p''')
        web.assert_text_equal_by_xpath('''Estimated costs assume the maximum number of gears running continuously, and include the platform fee where applicable but no add-ons.''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div/p[2]''')
        web.assert_text_equal_by_xpath('''Just starting up''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div[2]/h3''')
        web.assert_text_equal_by_xpath('''Pretty popular''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div[3]/h3''')
        web.assert_text_equal_by_xpath('''Making it Big''','''//div[@id='node-11187']/div/article/section[2]/div[2]/div[4]/h3''')

        #check the FAQ part
        web.click_element_by_link_text('''What is the current status of OpenShift?''')
        time.sleep(2)
        web.check_title("What is the current status of OpenShift? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''What is Red Hat's plan with respect to OpenShift pricing?''')
        time.sleep(2)
        web.check_title("What is Red Hat's plan with respect to OpenShift pricing? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''Are there different Gear sizes and how much do they cost?''')
        time.sleep(2)
        web.check_title("Are there different gear sizes and how much do they cost? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''What are scaling threshold settings?''')
        time.sleep(2)
        web.check_title("What are scaling threshold settings? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''Do you offer support?''')
        time.sleep(2)
        web.check_title("Do you offer support? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''What is Add On Storage?''')
        time.sleep(2)
        web.check_title("What is Add On Storage? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''What will happen to the free resources that were offered during the Developer Preview phase?''')
        time.sleep(2)
        web.check_title("What will happen to the free resources that were offered during the Developer Preview phase? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''How do I get SSL for my domains?''')
        time.sleep(2)
        web.check_title("How do I get SSL for my domains? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''What is included with Java EE6 Full Profile & CDI?''')
        time.sleep(2)
        web.check_title("What is included with Java EE6 Full Profile & CDI? | OpenShift by Red Hat")
        web.go_back()
        time.sleep(2)

        web.click_element_by_link_text('''OpenShift FAQ''')
        time.sleep(2)
        web.check_title("Frequently Asked Questions | OpenShift by Red Hat")             
        web.go_back()
        time.sleep(2)

        self.tearDown()

        return self.passed(" case_173928--CheckPricingPageLayout passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckPricingPageLayout)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_173928.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
