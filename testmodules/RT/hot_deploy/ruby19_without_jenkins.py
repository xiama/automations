#!/usr/bin/python

"""
Attila Nagy
Aug 28, 2012

"""
import rhtest
import common
from ruby18_without_jenkins import Ruby18HotDeployWithoutJenkins

class Ruby19HotDeployWithoutJenkins(Ruby18HotDeployWithoutJenkins):
    def __init__(self, config):
        Ruby18HotDeployWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['ruby-1.9']
        self.config.summary = "[US2443]Hot deployment support for application - without Jenkins - ruby-1.9"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby19HotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
