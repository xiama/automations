"""
Attila Nagy
anagy@redhat.com
Feb 9, 2012

[US1386][Runtime][cartridge]Control embedded PostgreSQL
https://tcms.engineering.redhat.com/case/128839/
"""

import common
import rhtest
import OSConf

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
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "App creation failed")
         
        # Add postgresql-9.2 to the app
        ret = common.embed(self.app_name, 'add-' + common.cartridge_types['postgresql-9.2'])
        self.assert_equal(ret, 0, "Failed to add Postgresql-9.2 to the app")

        #Check the version of cartridge
        cmd = "ssh %s 'psql --version | grep psql '" % (OSConf.get_ssh_url(self.app_name))
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Check Version Failed")

        #Scale up
        if self.scalable:
            ret = common.scale_up(self.app_name)
            self.assert_equal(0, ret, "Unable to scale_up.")

        #Stop
        cmd = "rhc cartridge stop %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Stop failed")

        #Start
        cmd = "rhc cartridge start %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Start failed")

        #Restart
        cmd = "rhc cartridge restart %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Restart failed")

        #Reload
        cmd = "rhc cartridge reload %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Reload failed")

        #Status
        cmd = "rhc cartridge status %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Show status failed")

        #Remove
        cmd = "rhc cartridge remove %s -a %s -l %s -p '%s' %s --confirm" %(common.cartridge_types['postgresql-9.2'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS) 
        (status, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(status, 0, "Remove failed")

        return self.passed()


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
