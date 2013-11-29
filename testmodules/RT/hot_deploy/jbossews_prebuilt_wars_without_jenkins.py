#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012
"""

import rhtest
import common
from jbossas_prebuilt_wars_without_jenkins import JBossHotDeployPrebuiltWarsWithoutJenkins

class EWSHotDeployPrebuiltWarsWithoutJenkins(JBossHotDeployPrebuiltWarsWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployPrebuiltWarsWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbossews']
        self.config.war_files = [ "sample.war" ]
        self.config.deploy_dir = "webapps"
        self.config.summary = "[US2513] Hot deployment support for Jboss EWS application with pre-built war"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSHotDeployPrebuiltWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
