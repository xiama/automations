#!/usr/bin/python

"""
Attila Nagy
Aug 1, 2012

"""
import rhtest
import common
from jbossas_without_jenkins import JBossHotDeployWithoutJenkins

class JBossHotDeployWithJenkins(JBossHotDeployWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployWithoutJenkins.__init__(self, config)
        self.config.jenkins_is_needed = True
        self.config.summary = "[US2309] Hot deployment support for JBoss AS 7 - with Jenkins"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossHotDeployWithJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
