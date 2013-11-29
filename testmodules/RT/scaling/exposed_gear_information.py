#!/usr/bin/env python

import common
import rhtest

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1907][BusinessIntegration] Retrive exposed gear information for a scalable app")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.test_variant = "php"
        self.app_type = common.app_types[self.test_variant]
        self.app_name = 'my%s%s' % ( self.test_variant, common.getRandomString() )
        common.env_setup()

    def finalize(self):
        pass


class ExposedGearInformation(OpenShiftTest):
    def verify_gear_info(self, scaled_up = False):
        # Loading gear information
        (gears, number_of_gears) = self.config.rest_api.get_gears(self.app_name)
        if scaled_up:
            expected_number_of_gears = 3
        else:
            expected_number_of_gears = 2

        php_proxy_exposed = True
        for gear in gears:
            for component in gear["components"]:
                if component["name"].startswith("php") and component["proxy_port"] is None and component["proxy_host"] is None:
                    php_proxy_exposed = False

        return (number_of_gears == expected_number_of_gears) and php_proxy_exposed

    def test_method(self):

        self.add_step(
            "Creating a scalable application",
            common.create_scalable_app,
            function_parameters = [ self.app_name, 
                                    self.app_type, 
                                    self.user_email, 
                                    self.user_passwd, 
                                    False],
            expect_description = "The application must be created successfully",
            expect_return = 0)

        self.add_step(
            "Getting and Verifying gear information",
            self.verify_gear_info,
            function_parameters = [ False ],
            expect_description = "Expected number of gears: 2, PHP proxy ports must be exposed",
            expect_return = True) 

        self.add_step(
            "Scaling-up",
            self.config.rest_api.app_scale_up,
            function_parameters = [self.app_name],
            expect_description = "The application must scale-up successfully",
            expect_return = 'OK')

        self.add_step(
            "Getting and Verifying gear information - the application is scaled-up",
            self.verify_gear_info,
            function_parameters = [ True ],
            expect_description = "Expected number of gears: 3, PHP proxy ports must be exposed",
            expect_return = True) 

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ExposedGearInformation)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
