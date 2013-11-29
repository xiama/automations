#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_141725.py
#  Date:      2012/08/10 11:23
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class add_mysql(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a jbosseap app
        web.create_app("jbosseap-6.0","jbosseap")
        time.sleep(5)
        
        #add mysql cartridge
        web.add_cartridge("jbosseap", "mysql-5.1")
        web.assert_text_equal_by_xpath("MySQL Database 5.1",'''//div[@id='cartridge_type_']/h3''')

        #delete a jbosseap app
        web.delete_last_app("jbosseap")
    
        self.tearDown()

        return self.passed(" case 141725 is passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(add_mysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_141725.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
