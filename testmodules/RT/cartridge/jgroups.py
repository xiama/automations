"""
Attila Nagy
anagy@redhat.com
May 4, 2012

[US2114][rhc-cartridge] Update jboss-as7 RPM to include jgroups update for clustering issues
"""

import sys
import subprocess
import os

import rhtest
import testcase
import common
import OSConf
import re
from time import sleep
from shutil import rmtree

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US2114][rhc-cartridge] Update jboss-as7 RPM to include jgroups update for clustering issues"
        self.app_name = "myjboss" + common.getRandomString()

        common.env_setup(cleanup=True)

    def finalize(self):
        rmtree(self.app_name, ignore_errors = True)
    
class JGroupsTest(OpenShiftTest):
        
    def test_method(self):
        #
        # Step 1
        #
        self.info("---------------------------------")
        self.info("1. Create a JBoss application")
        self.info("---------------------------------")
        ret_code = common.create_app(self.app_name, common.app_types["jbossas"], clone_repo = True)
        self.assert_equal(ret_code, 0, "Application must be created successfully")

        #
        # Step 2
        #
        self.info("---------------------------------")
        self.info("2. Deploy testing application")
        self.info("---------------------------------")
        ret_code = self.deploy_jgroups_testing_application("./" + self.app_name)
        self.assert_equal(ret_code, 0, "The application must be deployed successfully")

        # Waiting for the application to stand up
        sleep(30)

        #
        # Step 3
        #
        self.info("---------------------------------")
        self.info("3. Verify JGroups version number")
        self.info("---------------------------------")
        user = OSConf.OSConf()
        user.load_conf()
        app_cache = OSConf.get_apps(user)
        app_url = app_cache[self.app_name]['url']
        self.assert_true(
            int(common.fetch_page(app_url + "/jgroups.jsp")) > 6148,
            "JGroups version must be higher than 3.0.4"
        )

        self.passed(self.summary)


    def deploy_jgroups_testing_application(self, git_repo):

        deployment_steps = [
            "cp -v %s/app_template/jgroups.jsp %s/src/main/webapp/" % ( os.path.dirname(os.path.abspath(__file__)), git_repo ),
            "cd %s" % git_repo,
            "git add .",
            "git commit -a -m testing",
            "git push"
        ]

        return common.command_get_status(" && ".join(deployment_steps))
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JGroupsTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
