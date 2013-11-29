#!/usr/bin/python

"""
Attila Nagy
Aug 1, 2012

"""
import rhtest
import common
from ruby18_without_jenkins import Ruby18HotDeployWithoutJenkins

class Ruby18HotDeployWithJenkins(Ruby18HotDeployWithoutJenkins):
    def __init__(self, config):
        Ruby18HotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2443]Hot deployment support for application - with Jenkins - ruby-1.8"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby18HotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
