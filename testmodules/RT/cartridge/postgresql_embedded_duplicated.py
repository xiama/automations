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
        self.app_name1 =  test_name.split('-')[0]+common.get_random_string(7)
        self.app_name2 =  test_name.split('-')[0]+common.get_random_string(7)
        common.env_setup()


    def finalize(self):
        pass


class PostgresqlControlEmbededCartridge(OpenShiftTest):
    def test_method(self):

        self.add_step("Creating an application",
                      common.create_app,
                      function_parameters = [self.app_name1,
                                             self.app_type,
                                             self.config.OPENSHIFT_user_email,
                                             self.config.OPENSHIFT_user_passwd,
                                             True],
                      expect_description = 'The app should be created successfully',
                      expect_return = 0)

        self.add_step('Embedding PostgreSQL-9.2 to the application',
                      common.embed,
                      function_parameters = [self.app_name1, 
                                             'add-%s' % ( common.cartridge_types['postgresql-9.2']), 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd],
                      expect_description = 'PostgreSQL 9.2 cartridge should be embedded successfully',
                      expect_return = 0)

        self.add_step('Embedding PostgreSQL-8.4 to the application',
                      common.embed,
                      function_parameters = [self.app_name1, 
                                             'add-%s' % ( common.cartridge_types['postgresql']), 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd],
                      expect_description = 'PostgreSQL 8.4 cartridge should not be embedded successfully',
                      expect_return = 1)

        self.add_step("Creating a scalable application",
                      common.create_scalable_app,
                      function_parameters = [self.app_name2, 
                                             self.app_type, 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd, 
                                             True],
                      expect_description = 'The app should be created successfully',
                      expect_return = 0)

        self.add_step('Embedding PostgreSQL-9.2 to the application',
                      common.embed,
                      function_parameters = [self.app_name2, 
                                             'add-%s' % ( common.cartridge_types['postgresql-9.2']), 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd],
                      expect_description = 'PostgreSQL 9.2 cartridge should be embedded successfully',
                      expect_return = 0)

        self.add_step('Embedding PostgreSQL-8.4 to the application',
                      common.embed,
                      function_parameters = [self.app_name2, 
                                             'add-%s' % ( common.cartridge_types['postgresql']), 
                                             self.config.OPENSHIFT_user_email, 
                                             self.config.OPENSHIFT_user_passwd],
                      expect_description = 'PostgreSQL 8.4 cartridge should not be embedded successfully',
                      expect_return = 1)

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
