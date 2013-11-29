#!/usr/bin/python

#
#  File name: Use rsync jenkins like deploy to move code and libraries between gears.py
#  Date:      2012/04/05 16:44
#  Author:    mzimen@redhat.com
#  [US2087][Runtime][rhc-cartridge]Use rsync jenkins like deploy to move code and libraries between gears
#

import sys
import os
import re

import rhtest
import testcase
import common
import OSConf

#TODO: to accomplish
class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `php` instead.")
            self.app_type = 'php'

        common.env_setup()

    def finalize(self):
        os.sytem("rm -rf %s"%self.app_name)

class CheckGearsRsyncAtJenkins(OpenShiftTest):
    def test_method(self):
        #"Create a scalable application via REST API",
        ret = common.create_scalable_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(0,ret)

        ret = common.scale_up(self.app_name)
        self.assert_equal(0,ret)

        self.summary ="Scale up the app using REST API:" 


        return self.passed("%s passed" % self.__class__.__name__)

    def edit_app(self):
        content='''<html> <body> <?php echo "App DNS: " . $_ENV["OPENSHIFT_GEAR_DNS"] . "<br />"; ?> </body> </html> '''
        f = open("%s/php/index.php"%self.app_name, "w")
        f.write(content)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CheckGearsRsyncAtJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
