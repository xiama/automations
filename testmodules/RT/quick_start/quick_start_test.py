#!/usr/bin/python

"""
Attila Nagy
anagy@redhat.com
May 29, 2012
"""

import rhtest
import common
import re
import json
from pycurl import Curl
from pycurl import URL
from pycurl import WRITEFUNCTION
from shutil import rmtree
from time import sleep
from StringIO import StringIO

class QuickStartTest(rhtest.Test):
    """
    This is the super-class for OpenShift quick-start testing.
    
    If you need something specific in your sub-class, then you have to override the
    appropriate method.
    """

    def get_github_repo_name(self):
        """Returns reponame on GitHub"""
        return re.split(r'[/]', re.sub(r'\.git$', '', self.config.git_upstream_url))[-1]

    def get_git_branch_name(self):
        """Return the branch name should be used. If there's dev/typeless branch available we should use that one.
        # Retrieving info
        self.info("Repo name: " + self.get_github_repo_name())
        github_response = StringIO()
        github = Curl()
        github.setopt(URL, "https://api.github.com/repos/openshift/%s/branches" % self.get_github_repo_name())
        github.setopt(WRITEFUNCTION, github_response.write)
        github.perform()
        branches = json.loads(github_response.getvalue())
        # Looking for branch 'dev/typeless'
        branch_name_return = "master"
        for branch in branches:
            if branch["name"] == "dev/typeless":
                branch_name_return =  branch["name"]
                break
        self.info("We will use branch '%s'" % branch_name_return)
        return branch_name_return"""
	# The new behaviour is to use master branch
	return "master"

    def log_info(self, message):
        self.info("===========================")
        self.info(message)
        self.info("===========================")
        
    def initialize(self):
        self.log_info("Initializing")
	self.config.application_name = common.getRandomString()
        # General set-up
        common.env_setup()    
        # Creating the application
        common.create_app(
            self.config.application_name,
            self.config.application_type,
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd,
            clone_repo = True,
            git_repo = "./" + self.config.application_name
        )
        
        # Embedding cartridges
        for cartridge in self.config.application_embedded_cartridges:
            common.embed(
                self.config.application_name,
                "add-" + cartridge,
                self.config.OPENSHIFT_user_email,
                self.config.OPENSHIFT_user_passwd
            )
        
    def finalize(self):
        self.log_info("Finalizing")
        rmtree("./%s" % self.config.application_name)
        
    def pre_configuration_steps(self):
        pass
    
    def configuration_steps(self):
        self.log_info("Configuring")
        branch_name = self.get_git_branch_name()
        # Adding upstream url
        steps = [
            "cd %s" % self.config.application_name,
            "git remote add upstream -m %s %s" % ( branch_name, self.config.git_upstream_url ),
            "git pull -s recursive -X theirs upstream %s" % branch_name
        ]
        ret_code = common.command_get_status(" && ".join(steps))
        self.assert_equal(ret_code, 0, "Upstream git repo must be pulled successfully")
    
    def post_configuration_steps(self):
        pass
    
    def pre_deployment_steps(self):
        pass
    
    def deployment_steps(self):
        self.log_info("Deploying")
        steps = [
            "cd %s" % self.config.application_name,
            "git push"
        ]
        if self.get_run_mode() == "OnPremise":
            ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(steps), False, 1200)
        else:
            ( ret_code, ret_output ) = common.command_getstatusoutput(" && ".join(steps))
        self.assert_equal(ret_code, 0, "Git push operation must be successfull")
        return ( ret_code, ret_output )
    
    def post_deployment_steps(self):
        pass
    
    def verification(self):
        self.log_info("Verifying")
        sleep(30) # Waiting 30 seconds before checking
        ret_code = common.check_web_page_output(
            self.config.application_name,
            self.config.page,
            self.config.page_pattern                                    
        )
        self.assert_equal(ret_code, 0, "Pattern %s must be found" % self.config.page_pattern)
        
    def test_method(self):
        #
        # Step 1. Configuration
        #
        self.pre_configuration_steps()
        self.configuration_steps()
        self.post_configuration_steps()
        #
        # Step 2. Deployment
        #
        self.pre_deployment_steps()
        self.deployment_steps()
        self.post_deployment_steps()
        #
        # Step 3. Verification
        #
        self.verification()
        #
        # Everything is fine: PASSED
        #
        return self.passed(self.config.summary)
