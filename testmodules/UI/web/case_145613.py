#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_145613.py
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


class CheckHeaderTabs(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.go_to_home()

        web.assert_text_equal_by_xpath("LEARN MORE","//nav[@id='nav']/div/div/ul/li/a/span")
        web.assert_text_equal_by_xpath("GET STARTED","//nav[@id='nav']/div/div/ul/li[2]/a/span")
        web.assert_text_equal_by_xpath("DEVELOPERS","//nav[@id='nav']/div/div/ul/li[4]/a/span")
        web.assert_text_equal_by_xpath("COMMUNITY","//nav[@id='nav']/div/div/ul/li[5]/a/span")


        self.tearDown()

        return self.passed(" case_145613--CheckHeaderTabs passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckHeaderTabs)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_145613.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
