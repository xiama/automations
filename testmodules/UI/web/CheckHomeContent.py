#!/usr/bin/env python

#
#  File name: CheckHomeContent.py
#  Date:      2012/06/29 10:56
#  Author: mzimen@redhat.com   
#

import rhtest

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Demo01(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()
        #web.go_to_signin()
        #web.login()
        web.assert_text_equal_by_xpath('LEARN MORE',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[1]/a/span''')
        web.assert_text_equal_by_xpath('GET STARTED',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[2]/a/span''')
        web.assert_text_equal_by_xpath('DEVELOPERS',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[4]/a/span''')
        web.assert_text_equal_by_xpath('COMMUNITY',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[5]/a/span''')

        #check weather the links are correct
        #LEARN MORE
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[1]/a/span''')
        web.assert_text_equal_by_xpath('What is OpenShift?',
            '''/html/body/div[@id='content']/div/div/div/div/div/h1''',
            '`LEARN MORE` page is missing')

        #GET STARTED
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[2]/a/span''')
        web.assert_text_equal_by_xpath('Get Started with OpenShift',
            '''/html/body/div[@id='content']/div/div/div/div/div/h1''',
            'Get Started page is missing')

        #LOGO
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/div/a/div[1]''')
        web.assert_text_equal_by_xpath('BUZZ',
            '''/html/body/div[@id='buzz']/div/div/div/div/h2/strong''',
            'Check the Buzz part is missing')

        #DEVELOPERS
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[4]/a/span''')
        web.assert_text_equal_by_xpath('Developer Center',
            '''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div[1]''',
            'Developers page is missing')

        #COMMUNITY
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[5]/a/span''')
        web.assert_text_equal_by_xpath('Welcome to OpenShift',
            '''/html/body/div[@id='content']/div/div/div/div[3]/div/h1/div[1]''',
            'Community page is missing')

        self.tearDown()

        return self.passed("CheckHomeContent test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demo01)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of CheckHomeContent.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
