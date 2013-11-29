#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180954.py
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


class CreateSpringEapAppAndChangeDomainName(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a springeap app
        #web.create_app("springeap6","springeap")
        web.go_to_create_app("springeap6")
        web.input_by_id("application_name", "springeap")
        web.click_element_by_id("application_submit")
        time.sleep(20)
              
        
        web.go_to_domain_edit()
        web.input_by_id("domain_name","yujzhangcccc")
        web.click_element_by_id("domain_submit")
        time.sleep(15)
         

        #check the url after changed the domain name
        web.go_to_app_detail("springeap")
        web.assert_element_present_by_link_text("http://springeap-yujzhangcccc."+web.platform+".rhcloud.com/")
        #change the domain name back
        web.go_to_domain_edit()
        web.input_by_id("domain_name",web.domain)
        web.click_element_by_id("domain_submit")
        time.sleep(15)
        
        #delete a springeap app
        web.delete_last_app("springeap")
        
        self.tearDown()

        return self.passed(" case_180954--CreateSpringEapAppAndChangeDomainName passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateSpringEapAppAndChangeDomainName)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174336.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
