#!/usr/bin/python

"""
Attila Nagy
Nov 6, 2012
"""

import rhtest
import common
from jbossews_scaling_without_jenkins import EWSScalingHotDeployWithoutJenkins

class EWSScalingHotDeployWithJenkins(EWSScalingHotDeployWithoutJenkins):
    def __init__(self, config):
        EWSScalingHotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2513] Hot deployment support for scalable application - with Jenkins - jbossEWS"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSScalingHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
