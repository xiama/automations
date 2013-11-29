#!/usr/bin/python

"""
Attila Nagy
Nov 13, 2012
"""

import rhtest
import common
from nodejs_without_jenkins import NodeJSHotDeployWithoutJenkins

class NodeJSHotDeployWithJenkins(NodeJSHotDeployWithoutJenkins):

    def __init__(self, config):
        NodeJSHotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2747][RT]Hot deployment support for application - with Jenkins - nodejs"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NodeJSHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
