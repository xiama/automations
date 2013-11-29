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


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `ruby` as default")
            self.test_variant = 'ruby'
        try:
            self.rails_ver = self.config.tcms_arguments['rails']
        except:
            self.rails_ver = "3.0.16"
        self.summary = "[rhc-cartridge]Ruby / Rails Framework Support ruby-1.8\n[US2123]ruby-1.9 / Rails3.2 Framework Support"
        if "1.9" in self.test_variant:
            self.app_name = "ruby19rails" + common.getRandomString(4)
        else:
            self.app_name = "ruby18rails" + common.getRandomString(4)
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

    def setup(self):
        cmd = "rails -v"
        (ret, output) = common.command_getstatusoutput(cmd, True)
        if ret == 0 and "Rails %s" % (self.rails_ver) in output:
            return 0
        else:
            cmd = "sudo gem uninstall railties actionpack actionmailer activemodel activeresource activerecord activesupport rails -axI ; sudo gem install -v %s rails" % (self.rails_ver)
            (ret, output) = common.command_getstatusoutput(cmd, False)
            return ret

    def test_method(self):
        self.step("Setup rails environment")
        ret = self.setup()
        self.assert_equal(ret, 0, "Failed to setup rails %s environment" % (self.rails_ver))

        time.sleep(5)

        self.step("Create %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))

        self.step("Create new rails application")
        ret = common.command_get_status("rails new %s -f" % (self.git_repo))
        self.assert_equal(ret, 0, "Failed to create rails app")

        if "3.2" in self.rails_ver:
            self.step("Add execjs and therubyracer for rails-3.2 application")
            try:
                f = file("%s/Gemfile" % (self.git_repo), "a")
                f.writelines(["gem 'execjs'\n", "gem 'therubyracer'\n"])
                f.close()
            except IOError, e:
                raise TestFailError, e
            except:
                raise TestFailError, "Unkown exception. Failed to modify Gemfile"

        self.step("Generate rails controller")
        ret = common.command_get_status("cd %s && bundle install && rails generate controller home index" % (self.git_repo, ))
        self.assert_equal(ret, 0, "Failed to generate rails controller")

        self.step("Create home page")
        test_html = common.getRandomString()
        try:
            f = file("%s/app/views/home/index.html.erb" % (self.git_repo), "w")
            f.write(test_html)
            f.close()
        except IOError, e:
            raise TestFailError, e
        except:
            raise TestFailError, "Unkown exception. Failed to modify app/views/home/index.html.erb"

        self.step("Remove public/index.html")
        try:
            os.remove("%s/public/index.html" % (self.git_repo))
        except OSError, e:
            raise TestFailError, e

        self.step("Add controller to config/routes.rb")
        cmd = """sed -i -e '3 i\\\n  root :to => "home#index"' %s/config/routes.rb""" % (self.git_repo)
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to modify config/routes.rb")

        if "3.2" in self.rails_ver:
            cmd = "sed -i -E 's/config.assets.compile = false/config.assets.compile = true/g' %s/config/environments/production.rb" % (self.git_repo)
            ret = common.command_get_status(cmd)
            self.assert_equal(ret, 0, "Failed to modify config/environments/production.rb")

        self.step("Check hardware platform")
        (ret, output) = common.command_getstatusoutput("uname -i")
        self.assert_equal(ret, 0, "Failed to get hardware platform")
        self.hardware_platform = output.strip()

        if self.hardware_platform in ("i386", "i686"):
            self.step("Add sqlite3 libraries to .gitignore")
            try:
                f = file("%s/.gitignore" % (self.git_repo), "a")
                f.write("vendor/bundle/ruby/1.8/gems/sqlite3-*\n")
                f.close()
            except IOError:
                raise TestFailError, e
            except:
                raise TestFailError, "Unkown exception. Failed to modify .gitignore"

        self.step("Git push all the changes")
        ret = common.command_get_status("cd %s && git add . && git commit -amt && git push" % (self.git_repo))
        self.assert_equal(ret, 0, "Git push failed")

        self.step("Check web page via brower")
        self.app_url = OSConf.get_app_url(self.app_name)
        ret = common.grep_web_page(self.app_url, test_html)
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
