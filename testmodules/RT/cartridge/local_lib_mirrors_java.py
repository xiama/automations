#!/bin/env python
"""
Linqing Lu
lilu@redhat.com
Dec 12, 2011

[US1309][rhc-cartridge]Create local lib mirrors for Java framework
https://tcms.engineering.redhat.com/case/122394/
"""
import os
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1309][rhc-cartridge]Create local lib mirrors for Java framework")
        common.env_setup()
        self.app = { 'name' : common.getRandomString(7), 
                     'type' : common.app_types['jbossas'] }

    def finalize(self):
        os.system("rm -rf %s"%(self.app['name']))
        os.system("rm -rf kitchensink-example")


class LocalLibMirrorsJava(OpenShiftTest):
    def test_method(self):
        self.add_step("Create an %s app: %s" % (self.app['type'],self.app['name']),
                common.create_app,
                function_parameters = [self.app['name'], self.app['type']],
                expect_description = "App should be created successfully",
                expect_return = 0)

        self.add_step("Get jbossas-quickstart codes",
                "rm -rf kitchensink-example; git clone https://github.com/openshift/kitchensink-example.git",
                expect_return = 0)

        self.add_step("Git push codes",
                "cd %s && cp -rf ../kitchensink-example/* . && git add . && git commit -am test && git push" 
                    % self.app['name'],
                expect_str = ['BUILD SUCCESS', 'Downloaded: http.*nexus'],
                expect_return = 0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LocalLibMirrorsJava)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
