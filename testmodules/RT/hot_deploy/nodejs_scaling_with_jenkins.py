#!/usr/bin/python

"""
Attila Nagy
Nov 13, 2012
"""

import rhtest
import common
from nodejs_with_jenkins import NodeJSHotDeployWithJenkins

class NodeJSScalingHotDeployWithJenkins(NodeJSHotDeployWithJenkins):
    def __init__(self, config):
        NodeJSHotDeployWithJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2747][RT]Hot deployment support for scalable application - with Jenkins - nodejs"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NodeJSScalingHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
