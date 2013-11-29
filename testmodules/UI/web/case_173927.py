#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_173927.py
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


class CheckPricingPageContent(OpenShiftTest):
    def test_method(self):
        web = self.config.web

       
        #check with invalid  password
        web.go_to_home()
        #web.click_element_by_xpath("//nav[@id='nav']/div/div/ul/li[4]/a/span")
        web.click_element_by_xpath("//a[@href='/community/developers']")
        web.click_element_by_xpath("//a[@href='/community/developers/pricing']")
        web.assert_text_equal_by_xpath('''Pricing''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')

        #check the plan summary
        web.assert_text_equal_by_xpath('''FreeShift\nGet started\nMegaShift\nGo Big\nFree\n$42/month\nFree Gears 3 3\nMax Gears 3 16\nGear Sizes\nAbout\nSmall Small, $0.05/hr\nMedium, $0.12/hr\nSupport\nAbout\nCommunity By Red Hat\nScaling\nAbout\nLimited to 3 Gears Included\nAdditional Storage\nAbout\nNo $1/GB per month\nSSL\nAbout\nShared For custom domains\nJava EE6 Full Profile & CDI\nAbout\nIncluded $0.03/hr additional''','''//div[@id='node-11187']/div/article/section''')

        #check the example part
        web.assert_text_equal_by_xpath('''Let's look at an example app running on OpenShift''','''//div[@id='node-11187']/div/article/section[2]/h3''')
        web.assert_text_equal_by_xpath('''What's a gear?\nA gear is a resource constrained container that runs one or more user-specified software stacks, also known as cartridges. Each gear has a limited amount of RAM and disk space. If an application needs more resources, it can use multiple gears.\nGears come in multiple sizes to suit the needs of various software stacks.\nLet's look at an example app running on OpenShift\nWe can estimate the needs and costs of the app at different stages.\nDrupal-based Site\nStandard Drupal 7 install with normal caching, mostly anonymous traffic, and a 2% update rate.\nEstimated costs assume the maximum number of gears running continuously, and include the platform fee where applicable but no add-ons.\nJust starting up\n15 pages/second\nHundreds of articles\n~ 50k visitors per month\nNeeds 3 small gears\nFree\nPretty popular\n45 pages/second\nThousands of articles\n~ 200k visitors per day\nScales up to 5 small gears\n$114/month\nMaking it Big\n120 pages/second\nTen thousand articles\n~ 15M visitors per month\nScales to 10 small gears\n$294/month''','''//div[@id='node-11187']/div/article/section[2]''')

        #check the FAQ part
        web.assert_text_equal_by_xpath('''FAQ\nWhat is the current status of OpenShift?\nWhat is Red Hat's plan with respect to OpenShift pricing?\nAre there different Gear sizes and how much do they cost?\nWhat are scaling threshold settings?\nDo you offer support?\nWhat is Add On Storage?\nWhat will happen to the free resources that were offered during the Developer Preview phase?\nHow do I get SSL for my domains?\nWhat is included with Java EE6 Full Profile & CDI?\nIf you have more questions, please refer to the OpenShift Pricing FAQ section in our OpenShift FAQ.''','''//div[@id='node-11187']/div/article/section[3]''')

       

        self.tearDown()

        return self.passed(" case_173927--CheckPricingPageContent passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckPricingPageContent)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_173927.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
