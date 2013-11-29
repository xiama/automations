#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Aug 2, 2012
"""
import rhtest
import common
import re
import OSConf

class QuotaTest(rhtest.Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)

    def log_info(self, message):
        self.info('=' * 80)
        self.info(message)
        self.info('=' * 80)

    def initialize(self):
        self.application_name = common.getRandomString()
        self.application_type = common.app_types['php']
        self.summary = '[US1851][Runtime][rhc-node] View Quota info'

    def finalize(self):
        pass
    
    def test_method(self):
        self.log_info('Creating an application')
        common.create_app(
            self.application_name,
            self.application_type,
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd,
            clone_repo = False
        )

        self.log_info("Running command 'quota'")
        ( ret_code, ret_output ) = common.run_remote_cmd(self.application_name, 'quota')
        self.info('Asserting that the return code of the command is 0...')
        self.assert_equal(ret_code, 0)
        self.info('Verifyting the correct output...')
        uuid = OSConf.get_app_uuid(self.application_name)
        match = re.match('Disk quotas for user %s' % uuid, ret_output)
        self.assert_true(match != None)

        # Everything is OK
        self.passed(self.summary)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuotaTest)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
