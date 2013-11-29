#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Aug 1, 2012
"""

import rhtest
import common


class JBossEAP(rhtest.Test):
    def log_info(self, message):
        self.info('=' * 80)
        self.info(message)
        self.info('=' * 80)

    def initialize(self):
        self.application_name = common.getRandomString()
        self.summary = '[US2307][RT] Create and Control on-scalingJbossEAP6 App'


    def finalize(self):
        pass


    def mysql_status(self):
        cmd = ("rhc cartridge status -a %s -c %s "
               " -l %s -p '%s' %s") % (self.application_name, 
                                    common.cartridge_types['mysql'], 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd,
                                    common.RHTEST_RHC_CLIENT_OPTIONS)
        return common.command_getstatusoutput(cmd)


    def test_method(self):
        # Creation
        self.log_info('Creating application')
        common.create_app(
            self.application_name,
            common.app_types['jbosseap'],
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd)
        self.assert_equal(common.check_web_page_output(self.application_name), 0)

        # Deployment
        self.log_info('Modifying git repo')
        random_value = common.getRandomString()
        jsp_file = open(self.application_name + '/src/main/webapp/test.jsp', 'w')
        jsp_file.write(random_value)
        jsp_file.close()

        configuration_steps = [
            'cd %s' % self.application_name,
            'git add .',
            'git commit -a -m testing',
            'git push'
        ]
        self.assert_equal(common.command_get_status(' && '.join(configuration_steps)), 0)
        self.assert_equal(common.check_web_page_output(self.application_name, 
                                                       'test.jsp', 
                                                       random_value), 0)

        # Add MySQL
        self.log_info('Adding MySQL')
        common.embed(self.application_name, 'add-' + common.cartridge_types['mysql'])
        ( ret_code, ret_output ) =  self.mysql_status()
        self.assert_true(ret_output.find('MySQL is running') != -1)

        # Remove MySQL
        self.log_info('Removing MySQL')
        common.embed(self.application_name, 
                     'remove-' + common.cartridge_types['mysql'])
        ( ret_code, ret_output ) = self.mysql_status()
        self.assert_true(ret_output.find("%s" % (common.cartridge_types['mysql'])) != -1, "Failed to find given string in the output")

        # Remove the app
        self.log_info('Removing the app')
        ret_code = common.destroy_app(self.application_name)
        self.assert_equal(ret_code, 0)

        # Everythin is OK
        return self.passed(self.summary)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossEAP)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
