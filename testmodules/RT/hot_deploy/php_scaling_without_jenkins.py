#!/usr/bin/python

"""
Attila Nagy
Sept 26, 2012
"""
import rhtest
import common
from php_without_jenkins import PHPHotDeployWithoutJenkins

class PHPScalingHotDeployWithoutJenkins(PHPHotDeployWithoutJenkins):
    def __init__(self, config):
        PHPHotDeployWithoutJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2443] Hot deployment support for scaling application - php - without jenkins"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PHPScalingHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
