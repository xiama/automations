#!/usr/bin/python

"""
Attila Nagy
Nov 7, 2012

"""
import os
import shutil
import rhtest
import common
from jbossas_exploded_wars_without_jenkins import JBossHotDeployExplodedWarsWithoutJenkins

class JBossHotDeployPrebuiltWarsWithoutJenkins(JBossHotDeployExplodedWarsWithoutJenkins):

    def __init__(self, config):
        JBossHotDeployExplodedWarsWithoutJenkins.__init__(self, config)
        self.config.summary = "[US2443] Hot deployment support for Jboss-as7 application with 2 pre-built wars"

    def war(self, operation, war_file):
        source_file = "%s/%s" % ( self.config.app_template_dir, war_file )
        destination_dir = "./%s/%s" % ( self.config.application_name, self.config.deploy_dir )
        destination_file = "%s/%s" % ( destination_dir, war_file )
        marker_file_name = "%s/%s.dodeploy" % ( destination_dir, war_file )
        if operation == "add":
            # Copying the file
            shutil.copyfile(source_file, destination_file)
            # Creating the marker
            marker = file(marker_file_name, "a")
            marker.close()
        elif operation == "remove":
            # Removing the file
            os.remove(destination_file) 
            # Removing marker
            os.remove(marker_file_name)
        # ... and deploying
        self.deploy()
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossHotDeployPrebuiltWarsWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
