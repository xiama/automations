#!/usr/bin/python

"""
Attila Nagy
Oct 24, 2012
"""

import rhtest
import common
from python_without_jenkins import PythonHotDeployWithoutJenkins

class PythonScalingHotDeployWithoutJenkins(PythonHotDeployWithoutJenkins):
    
    def __init__(self, config):
        PythonHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2747][RT]Hot deployment support for scalable application - without Jenkins - python"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PythonScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
