#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
# user defined packages
import urllib
from quick_start_test import QuickStartTest

class QuickStartDiyBinhello(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["diy"]
        self.config.application_embedded_cartridges = [ ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: DYI-Binhello"
        self.config.page = "" # means '/'
        self.config.page_pattern = "Hello, World!"
    
    def configuration_steps(self):
        self.log_info("Configuring")
        
        # Getting binhello
        # Saving to $GIT_REPO/bin
        print "Creating directory: %s/bin" % self.config.application_name
        os.mkdir(self.config.application_name + "/bin")
        print "Downloading remote binary"
        remote_binary = urllib.urlopen("https://raw.github.com/openshift/openshift-diy-binhello-demo/master/binhello")
        binhello_binary = open("%s/bin/binhello" % self.config.application_name, "w")
        binhello_binary.write(remote_binary.read())
        binhello_binary.close()
        print "Adding execution permissions to the binary"
        os.chmod("%s/bin/binhello" % self.config.application_name, 0755)
        
        #Editing configuration files
        start_hook_filename = "%s/.openshift/action_hooks/start" % self.config.application_name
        print "Editing configuration file: " + start_hook_filename
        start_hook = open(start_hook_filename, "w")
        start_hook.write("#!/bin/bash\n")
        start_hook.write("cd $OPENSHIFT_REPO_DIR/bin\n")
        start_hook.write("nohup ./binhello >${OPENSHIFT_DIY_LOG_DIR}/binhello.log 2>&1 &\n")
        start_hook.close()
        os.chmod(start_hook_filename, 0755)
        
        stop_hook_filename = "%s/.openshift/action_hooks/stop" % self.config.application_name
        print "Editing configuration file: " + stop_hook_filename
        stop_hook = open(stop_hook_filename, "w")
        stop_hook.write("#!/bin/bash\n")
        stop_hook.write("kill `ps -ef | grep binhello | grep -v grep | awk '{ print $2 }'` > /dev/null 2>&1\n")
        stop_hook.write("exit 0\n")
        stop_hook.close()
        os.chmod(stop_hook_filename, 0755)
        
    def pre_deployment_steps(self):
        self.log_info("Performing additional step before deploying")
        steps = [
            "cd %s" % self.config.application_name,
            "git add .",
            "git commit -a -m testing"
        ]
        ret_code = common.command_get_status(" && ".join(steps))    


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartDiyBinhello)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
