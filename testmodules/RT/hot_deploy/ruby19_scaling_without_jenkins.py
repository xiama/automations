#!/usr/bin/python

"""
Attila Nagy
Aug 29, 2012

"""
import rhtest
import common
from ruby18_scaling_without_jenkins import Ruby18ScalingHotDeployWithoutJenkins

class Ruby19ScalingHotDeployWithoutJenkins(Ruby18ScalingHotDeployWithoutJenkins):
    
    def __init__(self, config):
        Ruby18ScalingHotDeployWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types["ruby-1.9"]
        self.config.summary = "[US2443]Hot deployment support for scalable application - without Jenkins - ruby-1.9"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Ruby19ScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
