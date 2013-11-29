#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-11-09

[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support
https://tcms.engineering.redhat.com/case/138803/
"""
import os
import common
import OSConf
import rhtest
import time
import pexpect

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `python` as default")
            self.test_variant = 'python'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        self.summary = "[origin_runtime#157] check environment variables of postgresql-9.2 embeded app"
        self.app_name = "envvar" + common.getRandomString(6)
        self.app_type = common.app_types[self.test_variant]
        self.cart = common.type_to_cart(self.app_type)
        self.git_repo = "./%s" % (self.app_name)

        common.env_setup()

    def finalize(self):
        pass


class NamespacedEnvVars(OpenShiftTest):
    def get_env_list(self,main_cart,*cart_list):
        postgresql_list = ['OPENSHIFT_POSTGRESQL_DB_SOCKET','OPENSHIFT_POSTGRESQL_DB_PASSWORD','OPENSHIFT_POSTGRESQL_DB_HOST','OPENSHIFT_POSTGRESQL_IDENT','OPENSHIFT_POSTGRESQL_DB_PID','OPENSHIFT_POSTGRESQL_DIR','OPENSHIFT_POSTGRESQL_DB_USERNAME','OPENSHIFT_POSTGRESQL_PATH_ELEMENT','OPENSHIFT_POSTGRESQL_DB_URL','OPENSHIFT_POSTGRESQL_VERSION','OPENSHIFT_POSTGRESQL_DB_PORT','OPENSHIFT_POSTGRESQL_DB_LOG_DIR']
        return postgresql_list

    def check_env_var(self, output, expected_list):
        missing_list = []
        for i in expected_list:
			if output.find(i) == -1:
				missing_list.append(i)
        return missing_list

    def check_app(self, app_name, *cart_list):
        app_url = OSConf.get_app_url(app_name)
        common.grep_web_page(app_url + '/env', "OPENSHIFT_APP_DNS")
        content = common.fetch_page(app_url +'/env')
        expected_list = self.get_env_list(self.cart,*cart_list)
        print "Expected env var list: %s" % (','.join(expected_list))
        missing_list = self.check_env_var(content, expected_list)
        flag = True
        if missing_list != []:
            print "The following env vars are missing:"
            print ', '.join(missing_list)
            flag = False
        return flag

    def test_method(self):
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App creation failed")

        # Add postgresql to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["postgresql-9.2"])
        self.assert_equal(ret, 0, "Failed to add postgresql to app")

        #Trigger env reload
        ret = common.trigger_env_reload(self.git_repo)
        self.assert_equal(ret, True, "Failed to trigger env reload")

        #Check env vars
        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["postgresql-9.2"]))
        self.assert_equal(ret, True, "postgresql env var check failed")

        return self.passed("%s passed" % self.__class__.__name__)



class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NamespacedEnvVars)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
