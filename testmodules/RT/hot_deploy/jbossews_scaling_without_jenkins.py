#!/usr/bin/python

"""
Attila Nagy
Nov 6, 2012
"""

import rhtest
import common
from jbossews_without_jenkins import EWSHotDeployWithoutJenkins

class EWSScalingHotDeployWithoutJenkins(EWSHotDeployWithoutJenkins):
    def __init__(self, config):
        EWSHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2513] Hot deployment support for scalable application - without Jenkins - jbossEWS"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
