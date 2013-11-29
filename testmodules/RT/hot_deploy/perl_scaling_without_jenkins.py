#!/usr/bin/python

"""
Attila Nagy
Sept 26, 2012
"""
import rhtest
import common
from perl_without_jenkins import PerlHotDeployWithoutJenkins

class PerlScalingHotDeployWithoutJenkins(PerlHotDeployWithoutJenkins):
    def __init__(self, config):
        PerlHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2443] Hot deployment support for scailing application - perl - without jenkins"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PerlScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
