#!/usr/bin/python

"""
Attila Nagy
Nov 13, 2012
"""

import rhtest
import common
from nodejs_without_jenkins import NodeJSHotDeployWithoutJenkins

class NodeJSScalingHotDeployWithoutJenkins(NodeJSHotDeployWithoutJenkins):
    def __init__(self, config):
        NodeJSHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2747][RT]Hot deployment support for scalable application - without Jenkins - nodejs"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NodeJSScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
