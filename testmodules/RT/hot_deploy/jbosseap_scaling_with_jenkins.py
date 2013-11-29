#!/usr/bin/python

"""
Attila Nagy
Aug 1, 2012

"""
import rhtest
import common
from jbosseap_with_jenkins import EAPHotDeployWithJenkins

class EAPScalingHotDeployWithJenkins(EAPHotDeployWithJenkins):
    def __init__(self, config):
        EAPHotDeployWithJenkins.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2443] Hot deployment support for scalable application - with Jenkins - jboss-eap6"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPScalingHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
