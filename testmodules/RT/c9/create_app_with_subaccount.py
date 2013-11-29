#!/usr/bin/python
#
#  File name: create_app_with_subaccount.py
#  Date:      2012/08/31 13:49
#  Author:    mzimen@redhat.com
#

import common
import rhtest


class OpenShiftTest(rhtest.Test):
    ITEST = ["DEV"]

    def initialize(self):
        self.info("create_app_with_subaccount.py")
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        self.info("VARIANT: %s"%self.test_variant)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.sub_account = common.getRandomString(10)+"@redhat.com"
        self.sub_domain = common.getRandomString(10)
        self.app_name = common.getRandomString(10)
        common.env_setup()


    def finalize(self):
        pass


class CreateAppWithSubaccount(OpenShiftTest):
    def test_method(self):
        self.info("Setting up C9 environment")
        ret = common.setup_c9_environment()
        self.assert_equal(ret, 0, "Error during setup C9 environment")
        ############################################
        ############################################
        self.info("Creating a sub domain")
        ret = common.create_subdomain(self.sub_domain,
                                      self.sub_account,
                                      self.user_email,
                                      self.user_passwd)
        self.assert_equal(ret, 0, "Error during create subaccount/subdomain")
        ############################################
        ############################################
        self.info("Adding ssh key for subaccount")
        (ret, output) = common.add_sshkey4sub_account(self.sub_account)
        self.assert_equal(0, ret, "Unable to add sshkey for subaccount:%s"%output)
        ############################################
        ############################################
        self.info("Creating an app under sub_account[%s]"%self.sub_account)
        (ret, app_output) = common.create_app_using_subaccount(self.sub_domain,
                                                self.sub_account,
                                                self.app_name,
                                                common.app_types[self.test_variant],
                                                self.user_email,
                                                self.user_passwd)
        self.assert_equal(ret, 0, "Error creating app under subaccount/subdomain: %s"%app_output)
        ############################################
        ############################################
        self.info("Getting source by git clone")
        cmd = "git clone %s "%(app_output['data']['git_url'])
        (status, output) = common.command_getstatusoutput(cmd, quiet=True)
        self.assert_equal(0, status, "Unable to do git clone...%s"%output)
        ############################################
        ############################################
        self.info("SSH to the app")
        cmd = "ssh %s ls -l"%(app_output['data']['ssh_url'].replace("ssh://",""))
        (status, output) = common.command_getstatusoutput(cmd, quiet=True)
        self.assert_equal(0, status, "Unable to ssh to app...%s"%output)
        self.assert_true((output.find(self.test_variant) >= 0), "Unable to ssh to the app.")
        ############################################
        ############################################
        self.info("Checking app's web page")
        url = app_output['data']['app_url']
        status = common.grep_web_page(url, "OpenShift")
        self.assert_equal(0, status, "Error checking app's web page.")

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateAppWithSubaccount)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of create_app_with_subaccount.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
