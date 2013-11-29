#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012
"""

import os
import shutil
import rhtest
import common
from jbossas_without_jenkins import JBossHotDeployWithoutJenkins

class JBossHotDeployExplodedWarsWithoutJenkins(JBossHotDeployWithoutJenkins):

    def __init__(self, config):
        JBossHotDeployWithoutJenkins.__init__(self, config)
        self.config.summary = "[US2443] Hot deployment support for Jboss application with exploded wars"
        self.config.deploy_dir = "deployments"
        self.config.app_template_dir = os.path.dirname(__file__) + "/../cartridge/app_template"
        self.config.war_files = [ "weldguess.war", "sample.war" ]

    def war(self, operation, war_file):
        war_dir = "./%s/%s/%s" % ( self.config.application_name, self.config.deploy_dir, war_file )
        war_dir_marker = war_dir + ".dodeploy"
        if operation == "add":
            # Creating the directory
            os.mkdir(war_dir)
            # Exploding the war file
            steps = [
                "cd %s" % war_dir,
                "jar -xvf %s" % self.config.app_template_dir + "/" + war_file
            ]
            common.command_get_status(" && ".join(steps))
            # Adding marker
            marker = file(war_dir_marker, "a")
            marker.close()
        elif operation == "remove":
            # Removing the exploded war
            shutil.rmtree(war_dir)
            os.remove(war_dir_marker)
        # ... and deploying
        self.deploy()

    def test_method(self):
        self.enable_jenkins()
        self.enable_hot_deployment()
        self.configuration()
        pid_original = self.get_process_id()
        for war in self.config.war_files:
            self.war("add", war)
        pid_new = self.get_process_id()
        self.verification(pid_original, pid_new)
        for war in self.config.war_files:
            for operation in [ "remove", "add" ]:
                self.war(operation, war)
                pid_new = self.get_process_id()
                self.verification(pid_original, pid_new)
        
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossHotDeployExplodedWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
