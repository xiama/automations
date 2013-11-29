#!/usr/bin/python

"""
Attila Nagy
Aug 29, 2012

"""
import rhtest
import common
from ruby18_without_jenkins import Ruby18HotDeployWithoutJenkins

class Ruby18ScalingHotDeployWithoutJenkins(Ruby18HotDeployWithoutJenkins):
    def __init__(self, config):
        Ruby18HotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2443]Hot deployment support for scalable application - without Jenkins - ruby-1.8"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby18ScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
