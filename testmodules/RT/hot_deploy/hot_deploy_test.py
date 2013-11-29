#!/usr/bin/python

"""
Attila Nagy
Jul 25, 2012

This is the super class for hot-deployment testing
"""

import rhtest
import common
import OSConf
import pexpect
import re
from openshift import Openshift
from shutil import rmtree
from time import sleep

class HotDeployTest(rhtest.Test):
    
    def log_info(self, message):
        self.info("===========================")
        self.info(message)
        self.info("===========================")
        
    def initialize(self):
        self.log_info("Initializing...")
        common.env_setup()
        # Creating the application
	self.app_type = self.config.application_type
	self.app_name = self.config.application_name
        common.create_app(
            self.config.application_name,
            self.config.application_type,
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd,
            clone_repo = True,
            git_repo = "./" + self.config.application_name,
            scalable = self.config.scalable
        )
        
        # Checking the application URL
        status, res = self.config.rest_api.app_get(self.config.application_name)
        if status == 'OK':
            self.config.application_url = res['app_url']
        else:
            self.config.applicaton_url = 'Not found'

        self.info("Application URL: " + self.config.application_url)
        
        
    def finalize(self):
        self.log_info("Finalizing...")
        rmtree("./%s" % self.config.application_name)
    
    def enable_jenkins(self):
        self.log_info("Enabling Jenkins if it's necessary")
        if self.config.jenkins_is_needed:
            common.create_app(
                "jenkins",
                common.app_types['jenkins'],
                self.config.OPENSHIFT_user_email,
                self.config.OPENSHIFT_user_passwd,
                clone_repo = False
            )
            common.embed(
                self.config.application_name, 
                "add-" + common.cartridge_types["jenkins"],
                self.config.OPENSHIFT_user_email,
                self.config.OPENSHIFT_user_passwd
            )
            
    def enable_hot_deployment(self):
        self.log_info("Enabling hot deployment support")
        marker = open("./%s/.openshift/markers/hot_deploy" % self.config.application_name, "a")
        marker.write("\n")
        marker.close()
            
    def configuration(self):
        # Setting up the code to retrieve process ID
        # It must be overriden
        pass
    
#    def get_process_id(self):
#        self.log_info("Getting the process ID")
#        return int(common.fetch_page("%s/%s" % ( self.config.application_url, self.config.file_name )))
    def get_process_id(self):
        pids = []
        if self.app_type.split('-')[0] in ('jbossas', 'jbosseap'):
            cmd = "ssh %s 'ps aux |grep -v grep| grep -i standalone'" % (OSConf.get_ssh_url(self.app_name))
        elif 'jbossews' in self.app_type:
            cmd = "ssh %s 'ps aux |grep -v grep| grep jre'" % (OSConf.get_ssh_url(self.app_name))
        else:
            cmd = "ssh %s 'ps aux |grep -v grep| grep bin/httpd'" % (OSConf.get_ssh_url(self.app_name))
        child = pexpect.spawn(cmd)
        print ">>"*50
        print cmd
        print "<<"*50
        for line in child.readlines():
            match = None
            if self.app_type.split('-')[0] in ('jbossas', 'jbosseap'):
                if 'jre' in line or 'standalone.sh' in line:
                    print line
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            elif 'jbossews' in self.app_type:
                if 'java' in line:
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            else:
                if 'httpd -C Include' in line:
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            if match:
                if match.group(1) not in pids:
                    pids.append(int(match.group(1)))
        pids.sort()
        return pids


    def deploy(self):
        deployment_steps = [
            "cd %s" % self.config.application_name,
            "git add .",
            "git commit -a -m 'Adding test file'",
            "git push"
        ]
        ret_code = common.command_get_status(" && ".join(deployment_steps))
        self.info("Waiting for the application...")
        sleep(30) # Waiting 30 minutes for the application
        return ret_code
    
    def deploy_changes(self):
        self.log_info("Modifying local git repo and push")
        steps = [
            "cd %s" % self.config.application_name,
            "touch %s" % common.getRandomString()
        ]
        common.command_get_status(" && ".join(steps))
        return self.deploy()
    
    def verification(self, lst1, lst2):
        print "$$"*50
        print "pid_original : %s"%lst1
        print "pid_later : %s"%lst2
        print "$$"*50
        if len(lst1) > len(lst2):
            return False
        for i in range(len(lst1)):
            if lst1[i] != lst2[i]:
                return False
#        return True
#        self.info("PID1: %d" % pid1)
#        self.info("PID2: %d" % pid2)
#        self.assert_equal(pid1[], pid2)
        # Everything is OK
        return self.passed(self.config.summary)
            
    def test_method(self):
        self.enable_jenkins()
        self.enable_hot_deployment()
        self.configuration()
        pid_original = self.get_process_id()
        self.deploy_changes()
        pid_latter = self.get_process_id()
        return self.verification(pid_original, pid_latter)
