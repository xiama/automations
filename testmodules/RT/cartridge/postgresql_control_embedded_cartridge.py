"""
Attila Nagy
anagy@redhat.com
Feb 9, 2012

[US1386][Runtime][cartridge]Control embedded PostgreSQL
https://tcms.engineering.redhat.com/case/128839/
"""

import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info ('[US1386][Runtime][cartridge]Control embedded PostgreSQL')
        try:
            test_name = self.get_variant()
        except:
            self.info("Missing variant, used `php` as default")
            test_name = 'php'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        self.app_type = common.app_types[test_name]
        self.app_name =  test_name.split('-')[0]+common.get_random_string(7)
        common.env_setup()


    def finalize(self):
        pass


class PostgresqlControlEmbededCartridge(OpenShiftTest):
    def test_method(self):
        if self.scalable:
            self.add_step("Creating a scalable application",
                          common.create_scalable_app,
                          function_parameters = [self.app_name, 
                                                 self.app_type, 
                                                 self.config.OPENSHIFT_user_email, 
                                                 self.config.OPENSHIFT_user_passwd, 
                                                 True],
                          expect_description = 'The app should be created successfully',
                          expect_return = 0)
        else:
            self.add_step("Creating an application",
                          common.create_app,
                          function_parameters = [self.app_name,
                                                 self.app_type,
                                                 self.config.OPENSHIFT_user_email,
                                                 self.config.OPENSHIFT_user_passwd,
                                                 True],
                          expect_description = 'The app should be created successfully',
                          expect_return = 0)

        self.add_step('Embedding PostgreSQL to the application',
                      common.embed,
                      function_parameters = [self.app_name, 
                                             'add-%s' % ( common.cartridge_types['postgresql']), 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd],
                      expect_description = 'PostgreSQL 8.4 cartridge should be embedded successfully',
                      expect_return = 0)

        self.add_step('Ensuring the right status message of the started instance',
                        "rhc cartridge status %s -a %s -l %s -p '%s' %s"% (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                      expect_description = 'PostgreSQL 8.4 should be started',
                      expect_str = ['Postgres is running'])

        if self.scalable:
            self.add_step('Scale up',
                          common.scale_up,
                          function_parameters= [self.app_name],
                          expect_return = 0)

            self.add_step('Ensuring the right status message of the started instance',
                            'rhc cartridge status %s -a %s -l %s -p %s %s'% (
                            common.cartridge_types['postgresql'],
                            self.app_name,
                            self.config.OPENSHIFT_user_email, 
                            self.config.OPENSHIFT_user_passwd,
                            common.RHTEST_RHC_CLIENT_OPTIONS),
                          expect_description = 'PostgreSQL 8.4 should be started',
                          expect_str = ['Postgres is running'])

            '''self.add_step("Inject app with ENV page",
                             common.inject_app_index_with_env,
                             function_parameters = [self.app_name, self.app_type],
                             expect_return = 0)

               self.add_step("Ensuring the right number of gears used",
                             common.get_num_of_gears_by_web,
                             function_parameters = [self.app_name, self.app_type],
                             expect_description = "PostgreSQL 8.4 should have 2 gears",
                             )
                             #expect_return = 2)'''

        self.add_step('Stopping PostgreSQL',
                        "rhc cartridge stop %s -a %s -l %s -p '%s' %s"% (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description = 'PostgreSQL 8.4 should be stopped',
                        expect_return = 0)

        self.add_step('Ensuring the right status message of the the stopped instance',
                        "rhc cartridge status %s -a %s -l %s -p %s %s" % (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description = 'PostgreSQL 8.4 should be stopped',
                        expect_str = ['Postgres is stopped'])

        self.add_step('Restarting PostgreSQL',
                        'rhc cartridge restart %s -a %s -l %s -p %s %s'% (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description = 'PostgreSQL 8.4 should be started',
                        expect_return = 0)

        self.add_step('Ensuring the right status message of the started instance',
                        "rhc cartridge status %s -a %s -l %s -p '%s' %s"% (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description = 'PostgreSQL 8.4 should be started',
                        expect_str = ['Postgres is running'])

        if self.scalable:
			self.add_step('Inject app with ENV page',
                            common.inject_app_index_with_env,
                            function_parameters = [self.app_name, self.app_type],
                            expect_return = 0)

			self.add_step('Ensuring the right number of gears used',
							common.get_num_of_gears_by_web,function_parameters = [self.app_name, self.app_type],
            			    expect_description = 'PostgreSQL 8.4 should have 2 gears',
            				expect_return = 2)

        self.add_step('Removing PostgreSQL cartridge',
                        "rhc cartridge remove %s -a %s -l %s -p '%s' --confirm %s"% (
                        common.cartridge_types['postgresql'],
                        self.app_name,
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd,
                        common.RHTEST_RHC_CLIENT_OPTIONS),
                        expect_description = 'The PostgreSQL cartridge should be removed',
                        expect_return = 0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PostgresqlControlEmbededCartridge)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
