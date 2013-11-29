#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Feb 14, 2012

[US1386][Runtime][cartridge]Embed PostgreSQL cartridge to {rack, perl, wsgi, php, jbossas, jbossews, nodejs, ruby-1.9} app
https://tcms.engineering.redhat.com/case/128838/
https://tcms.engineering.redhat.com/case/128837/
https://tcms.engineering.redhat.com/case/128836/
https://tcms.engineering.redhat.com/case/128835/
https://tcms.engineering.redhat.com/case/128834/
https://tcms.engineering.redhat.com/case/137725/
"""

import os
import commands

import testcase
import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1386][Runtime][cartridge]Embed PostgreSQL cartridge to {rack, perl, wsgi, php, jbossas, jbosseap, nodejs} app"
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing Variant, using `zend` as default")
            self.test_variant = 'zend'

        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        if self.scalable:
            self.scalable = True

        self.info("VARIANT: %s"%self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.git_repo = './' + self.app_name
        self.random1 = common.getRandomString(30)
        self.random2 = common.getRandomString(30)

        self.steps_list = []

        self.app_config = {
            'php'     : { 'destination' : 'php', 'suffix' : 'php' },
            'zend'     : { 'destination' : 'php', 'suffix' : 'php' },
            'perl'    : { 'destination' : 'perl', 'suffix' : 'pl' },
            'wsgi'    : { 'destination' : 'wsgi/application', 'suffix' : 'py' },
            'python'  : { 'destination' : 'wsgi/application', 'suffix' : 'py' },
            'python-2.7'  : { 'destination' : 'wsgi/application', 'suffix' : 'py' },
            'python-3.3'  : { 'destination' : 'wsgi/application', 'suffix' : 'py' },
            'rack'    : { 'destination' : '', 'suffix' : 'rb' },
            'ruby'    : { 'destination' : '', 'suffix' : 'rb' },
            'ruby-1.9': { 'destination' : '', 'suffix' : 'rb' },
            'jbossas' : { 'destination' : 'src/main/webapp', 'suffix' : 'jsp' },
            'jbosseap': { 'destination' : 'src/main/webapp', 'suffix' : 'jsp' },
            'jbossews': { 'destination' : 'src/main/webapp', 'suffix' : 'jsp' },
            'jbossews2': { 'destination' : 'src/main/webapp', 'suffix' : 'jsp' },
            'nodejs'  : { 'destination' : '', 'suffix' : 'js'}}

        common.env_setup()

    def finalize(self):
        pass

class PostgresqlUsage(OpenShiftTest):

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
                'Creating an application',
                common.create_app,
                function_parameters = [ self.app_name, 
                                        self.app_type, 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd, 
                                        True, self.git_repo, self.scalable],
                expect_description = 'The app should be created successfully',
                expect_return = 0))

        #2
        self.steps_list.append(testcase.TestCaseStep(
                'Embedding PostgreSQL to the application',
                common.embed,
                function_parameters = [ self.app_name, 
                                        'add-%s' % ( common.cartridge_types['postgresql'] ), 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd ],
                expect_description = 'PostgreSQL cartridge should be embedded successfully',
                expect_return = 0))

        #3
        self.steps_list.append(testcase.TestCaseStep(
                'Configuring the application',
                self.app_setup,
                expect_description = "App configuration + deployment should be successfull",
                expect_return = 0))

        #4
        self.steps_list.append(testcase.TestCaseStep(
                'Writing to the database - Step #1',
                self.postgresql_check_webpage_output,
                function_parameters = [ "data1", "Please visit /show\..+ to see the data" ],
                expect_description = "INSERT operation should be successfull",
                expect_return = 0))

        #5
        self.steps_list.append(testcase.TestCaseStep(
                'Checking the output of the database - Step #1',
                self.postgresql_check_webpage_output,
                function_parameters = [ "show", self.random1 ],
                expect_description = "We should get the first random value from the database",
                expect_return = 0))

        #6
        self.steps_list.append(testcase.TestCaseStep(
                'Writing to the database - Step #2',
                self.postgresql_check_webpage_output,
                function_parameters = [ "data2", "Please visit /show\..+ to see the data" ],
                expect_description = "INSERT operation should be successfull",
                expect_return = 0))

        #7
        self.steps_list.append(testcase.TestCaseStep(
                'Checking the output of the database - Step #2',
                self.postgresql_check_webpage_output,
                function_parameters = [ "show", self.random2 ],
                expect_description = "We should get the second random value from the database",
                expect_return = 0))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def app_setup(self):
        user = OSConf.OSConf()
        user.load_conf()
        apps_cache = OSConf.get_apps(user)
        psql_version = common.cartridge_types['postgresql']

        postgresql_url = apps_cache[self.app_name]['embed'][psql_version]['url']
        postgresql_user = apps_cache[self.app_name]['embed'][psql_version]['username']
        postgresql_passwd = apps_cache[self.app_name]['embed'][psql_version]['password']
        postgresql_dbname = apps_cache[self.app_name]['embed'][psql_version]['database']
        postgresql_port = apps_cache[self.app_name]['embed'][psql_version]['port']

        app_setup_steps = [
            "cp -rv %s/app_template/postgresql/%s/* %s/%s" % ( WORK_DIR, self.test_variant, self.git_repo, self.app_config[self.test_variant]['destination'] ),
            "find %s/%s -type f -print | while read file ; do echo 'Editing file: ' $file ; sed -i -e 's/#pgsql_user#/%s/;s/#pgsql_passwd#/%s/;s/#pgsql_dbname#/%s/;s/#pgsql_host#/%s/;s/#pgsql_port#/%s/;s/#str_random1#/%s/;s/#str_random2#/%s/' $file; done" % (self.git_repo, self.app_config[self.test_variant]['destination'], postgresql_user, postgresql_passwd, postgresql_dbname, postgresql_url, postgresql_port, self.random1, self.random2 ), 
            "cd %s" % (self.git_repo),
            "git add %s" % (self.app_config[self.test_variant]['destination'] or '.' ),
            "git commit -a -m deployment",
            "git push" ]

        if self.test_variant in ('ruby', 'ruby-1.9', 'rack'):
            app_setup_steps.insert(3, 'bundle install' )
            app_setup_steps.insert(4, 'bundle check' )
        if self.test_variant == 'nodejs':
            app_setup_steps.insert(3, 'rm -f deplist.txt' )#bug if the pg dependency is there...
        if self.test_variant in ('python-2.7','python-3.3'):
            #app_setup_steps.insert(3, "cp -f  %s/../client/data/snapshot_restore_mysql_data/setuppostgresql.py ./setup.py" % (WORK_DIR))
            app_setup_steps.insert(3, "sed -i -e \"s/#\s*'psycopg2',/'psycopg2',/g\" setup.py")
        
        ( ret_code, ret_output) = commands.getstatusoutput(" && ".join(app_setup_steps))
        print ret_output
        return ret_code

    def postgresql_check_webpage_output(self, path, pattern):
        app_url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page( "%s/%s.%s" % ( app_url, path, self.app_config[self.test_variant]['suffix']), pattern, count=10)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PostgresqlUsage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
