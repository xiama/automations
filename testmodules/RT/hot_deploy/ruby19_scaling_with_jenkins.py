#!/usr/bin/python

"""
Attila Nagy
Aug 29, 2012

"""
import rhtest
import common
from ruby19_scaling_without_jenkins import Ruby19ScalingHotDeployWithoutJenkins

class Ruby19ScalingHotDeployWithJenkins(Ruby19ScalingHotDeployWithoutJenkins):
    def __init__(self, config):
        Ruby19ScalingHotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2443]Hot deployment support for scalable application - with Jenkins - ruby-1.9"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby19ScalingHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
