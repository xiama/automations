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


class CheckCommunityLink(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_community()
        time.sleep(5)
        
        #Assert all the links of Community page.
        web.assert_text_equal_by_xpath('Overview',
            '''//div[@id='block-menu_block-1']/div/div/ul/li/a''')
        web.assert_text_equal_by_xpath('Blog',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('Forum',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[3]/a''')
        web.assert_text_equal_by_xpath('Vote on Features',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[4]/a''')
        web.assert_text_equal_by_xpath('Get Involved',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[5]/a''')
        web.assert_text_equal_by_xpath('Open Source',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[5]/ul/li/a''')
        web.assert_text_equal_by_xpath('Get the Bits',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[5]/ul/li[2]/a''')
        web.assert_text_equal_by_xpath('Events',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[6]/a''')
        web.assert_text_equal_by_xpath('Videos',
            '''//div[@id='block-menu_block-1']/div/div/ul/li[7]/a''')
        
        
      
        #Check all the links of Community page.
        #Overview
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Welcome to OpenShift',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Overview link is broken')

        #Blog
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[2]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Blogs',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Blog link is broken')

        #Forum
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[3]/a''')
        web.assert_text_equal_by_xpath('Forums',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Forum link is broken')

        #Vote on Features
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[4]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Vote on Features',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Vote on Features link is broken')

        #Get Involved
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[5]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Get Involved',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Get Involved link is broken')

        #Open Source
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[5]/ul/li/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('OpenShift is Open Source',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Open Source link is broken')

        #Get the Bits
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[5]/ul/li[2]/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('OpenShift Origin Source Code',
            '''//div[@id='content']/div/div/div/div/div/h1''',
            'Get the bits link is broken')

        #Events
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[6]/a''')
        time.sleep(2)
        web.assert_text_equal_by_xpath('Events',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Events link is broken')
       
        #Videos
        web.go_to_community()
        web.click_element_by_xpath('''//div[@id='block-menu_block-1']/div/div/ul/li[7]/a''')
        time.sleep(5)
        web.assert_text_equal_by_xpath('Videos',
            '''//div[@id='content']/div/div/div/div[3]/div/h1/div''',
            'Videos link is broken')

        self.tearDown()

        return self.passed("Case 141708 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckCommunityLink)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_141708.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
