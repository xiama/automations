#!/usr/bin/python

"""
Attila Nagy
Aug 1, 2012

"""
import rhtest
import common
from jbossas_without_jenkins import JBossHotDeployWithoutJenkins

class EAPHotDeployWithoutJenkins(JBossHotDeployWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbosseap']
        self.config.pid_file = "/app-root/runtime/jbosseap.pid"
        self.config.summary = "[US2422] Hot deployment support for JBoss EAP6 - without Jenkins"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
