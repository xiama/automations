#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-08-15

[rhc-cartridge]Ruby / Rails Framework Support ruby-1.8
[US2123]ruby-1.9 / Rails3.2 Framework Support
https://tcms.engineering.redhat.com/case/167902/
"""
import os
import common
import OSConf
import rhtest
import time
from helper import get_instance_ip


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `ruby` as default")
            self.test_variant = 'ruby-1.9'
        try:
            self.rails_ver = self.config.tcms_arguments['rails']
        except:
            self.rails_ver = "3.0.16"
        self.summary = "[rhc-cartridge]Ruby / Rails Framework Support ruby-1.8\n[US2123]ruby-1.9 / Rails3.2 Framework Support"
        if "1.9" in self.test_variant:
            self.app_name = "ruby19rails" + common.getRandomString(4)
        else:
            self.app_name = "ruby18rails" + common.getRandomString(4)
        self.domain_name = common.get_domain_name()
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name) 
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        common.env_setup()

    def finalize(self):
        pass


class RubyRailsFrameworkTest(OpenShiftTest):

    def test_method(self):
        instance_ip = get_instance_ip()
        if self.config.options.run_mode == 'DEV':
            instance_ip = 'dev.rhcloud.com'
        self.step("Create a rails application")
        ret = common.command_get_status("rhc app create %s ruby-1.9 postgresql-9.2 --from-code https://github.com/congqiyuan/openshift-rails-example-postgresql.git"%( self.app_name))
        self.assert_equal(ret, 0, "Failed to create rails app")
        '''
        self.step("Add sqlite3 for rails-3.2 application")
        try:
            f = file("%s/Gemfile" % (self.git_repo), "a")
            f.writelines(["gem 'sqlite3'\n"])
            f.close
        except IOError,e:
            raise TestFailError, e
        except:
            raise TestFailError, "Unkown exception. Failed to modify Gemfile"
        '''

        self.step("rails g scaffold Article title author")
        ret = common.command_get_status('cd %s && pwd && bundle install' % (self.git_repo, ))
        self.assert_equal(ret, 0, "Failed to rails g scaffold Article title author")

        self.step("rails g scaffold Article title author")
        ret = common.command_get_status('cd %s && ./script/rails g scaffold Article title author' % (self.git_repo, ))
        self.assert_equal(ret, 0, "Failed to rails g scaffold Article title author")

        self.step("Git push all the changes")
        ret = common.command_get_status("cd %s && git add . && git commit -amt && git push" % (self.git_repo))
        self.assert_equal(ret, 0, "Git push failed")

        self.step("Check web page via brower")
        app_url = "http://%s-%s.%s"% (self.app_name,self.domain_name,instance_ip)
        ret = common.grep_web_page(app_url, "OpenShift")
        self.assert_equal(ret, 0, "Rails app isn't deployed successfully")

        return self.passed()


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RubyRailsFrameworkTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
