#!/usr/bin/env python

import common
import rhtest
import re

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    CART_LIST = []
    BLACKLIST = ("10gen", "rockmongo", "phpmyadmin", "phpmoadmin", "jenkins")

    def initialize(self):
        self.info("[US1317][UI][CLI]rhc wrapper - rhc cartridge")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        self.actions = ['add', 'stop', 'status', 'start', 'restart', 'reload', 'remove']
        common.env_setup()

    def finalize(self):
        pass


class RhcWrapper(OpenShiftTest):
    def gen_cartr_list(self):
        cmd = "rhc cartridge list -l %s -p '%s' %s"%(self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
        (status, output) = common.cmd_get_status_output(cmd)

        self.assert_equal(status, 0, "Unable to get list of cartridges")
        self.assert_match("postgresql", output, "Missing postgresql support?")
        self.assert_match("mysql", output, "Missing mysql support")

        x = re.compile(r"^(.*-\d+\.\d+, .*-\d+\.\d+, .*)$", re.MULTILINE)
        obj = x.search(output)
        if (obj):
            self.CART_LIST=[]
            for i in obj.group(1).split(', '):
                print "Appended %s"%i
                self.CART_LIST.append(i)
        return 0

    def gen_function(self, action, cartridge, app_name):
        cmd = "rhc cartridge %s %s -a %s -l %s -p '%s' %s "%(action, cartridge, app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        if action == "remove":
            return cmd + "--confirm"
        else:
            return cmd

    def gen_steps(self, app_names):
        for app_name in app_names:
            print "app_name:",app_name
            for cartridge_name in self.CART_LIST:
                print "cartridge_name:",cartridge_name
                _x=None
                for black in self.BLACKLIST:
                    if re.search(r"%s"%black,cartridge_name):
                        _x=1
                        break
                if _x==1:
                    _x=None
                    continue
                for action in self.actions:
                    self.add_step("Execute '%s' with %s"%(action, cartridge_name),
                                  self.gen_function(action, cartridge_name, app_name),
                                  expect_return = 0, try_count=3)

    def test_method(self):

        self.step("Get the list of supported cartridges")
        self.assert_equal(0, self.gen_cartr_list())

        self.step("Create a test app")
        self.assert_equal(0, common.create_app(self.app_name, 
                                               common.app_types['php'], 
                                               self.user_email, 
                                               self.user_passwd, 
                                               False))

        #let's generates steps for all cartridges and actions...
        self.gen_steps([self.app_name])

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcWrapper)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
