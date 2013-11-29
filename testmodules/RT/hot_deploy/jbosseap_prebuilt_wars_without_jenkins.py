#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012
"""

import rhtest
import common
from jbossas_prebuilt_wars_without_jenkins import JBossHotDeployPrebuiltWarsWithoutJenkins

class EAPHotDeployPrebuiltWarsWithoutJenkins(JBossHotDeployPrebuiltWarsWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployPrebuiltWarsWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbosseap']
        self.config.summary = "[US2443] Hot deployment support for Jboss EAP6 application with 2 pre-built wars"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPHotDeployPrebuiltWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
