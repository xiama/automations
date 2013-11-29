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


class CreateJbossEapAppAndChangeDomainName(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        web.create_app("jbosseap-6.0","jbosseap")

        #check wether the links are correct
        time.sleep(5)
       
        #check the "appurl" link
        web.go_to_app_detail("jbosseap")
        web.click_element_by_link_text('''http://jbosseap-'''+web.domain+'''.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(2)
        web.assert_text_equal_by_xpath("Welcome To OpenShift, JBossEAP6.0 Cartridge",'''//h1''') 
        
        #go to my account page and change domain name
        web.go_to_domain_edit()
        web.input_by_id("domain_name","yujzhangcccc")
        web.click_element_by_id("domain_submit")
        time.sleep(10)
        
        #check the url after changed the domain name
        web.go_to_app_detail("jbosseap")
        web.click_element_by_link_text('''http://jbosseap-yujzhangcccc.'''+web.platform+'''.rhcloud.com/''')
        time.sleep(2)
        web.assert_text_equal_by_xpath("Welcome To OpenShift, JBossEAP6.0 Cartridge",'''//h1''') 

        #change the domain name back
        web.go_to_domain_edit()
        web.input_by_id("domain_name",web.domain)
        web.click_element_by_id("domain_submit")
        time.sleep(10)
         
        #delete a jbosseap app
        web.delete_last_app("jbosseap")


        self.tearDown()

        return self.passed(" case_174336--CreateJbossEapAppAndChangeDomainName passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateJbossEapAppAndChangeDomainName)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174336.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
