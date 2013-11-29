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

        web.login()

        web.create_app("python-2.6","python")
        web.click_element_by_xpath('''//a[contains(@href, '/app/console/help')]''')
        time.sleep(2)

        #check the "Create an app now" link 
        web.assert_text_equal_by_xpath("Create an app now",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[3]/a''')
        web.click_element_by_link_text("Create an app now")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''cartridges''','''//div[@id='content']/div/div/div/div[2]/div/section/p/strong''')   
        web.go_back()
        #check the "our Getting Started page" link 
        web.assert_text_equal_by_xpath("our Getting Started page",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[4]/a''')
        web.click_element_by_link_text("our Getting Started page")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Get Started with OpenShift''','''//div[@id='content']/div/div/div/div/div/h1''')   
        web.go_back()
        #check the "Get Started Fast page" link 
        web.assert_text_equal_by_xpath("Get Started Fast page",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[5]/a''')
        web.click_element_by_link_text("Get Started Fast page")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Get Started on OpenShift''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "Ruby on Rails" link 
        web.assert_text_equal_by_xpath("Ruby on Rails",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[5]/a[3]''')
        web.click_element_by_link_text("Ruby on Rails")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''rails-example''','''//body/div/div[2]/div/div/div/h1/strong/a''')   
        web.go_back()
        #check the "Drupal" link 
        web.assert_text_equal_by_xpath("Drupal",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[5]/a[2]''')
        web.click_element_by_link_text("Drupal")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''drupal-example''','''//body/div/div[2]/div/div/div/h1/strong/a''') 
        web.go_back()
        #check the "Wordpress" link 
        web.assert_text_equal_by_xpath("Wordpress",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[5]/a[4]''')
        web.click_element_by_link_text("Wordpress")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''wordpress-example''','''//body/div/div[2]/div/div/div/h1/strong/a''') 
        web.go_back()
        #check the "let us know" link 
        web.assert_text_equal_by_xpath("let us know",'''//div[@id='content']/div/div/div/div[2]/div/section/div/p[5]/a[5]''')
        web.assert_text_equal_by_xpath("let us know",'''//a[contains(@href, 'mailto:openshift@redhat.com')]''')

        #check the "The Developer Center" link 
        web.assert_text_equal_by_xpath("The Developer Center",'''//div[@id='content']/div/div/div/div[2]/div/section/div[2]/p[2]/a''')
        web.click_element_by_link_text("The Developer Center")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Developer Center''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "the User Guide" link 
        web.assert_text_equal_by_xpath("the User Guide",'''//div[@id='content']/div/div/div/div[2]/div/section/div[2]/p[3]/a''')
        web.click_element_by_link_text("the User Guide")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''User Guide''','''//div[@id='id2789633']/div/div/div[2]/h1''')   
        web.go_back()
        #check the "JBoss" link 
        web.assert_text_equal_by_xpath("JBoss",'''//div[@id='content']/div/div/div/div[2]/div/section/div[2]/p[4]/a''')
        web.click_element_by_link_text("JBoss")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift Resources for JBoss''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "MongoDB" link 
        web.assert_text_equal_by_xpath("MongoDB",'''//div[@id='content']/div/div/div/div[2]/div/section/div[2]/p[4]/a[2]''')
        web.click_element_by_link_text("MongoDB")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Building with MongoDB''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "see our Videos page" link 
        web.assert_text_equal_by_xpath("see our Videos page",'''//div[@id='content']/div/div/div/div[2]/div/section/div[2]/p[5]/a''')
        web.click_element_by_link_text("see our Videos page")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Videos''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()







        #check the "community forum" link 
        web.assert_text_equal_by_xpath("community forum",'''//div[@id='content']/div/div/div/div[2]/div/section/div[3]/p[2]/a''')
        web.click_element_by_link_text("community forum")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Forums''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "search" link 
        web.click_element_by_xpath("//div[@id='content']/div/div/div/div[2]/div/section/div[3]/form/button")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Search''','''//div[@id='content']/div/div/div/div/div/h1/div''')   
        web.go_back()
        #check the "Knowledge Base" link 
        web.assert_text_equal_by_xpath("Knowledge Base",'''//div[@id='content']/div/div/div/div[2]/div/section/div[3]/p[3]/a''')
        web.click_element_by_link_text("Knowledge Base")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Knowledge Base''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "FAQ" link 
        web.assert_text_equal_by_xpath("FAQ",'''//div[@id='content']/div/div/div/div[2]/div/section/div[3]/p[3]/a[2]''')
        web.click_element_by_link_text("FAQ")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Frequently Asked Questions''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')     
        web.go_back()
        #check the "freenode.net on channel #openshift" link 
        web.assert_text_equal_by_xpath("freenode.net on channel #openshift",'''//div[@id='content']/div/div/div/div[2]/div/section/div[3]/p[4]/a''')
        web.click_element_by_link_text("freenode.net on channel #openshift")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Connection details''','''//body/div/div/div[2]/a''')   
        web.go_back()





        #check the "Subscribe today" link 
        web.assert_text_equal_by_xpath("Subscribe today",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[3]/a''')
        web.click_element_by_link_text("Subscribe today")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Thanks for signing up for the OpenShift Newsletter which includes news and events, tips and tricks and other useful information concerning the OpenShift platform-as-a-service. Please provide a valid email address and click submit.''','''//body/div[2]/form/div/p''')   
        web.go_back()
        #check the "powered by open source" link 
        web.assert_text_equal_by_xpath("powered by open source",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[4]/a''')
        web.click_element_by_link_text("powered by open source")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift is Open Source''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''')   
        web.go_back()
        #check the "run on your laptop" link 
        web.assert_text_equal_by_xpath("run on your laptop",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[4]/a[2]''')
        web.click_element_by_link_text("run on your laptop")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''OpenShift Origin Source Code''','''//div[@id='content']/div/div/div/div/div/h1''')   
        web.go_back()
        #check the "Get involved today" link 
        web.assert_text_equal_by_xpath("Get involved today",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[4]/a[3]''')
        web.click_element_by_link_text("Get involved today")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Get Involved''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''') 
        web.go_back()

        #check the "@openshift" link 
        web.assert_text_equal_by_xpath("@openshift",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[5]/a''')
        web.assert_text_equal_by_xpath('''@openshift''','''//a[@href='http://www.twitter.com/#!/openshift']''')   
        #check the "OpenShift blog" link 
        web.assert_text_equal_by_xpath("OpenShift blog",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[5]/a[2]''')
        web.click_element_by_link_text("OpenShift blog")
        time.sleep(2)
        web.assert_text_equal_by_xpath('''Blogs''','''//div[@id='content']/div/div/div/div[3]/div/h1/div''') 
        web.go_back()
        #check the "file a bug" link 
        web.assert_text_equal_by_xpath("file a bug",'''//div[@id='content']/div/div/div/div[2]/div/section/div[4]/p[6]/a''')
        web.assert_text_equal_by_xpath('''file a bug''','''//a[contains(@href, 'https://bugzilla.redhat.com/enter_bug.cgi?product=OpenShift')]''')   
        web.go_back()



        web.delete_app("python")


        
    
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
