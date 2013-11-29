#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174331.py
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


class CheckJbossEapInAppCartridgePage(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
       
        #go to app create page
        web.go_to_create_app("")
       
        #check the jboss eap cartridge in this page
        web.assert_text_equal_by_xpath('''JBoss Enterprise Application Platform 6.0''','''//div[@id='application_type_jbosseap-6.0']/h3''')
        web.assert_text_equal_by_xpath('''Market-leading open source enterprise platform for next-generation, highly transactional enterprise Java applications. Build and deploy enterprise Java in the cloud.''','''//div[@id='application_type_jbosseap-6.0']/p''')
     
         


        self.tearDown()

        return self.passed(" case_174331--CheckJbossEapInAppCartridgePage passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckJbossEapInAppCartridgePage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174331.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
