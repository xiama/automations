#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-07-23

[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support
https://tcms.engineering.redhat.com/case/138803/
"""
import os
import common
import OSConf
import rhtest
import time


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `php` as default")
            self.test_variant = 'php'
        self.summary = "[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support"
        self.app_name = "mysqladmin" + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name)
        common.env_setup()

    def finalize(self):
        pass


class MysqlAdminTest(OpenShiftTest):

    def test_method(self):
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App creation failed")
        # Try to embed phpmyadmin without mysql embedded
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["phpmyadmin"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_not_equal(ret, 0, "phpmyadmin shouldn't be embedded before embedding mysql")
        # Embed mysql to it
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mysql to the app")
        # Embed phpmyadmin to it
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["phpmyadmin"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed MySQL Admin(phpmyadmin) to the app")
        # Check phpmyadmin is working properly
        mysql_username = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]['username']
        mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]['password']
        phpadmin_url = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["phpmyadmin"]]['url']
        expected_output = "www.phpMyAdmin.net"
        ret = common.grep_web_page(phpadmin_url, common.raw_str(expected_output), "-k -H 'Pragma: no-cache' -L -u '%s:%s'" % (mysql_username, mysql_passwd), 5, 4)
        self.assert_equal(ret, 0, "phpmyadmin isn't working properly")
        # Remove embedded mysql from the app
        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to remove embedded mysql from the app")
        # Check phpmyadmin isn't removed
        time.sleep(5)
        cmd = "curl -k -H 'Pragma: no-cache' -L -u '%s:%s' %s" % (mysql_username, mysql_passwd, phpadmin_url)
        (ret, output) = common.command_getstatusoutput(cmd, quiet=True)
        self.assert_not_match("404 Not Found", output, "Found '404 Not Found'. phpmyadmin shouldn't be removed")
        # Check mysql database is inaccessable
        expected_outputs = [common.raw_str("phpMyAdmin - Error"),
                            common.raw_str("#2003 - Can't connect to MySQL server on"),
                            common.raw_str("The server is not responding")]
        ret = common.grep_web_page(phpadmin_url, expected_outputs, "-k -H 'Pragma: no-cache' -L -u '%s:%s'" % (mysql_username, mysql_passwd), 5, 4, True)
        self.assert_equal(ret, 0, "phpmyadmin shouldn't be working!!!")
        # Re-embed mysql to the app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to re-embed mysql")
        # Check phpmyadmin is working properly again
        mysql_username = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]['username']
        mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]['password']
        ret = common.grep_web_page(phpadmin_url, common.raw_str(expected_output), "-k -H 'Pragma: no-cache' -L -u '%s:%s'" % (mysql_username, mysql_passwd), 5, 4)
        expected_output = "www.phpMyAdmin.net"
        self.assert_equal(ret, 0, "phpmyadmin isn't working properly after re-embedding mysql")
        # The end
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MysqlAdminTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
