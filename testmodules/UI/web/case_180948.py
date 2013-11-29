#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174336.py
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


class CreateRubyAndRailsAppAndChangeDomainName(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        #web.create_app("rails","rubyonrails")
        web.create_app("rails", "rubyonrails")
        
        time.sleep(20)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')
     
               
        #go to my account page and change domain name
        web.go_to_domain_edit()
        web.input_by_id("domain_name","yujzhangcccc")
        web.click_element_by_id("domain_submit")
        time.sleep(10)
        web.assert_text_equal_by_xpath("Your domain has been changed. Your public URLs will now be different",'''//div[@id='content']/div/div/div/div[2]/div/div/div''') 

        #check the url after changed the domain name
        web.go_to_app_detail("rubyonrails")
        web.assert_text_equal_by_xpath("http://rubyonrails-yujzhangcccc.stg.rhcloud.com/",'''//div[@id='content']/div/div/div/div[2]/nav/div/a''')
        

        #change the domain name back
        web.go_to_domain_edit()
        web.input_by_id("domain_name","yujzhang")
        web.click_element_by_id("domain_submit")
        time.sleep(10)
        web.assert_text_equal_by_xpath("Your domain has been changed. Your public URLs will now be different",'''//div[@id='content']/div/div/div/div[2]/div/div/div''') 

        
        #web.delete_last_app("rubyonrails")
        web.go_to_app_detail("rubyonrails")
        time.sleep(2)
        web.click_element_by_link_text("Delete this application")
        time.sleep(1)
        web.click_element_by_name("commit")
        time.sleep(60)
        web.assert_text_equal_by_xpath('''Create your first application now!''', '''//div[2]/div/div/div''')
        


        self.tearDown()

        return self.passed(" case_180948--CreateRubyAndRailsAppAndChangeDomainName passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateRubyAndRailsAppAndChangeDomainName)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174336.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
