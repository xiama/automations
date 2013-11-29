#!/usr/bin/python

"""
Attila Nagy
Nov 6, 2012
"""

import rhtest
import common
from jbosseap_without_jenkins import EAPHotDeployWithoutJenkins

class EAPScalingHotDeployWithoutJenkins(EAPHotDeployWithoutJenkins):
    def __init__(self, config):
        EAPHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2443] Hot deployment support for scalable application - without Jenkins - jbossaeap6"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
