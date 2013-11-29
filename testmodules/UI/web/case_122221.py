#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122221.py
#  Date:      2012/06/29 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CheckHomeContent(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_home()
        #web.go_to_signin()
        #web.login()
        #Assert all the elements on home page (except for the footer).
        web.assert_text_equal_by_xpath('LEARN MORE',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[1]/a/span''')
        web.assert_text_equal_by_xpath('GET STARTED',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[2]/a/span''')
        web.assert_text_equal_by_xpath('DEVELOPERS',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[4]/a/span''')
        web.assert_text_equal_by_xpath('COMMUNITY',
            '''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[5]/a/span''')
        web.assert_text_equal_by_xpath('DEVELOP AND SCALE APPS IN THE CLOUD',
            '''//nav[@id='nav']/div[2]/div/h1''')
        web.assert_text_equal_by_xpath('''OpenShift is Red Hat's free, auto-scaling Platform as a Service (PaaS) for applications. As an application platform in the cloud, OpenShift manages the stack so you can focus on your code.''',
            '''//nav[@id='nav']/div[2]/div/h2''')
        web.assert_text_equal_by_xpath('GET STARTED IN THE CLOUD',
            '''//div[@id='learn']/div/div/a/div''')
        web.assert_text_equal_by_xpath('''SIGN UP - IT'S FREE''',
            '''//div[@id='learn']/div/div/a/div[2]''')
        web.assert_text_equal_by_xpath('Java, Ruby, Node.js, Python, PHP, or Perl',
            '''//div[@id='learn']/div/div/div/ul/li/a/h4''')
        web.assert_text_equal_by_xpath('Code in your favorite language, framework, and middleware. Grow your applications easily with resource scaling.','''//div[@id='learn']/div/div/div/ul/li/a/p''')
        web.assert_text_equal_by_xpath('Announcing the first tier of OpenShift pricing',
            '''//div[@id='learn']/div/div/div[2]/ul/li/a/h4''')
        web.assert_text_equal_by_xpath("We're announcing OpenShift pricing for the first paid tier offering, along with our plan to continue a free offering like the one that developers are currently enjoying in the OpenShift Developer Preview.",
            '''//div[@id='learn']/div/div/div[2]/ul/li/a/p''')
        web.assert_text_equal_by_xpath('Super Fast!',
            '''//div[@id='learn']/div/div/div/ul/li[2]/a/h4''')
        web.assert_text_equal_by_xpath('Code and deploy to the cloud in minutes. Faster and easier than it has ever been.',
            '''//div[@id='learn']/div/div/div/ul/li[2]/a/p''')
        web.assert_text_equal_by_xpath('Build your apps with JBoss EAP 6',
            '''//div[@id='learn']/div/div/div[2]/ul/li[2]/a/h4''')
        web.assert_text_equal_by_xpath('Market-leading open source enterprise platform for next-generation, highly transactional enterprise Java applications. Build and deploy enterprise Java on OpenShift!',
            '''//div[@id='learn']/div/div/div[2]/ul/li[2]/a/p''')
        web.assert_text_equal_by_xpath('No Lock-In',
            '''//div[@id='learn']/div/div/div/ul/li[3]/a/h4''')
        web.assert_text_equal_by_xpath('Built on open technologies so you can take it with you.',
            '''//div[@id='learn']/div/div/div/ul/li[3]/a/p''')
        web.assert_text_equal_by_xpath('Find answers in the Developer Center',
            '''//div[@id='learn']/div/div/div[2]/ul/li[3]/a/h4''')
        web.assert_text_equal_by_xpath('Building applications involves lots of questions and we want you to find those answers fast. The new Developer Center will centralize and organize all our reference material.',
            '''//div[@id='learn']/div/div/div[2]/ul/li[3]/a/p''')
        

        #check weather the links are correct
        #LEARN MORE
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[1]/a/span''')
        time.sleep(2)
        web.check_title("About the OpenShift Platform as a Service (PaaS) | OpenShift by Red Hat")

        #GET STARTED
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[2]/a/span''')
        web.check_title("Get Started with OpenShift | OpenShift by Red Hat")

        #LOGO
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/div/a/div[1]''')
        web.assert_text_equal_by_xpath('BUZZ',
            '''/html/body/div[@id='buzz']/div/div/div/div/h2/strong''',
            'Check the Buzz part is missing')

        #DEVELOPERS
        web.go_to_home()
        web.click_element_by_xpath('''/html/body/header/nav[@id='nav']/div[1]/div/ul/li[4]/a/span''')
        time.sleep(2)
        web.check_title("Developer Center | OpenShift by Red Hat")

        #COMMUNITY
        web.go_to_home()
        web.click_element_by_link_text("COMMUNITY")
        web.check_title("Welcome to OpenShift | OpenShift by Red Hat")

        #Other links
        web.go_to_home()
        web.click_element_by_xpath("//div[@id='learn']/div/div/div/ul/li/a/p")
        web.check_title("About the OpenShift Platform as a Service (PaaS) | OpenShift by Red Hat")

        web.go_to_home()
        web.click_element_by_xpath("//div[@id='learn']/div/div/div[2]/ul/li/a/p")
        web.check_title("Pricing | OpenShift by Red Hat")

        web.go_to_home()
        web.click_element_by_xpath("//div[@id='learn']/div/div/div/ul/li[2]/a/p")
        web.check_title("About the OpenShift Platform as a Service (PaaS) | OpenShift by Red Hat")

        web.go_to_home()
        web.click_element_by_xpath("//div[@id='learn']/div/div/div/ul/li[3]/a/p")
        web.check_title("About the OpenShift Platform as a Service (PaaS) | OpenShift by Red Hat")

        web.go_to_home()
        web.click_element_by_xpath("//div[@id='learn']/div/div/div[2]/ul/li[3]/a/p")
        web.check_title("Developer Center | OpenShift by Red Hat")
        self.tearDown()

        return self.passed("Case 122221 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckHomeContent)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122221.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
