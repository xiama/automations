#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012

"""
import rhtest
import common
from jbossas_exploded_wars_without_jenkins import JBossHotDeployExplodedWarsWithoutJenkins

class EAPHotDeployExplodedWarsWithoutJenkins(JBossHotDeployExplodedWarsWithoutJenkins):
    def __init__(self, config):
        JBossHotDeployExplodedWarsWithoutJenkins.__init__(self, config)
        self.config.application_type = common.app_types['jbosseap']
        self.config.summary = "[US2443] Hot deployment support for Jboss-Eap6 application with exploded wars"
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EAPHotDeployExplodedWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
