#!/usr/bin/python

"""
Attila Nagy
Aug 1, 2012

"""
import rhtest
import common
from jbosseap_without_jenkins import EAPHotDeployWithoutJenkins

class EAPHotDeployWithJenkins(EAPHotDeployWithoutJenkins):
    def __init__(self, config):
        EAPHotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2443] Hot deployment support for application - with Jenkins - Jboss-eap6"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
