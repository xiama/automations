#!/usr/bin/env python

"""
Attila Nagy
anag@redhat.com
June 12, 2012

[US1941][runtime][rhc-cartridge]A user not logged in jenkins can not see the build and workspace existed in jenkins [P1]
https://tcms.engineering.redhat.com/case/138302/
"""

import rhtest
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    
    def initialize(self):
        try:
            self.test_variant = common.get_variant()
        except:
            self.info("Test variant is not specified. Using 'php' as default...")
            self.test_variant = "php"
            
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString()
        common.env_setup()  


    def finalize(self):
        if self.test_variant in ( "jbossas", "jbosseap" ):
            if self.config.options.run_mode=="DEV":
                common.change_node_profile("small")
    

class JenkinsAndUserNotLoggedIn(OpenShiftTest):
    def test_method(self):
        self.info("=====================")
        self.info("Creating a Jenkins application")
        self.info("=====================")
        common.create_app("jenkins", common.app_types["jenkins"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, clone_repo = False)
        
        self.info("=====================")
        self.info("Creating an application")
        self.info("=====================")
        common.create_app(self.app_name, common.app_types[self.test_variant], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, clone_repo = False)
        
        if self.test_variant in ( "jbossas", "jbosseap" ):
            if self.config.options.run_mode=="DEV":
                common.change_node_profile("medium")
        
        self.info("=====================")
        self.info("Embedding Jenkins client")
        self.info("=====================")
        common.embed(self.app_name, "add-" + common.cartridge_types["jenkins"])
        
        self.info("=====================")
        self.info("Checking Jenkins URLs")
        self.info("=====================")
        for url in ( OSConf.default.conf["apps"]["jenkins"]["url"], OSConf.default.conf["apps"][self.app_name]["embed"][common.cartridge_types["jenkins"]]["url"] ):
            ret_code = common.grep_web_page(
                   url,
                   [ "Authentication required", r"window.location.replace\('/login" ],
                   "-L -k -H 'Pragma: no-cache'",
                   30, 5          
            )
            self.assert_equal(ret_code, 0, "Login form must be shown")
        
        
        return self.passed("[US1941][runtime][rhc-cartridge]A user not logged in jenkins can not see the build and workspace existed in jenkins [P1]")
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsAndUserNotLoggedIn)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
