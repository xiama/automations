#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com

[US2282][BusinessIntegration] MIN_GEAR setting in cartridge [jbossas]
https://tcms.engineering.redhat.com/case/173957/
"""

import rhtest
import common
import time

class OpenShiftTest(rhtest.Test):
    ITEST = "DEV"

    def initialize(self):
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = 'php'
        self.app_name = common.getRandomString(10)
        self.summary = "[US2282][BusinessIntegration] MIN_GEAR setting in cartridge"

    	common.env_setup()

    def finalize(self):
        self.change_descriptor(1)

class ScalingMinGears(OpenShiftTest):
    
    def change_descriptor(self, num = 1):
        ( ret_code, ret_output ) = common.run_remote_cmd_as_root(
            "sed -i -e 's/Min: ./Min: %d/' /usr/libexec/openshift/cartridges/%s/info/manifest.yml" % ( num, common.app_types[self.app_type] )
        )
        if self.get_run_mode() == "OnPremise":
            cmd="service openshift-broker restart"
        else:
            cmd="service rhc-broker restart"
        if ret_code == 0:
            ( ret_code, ret_output ) = common.run_remote_cmd_as_root(cmd)
        return ret_code

    def test_method(self):
        self.info("===============================")
        self.info("1. Changing MIN_GEAR settings in the cartridge descriptor file")
        self.info("===============================")
        status = self.change_descriptor(3)
        self.assert_equal(status, 0, "Error during manipulating with manifest.yml")

        # Wait for rhc-broker to start
        time.sleep(15)
        
        self.info("===============================")
        self.info("2. Creating a scalable application")
        self.info("===============================")
        status = common.create_app(self.app_name, common.app_types[self.app_type], scalable = True, clone_repo = False, timeout=360)
        self.assert_equal(status, 0, "Unable to create an app")
        
        self.info("===============================")
        self.info("3. Checking the number of gears")
        self.info("===============================")
        ( gear_info, gear_count ) = self.config.rest_api.get_gears(self.app_name)
        self.assert_equal(gear_count, 4, "Gear count must be 4")
        
        self.info("===============================")
        self.info("4. Scaling down")
        self.info("===============================")
        (status, resp) = self.config.rest_api.app_scale_down(self.app_name)
        self.assert_match(status, 'Unprocessable Entity', "Scale-down operation must fail")
        
        # Everything is OK
        return self.passed(self.summary)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ScalingMinGears)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
