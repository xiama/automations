#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012
"""

import rhtest
import common
from jbossas_exploded_wars_without_jenkins import JBossHotDeployExplodedWarsWithoutJenkins

class EWSHotDeployExplodedWarsWithoutJenkins(JBossHotDeployExplodedWarsWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployExplodedWarsWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbossews']
        self.config.deploy_dir = "webapps"
        self.config.summary = "[US2513] Hot deployment support for JbossEWS application with exploded wars"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSHotDeployExplodedWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
