"""
Michal Zimen
mzimen@redhat.com
Sept 24, 2012

[US2105][US2110][US1386][[Runtime][cartridge]Control embedded Metrics
https://tcms.engineering.redhat.com/case/167565/?from_plan=4962
"""

import common
import rhtest
import OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = '[US1386][Runtime][cartridge]Control embedded Metrics'
        
        try:
            test_name = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `php` as default")
            test_name = 'php'

        self.info("VARIANT: %s"%test_name)
        self.app_type = common.app_types[test_name]
        self.app_name =  common.getRandomString(10)

        common.env_setup()

    def finalize(self):
        pass

class MetricsControlEmbededCartridge(OpenShiftTest):
    def verify(self, str2verify):
        url = OSConf.get_app_url(self.app_name)+"/metrics/"
        return common.grep_web_page(url, str2verify)

    def test_method(self):
        self.add_step("Creating an application",
            common.create_app,
            function_parameters = [ self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False  ],
            expect_description = 'The app should be created successfully',
            expect_return = 0)

        self.add_step('Embedding Metrics to the application',
            common.embed,
            function_parameters = [ self.app_name, 
                                    'add-%s' % ( common.cartridge_types['metrics']), 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd ],
            expect_description = 'Metrics cartridge should be embedded successfully',
            expect_return = 0)

        self.add_step(
            'Ensuring the web page is available',
            self.verify,
            function_parameters = [ "App Resource Data"],
            expect_description = 'Metrics should be started',
            expect_return = 0)


        self.add_step(
            'Stopping Metrics',
            'rhc cartridge stop %s -a %s -l %s -p %s %s' % (           common.cartridge_types['metrics'], 
                                                                    self.app_name,
                                                                    self.config.OPENSHIFT_user_email, 
                                                                    self.config.OPENSHIFT_user_passwd,
                                                                    common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'Metrics should be stopped',
            expect_return = 0)

        self.add_step(
            'Ensuring the app is not available',
            self.verify,
            function_parameters = ["Service Temporarily"],
            expect_description = 'Metrics should be stopped',
            expect_return = 0 )

        self.add_step(
            'Restarting Metrics',
            "rhc cartridge restart %s -a %s -l %s -p '%s' %s" % (  common.cartridge_types['metrics'], 
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email, 
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'Metrics should be started',
            expect_return = 0)

        self.add_step(
            'Ensuring the right status message of the started instance',
            self.verify,
            function_parameters = ["App Resource Data"],
            expect_description = 'Metrics should be started',
            try_count=3,
            try_interval=10,
            expect_return = 0)

        self.add_step(
            'Removing Metrics cartridge',
            "rhc cartridge remove %s -a %s -l %s -p '%s' --confirm %s" % (   common.cartridge_types['metrics'],
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email, 
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'The Metrics cartridge should be removed',
            expect_return = 0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MetricsControlEmbededCartridge)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
