#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com

[US2089][BI] Prohibit cartridges except mysql and jenkins-client from being embedded to a scalable app
https://tcms.engineering.redhat.com/case/145115/
"""
import rhtest
import common
import testcase
import openshift


class ScalingProhibitedCartridges(rhtest.Test):
    def initialize(self):
        self.summary = "[US2089][BI] Prohibit cartridges except mysql and jenkins-client from being embedded to a scalable app"
        common.env_setup()
    
    def finalize(self):
        pass

    def test_method(self):
        
        self.info("===============================================")
        self.info("Creating a scalable application (PHP)")
        self.info("===============================================")
        common.create_app(
            "testapp", 
            common.app_types['php'], 
            self.config.OPENSHIFT_user_email, 
            self.config.OPENSHIFT_user_passwd,
            clone_repo = False,
            scalable = True
        )

        # Dependency
        self.info("===============================================")
        self.info("Creating a Jenkins app (It's a dependency)")
        self.info("===============================================")
        common.create_app(
            "jenkins", 
            common.app_types['jenkins'], 
            self.config.OPENSHIFT_user_email, 
            self.config.OPENSHIFT_user_passwd,
            clone_repo = False 
        )

        for cartridge in common.cartridge_types.keys():
            if cartridge == "mysql" or cartridge == "jenkins" or cartridge == "mongodb":
                expect_return_rest = "Added"
                expect_return_cli = 0
                cartridge_enabled = True
            else:
                expect_return_rest = "Failed to add"
                expect_return_cli = 1
                cartridge_enabled = False
            
            self.info("===============================================")
            self.info("Embedding cartridge via REST API - " + cartridge)
            self.info("===============================================")
            ( status, messages ) = self.config.rest_api.cartridge_add("testapp", common.cartridge_types[cartridge])
            self.assert_true(messages[0]["text"].startswith(expect_return_rest))
            
            # Dependency
            if cartridge_enabled:
                common.command_get_status("rhc cartridge remove %s -a %s -l %s -p '%s' --confirm %s" % (common.cartridge_types[cartridge], "testapp", self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        
            self.info("===============================================")
            self.info("Embedding cartridge in the command line - " + cartridge)
            self.info("===============================================")
            ret_code = common.embed("testapp", "add-" + common.cartridge_types[cartridge])
            self.assert_equal(ret_code, expect_return_cli)
            
            # Cleaning
            if cartridge_enabled:
                common.command_get_status("rhc cartridge remove %s -a %s -l %s -p '%s' --confirm %s" % (common.cartridge_types[cartridge], "testapp", self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))

        # Everything is OK: Passed
        return self.passed(self.summary)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ScalingProhibitedCartridges)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
