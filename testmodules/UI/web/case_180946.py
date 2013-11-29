#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_180946.py
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


class DeleteSpringeap6App(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()

        #create a springeap6 app
        web.create_app("springeap6", "sprinteap")
        
        time.sleep(20)
        web.assert_text_equal_by_xpath('''Your application has been created. If you're new to OpenShift check out these tips for where to go next.''', '''//div[@id='content']/div/div/div/div[2]/div/section/p''')
     
          

        #delete a springeap app
        web.delete_last_app("springeap")
        

        self.tearDown()

        return self.passed(" case_180946--DeleteSpringeap6App passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DeleteSpringeap6App)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_180946.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
