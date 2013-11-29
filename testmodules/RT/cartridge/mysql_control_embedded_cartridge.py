"""
Michal Zimen
mzimen@redhat.com
Sept 24, 2012

[US2105][US2110][US1386][[Runtime][cartridge]Control embedded MySQL
https://tcms.engineering.redhat.com/case/167565/?from_plan=4962
"""

import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = '[US1386][Runtime][cartridge]Control embedded MySQL'
        
        try:
            test_name = self.get_variant()
        except:
            self.info("WARN: Missing OPENSHIFT_test_name, used `php` as default")
            test_name = 'php'

        self.info("VARIANT: %s"%test_name)
        self.app_type = common.app_types[test_name]
        self.app_name =  common.getRandomString(10)

        common.env_setup()

    def finalize(self):
        pass

class MysqlControlEmbededCartridge(OpenShiftTest):
    def test_method(self):
        self.add_step("Creating an application",
            common.create_app,
            function_parameters = [ self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False  ],
            expect_description = 'The app should be created successfully',
            expect_return = 0)

        self.add_step('Embedding MySQL to the application',
            common.embed,
            function_parameters = [ self.app_name, 
                                    'add-%s' % ( common.cartridge_types['mysql']), 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd ],
            expect_description = 'MySQL 5.1 cartridge should be embedded successfully',
            expect_return = 0)

        self.add_step(
            'Ensuring the right status message of the started instance',
            "rhc cartridge status %s -a %s -l %s -p '%s' %s" % (   common.cartridge_types['mysql'],
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email, 
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'MySQL 5.1 should be started',
            expect_str = [ 'MySQL is running' ])


        self.add_step(
            'Stopping MySQL',
            "rhc cartridge stop %s -a %s -l %s -p '%s' %s" % (   common.cartridge_types['mysql'],
                                                            self.app_name,
                                                            self.config.OPENSHIFT_user_email, 
                                                            self.config.OPENSHIFT_user_passwd,
                                                            common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'MySQL 5.1 should be stopped',
            expect_return = 0)

        self.add_step(
            'Ensuring the right status message of the the stopped instance',
            "rhc cartridge status %s -a %s -l %s -p '%s' %s" % (   common.cartridge_types['mysql'],
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email, 
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'MySQL 5.1 should be stopped',
            expect_str = [ 'MySQL is stopped' ])

        self.add_step(
            'Restarting MySQL',
            "rhc cartridge restart %s -a %s -l %s -p '%s' %s" % (  common.cartridge_types['mysql'],
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email, 
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'MySQL should be started',
            expect_return = 0)

        self.add_step(
            'Ensuring the right status message of the started instance',
            "rhc cartridge status %s -a %s -l %s -p '%s' %s" % (   common.cartridge_types['mysql'],
                                                                self.app_name,
                                                                self.config.OPENSHIFT_user_email,
                                                                self.config.OPENSHIFT_user_passwd,
                                                                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'MySQL should be started',
            expect_str = [ 'MySQL is running' ])

        self.add_step(
            'Removing MySQL cartridge',
            "rhc cartridge remove %s -a %s -l %s -p '%s' --confirm %s" % ( common.cartridge_types['mysql'],
                                                                        self.app_name,
                                                                        self.config.OPENSHIFT_user_email, 
                                                                        self.config.OPENSHIFT_user_passwd,
                                                                        common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'The MySQL cartridge should be removed',
            expect_return = 0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MysqlControlEmbededCartridge)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
