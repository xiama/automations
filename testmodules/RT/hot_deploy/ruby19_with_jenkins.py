#!/usr/bin/python

"""
Attila Nagy
Aug 28, 2012

"""
import rhtest
import common
from ruby19_without_jenkins import Ruby19HotDeployWithoutJenkins

class Ruby19HotDeployWithJenkins(Ruby19HotDeployWithoutJenkins):
    def __init__(self, config):
        Ruby19HotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2443]Hot deployment support for application - with Jenkins - ruby-1.9"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby19HotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
