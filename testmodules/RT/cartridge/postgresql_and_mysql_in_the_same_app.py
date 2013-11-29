"""
Attila Nagy
anagy@redhat.com
Feb 9, 2012

[US1386][Runtime][rhc-cartridge]Shouldn't be able to embed PostgreSQL and MySQL in the same app
https://tcms.engineering.redhat.com/case/129309/
"""

import os
import sys

import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary ="[US1386][Runtime][rhc-cartridge]Shouldn't be able to embed PostgreSQL and MySQL in the same app"
        self.testcase_id = 129309
        try:
            test_name = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `php` as default.")
            test_name = 'php'
        self.app_type = common.app_types[test_name]
        self.app_name = 'myTestingApp'
        self.steps= []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class PostgresqlAndMysqlInTheSameApp(OpenShiftTest):
    def test_method(self):
        self.steps.append(testcase.TestCaseStep(
                'Creating an application',
                common.create_app,
                function_parameters = [ self.app_name, self.app_type, 
                                        self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False  ],
                expect_description = 'The app should be created successfully',
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                'Embedding MySQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['mysql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'MySQL cartridge should be embedded successfully',
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                'Embedding PostgreSQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['postgresql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'PostgreSQL 8.4 cartridge should NOT be embedded successfully',
                expect_return = "!0"))

        self.steps.append(testcase.TestCaseStep(
                'Removing MySQL cartrdige',
                common.embed,
                function_parameters = [ self.app_name,
                                        'remove-%s' % ( common.cartridge_types['mysql'] ),
                                        self.config.OPENSHIFT_user_email,
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'MySQL cartrdige should be removed successfully',
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                'Embedding PostgreSQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['postgresql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'PostgreSQL 8.4 cartridge should be embedded successfully',
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                'Embedding MySQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['mysql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'MySQL 5.1 cartridge should NOT be embedded successfully',
                expect_return = "!0"))

        self.steps.append(testcase.TestCaseStep(
                'Embedding Cron',
                common.embed,
                function_parameters = [ self.app_name,
                                        'add-%s' % ( common.cartridge_types['cron'] ),
                                        self.config.OPENSHIFT_user_email,
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'Cron cartridge should be embed successfully',
                expect_return = 0))

        case = testcase.TestCase(self.summary, self.steps)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PostgresqlAndMysqlInTheSameApp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
