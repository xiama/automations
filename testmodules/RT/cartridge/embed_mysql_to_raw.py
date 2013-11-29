#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1221][rhc-cartridge] embed MySQL instance to DIY application
https://tcms.engineering.redhat.com/case/122382/
"""
import os
import sys

import rhtest
import testcase
import common

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US1221][rhc-cartridge] embed MySQL instance to DIY application"
        self.app_name = "diy"
        self.app_type = common.app_types["diy"]
        tcms_testcase_id=122382
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysqlToRaw(OpenShiftTest):
    def test_method(self):
        #"Create a diy app", 
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret,0, "the app should be created successfully")

        #"Embed mysql to the app", 
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"])
        self.assert_equal(ret, 0, "the mysql cartridge should be embedded successfully")

        #"Remove embedded mysql from the app", 
        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["mysql"])
        self.assert_equal(ret,0, "the mysql should be removed successfully")

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EmbedMysqlToRaw)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
