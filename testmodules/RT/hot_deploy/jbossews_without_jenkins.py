#!/usr/bin/python

"""
Attila Nagy
Oct 23, 2012
"""

import rhtest
import common
from jbossas_without_jenkins import JBossHotDeployWithoutJenkins

class EWSHotDeployWithoutJenkins(JBossHotDeployWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbossews']
        #self.config.application_type_no_version = 'jbossews'
        self.config.pid_file = "/jbossews/run/jboss.pid"
        self.config.summary = "[US2513] Hot deployment support for JBossEWS- without Jenkins"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
