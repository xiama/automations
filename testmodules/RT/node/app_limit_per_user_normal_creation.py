import os
import sys
import string
import rhtest
import common


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary= "Application limit per user validation on single/multiple node"
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types["php"]
        self.app_name_prefix = common.getRandomString(5)
        try:
            #self.app_limit_per_user = string.atoi(os.environ["OPENSHIFT_app_limit_per_user"])
            self.app_limit_per_user = self.config.tcms_arguments['app_limit']
            if self.app_limit_per_user == 'auto':
                self.info("Found AUTO -> getting max_gears via REST API")
                self.app_limit_per_user = common.get_max_gears()
        except:
            import traceback
            traceback.print_exc(file=sys.stderr)
            try:
                self.app_limit_per_user = common.get_max_gears()
                # $OPENSHIFT_app_limit_per_user is obsolete
                self.info("Missing tcms_arguments['app_limit'] in config. Used %s as default (obtained from REST API)."%self.app_limit_per_user)
            except Exception as e:
                import traceback
                traceback.print_exc(file=sys.stderr)
                self.abort("Unable to get max_gears per this user: %s"%str(e))
                #self.app_limit_per_user = common.MAX_GEARS

        self.info("Testing limit for user: %s"%self.app_limit_per_user)
        self.app_name = "%s%s" %(self.app_name_prefix, self.app_limit_per_user + 1)
        self.info(self.summary)
        # we need to be sure, that there are no other apps per this account
        common.env_setup() 

    def finalize(self):
        if self.get_run_mode() == "DEV":
            ret = common.set_max_gears(self.user_email, common.DEV_MAX_GEARS)
            if ret != 0:
                self.info("Failed to set max gears back to %d" % (common.DEV_MAX_GEARS))
            else:
                self.info("Successfully set max gears back to %d" % (common.DEV_MAX_GEARS))
        os.system("rm -rf *%s" %self.app_name_prefix)
        for i in range(0, self.app_limit_per_user):
            app_name = "%s%s" %(self.app_name_prefix, i)
            try:
                common.destroy_app(app_name, self.user_email, self.user_passwd)
            except:
                pass

class AppLimitPerUserNormalCreation(OpenShiftTest):

    def create_apps_one_by_one(self, start, end):
        for i in range(start, end):
            app_name = "%s%s" %(self.app_name_prefix, i)
            self.info("Creating app#%d"%i)
            ret = common.create_app(app_name, self.app_type, self.user_email, self.user_passwd, False)
            self.assert_equal(0, ret, "App #%d must be created successfully"%i)
        return 0

    def test_method(self):
        if self.get_run_mode() == 'DEV':
            self.add_step("Set max gear to %d" % (self.app_limit_per_user),
                    common.set_max_gears,
                    function_parameters = [self.user_email, self.app_limit_per_user],
                    expect_return = 0,
                    expect_description = "Max gear should be set successfully")

        self.add_step("Create %s apps one by one according to app_limit_per_user setting" %(self.app_limit_per_user),
                self.create_apps_one_by_one,
                function_parameters = [0, self.app_limit_per_user],
                expect_return = 0,
                expect_description = "Apps should be created successfully")

        self.add_step("Try to create one more app to validate app_limit_per_user",
                "rhc app create %s %s -l %s -p '%s' %s" 
                    %(self.app_name, self.app_type, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return='!0',
                expect_str=["already reached the gear limit of"],
                expect_description="No more app should be created")

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppLimitPerUserNormalCreation)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
