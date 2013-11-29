#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-07-24

[rhc-cartridge]snapshot/restore big data to new app
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
            self.info("WARN: Missing variant, used `php` as default")
            self.test_variant = 'python-2.7'
            #self.test_variant = 'php'
        self.summary = "[rhc-cartridge]snapshot/restore big data to new app"
        self.app_name = self.test_variant.split('-')[0] + "bigdata" + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name)
        self.filesize = 300 # filesize is calculated by MB
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        common.env_setup()

    def finalize(self):
        os.system("rm -f %s*" % (self.app_name))


class BigDataTest(OpenShiftTest):

    def test_method(self):
        self.step("Create %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, common.app_types[self.test_variant], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))

        self.app_url = OSConf.get_app_url(self.app_name)
        self.url_dict = {   "php"   :   {   "create":   "%s/data.php?action=create&size=%s" % (self.app_url, self.filesize),
                                            "delete":   "%s/data.php?action=delete" % (self.app_url),
                                            "show"  :   "%s/data.php?action=show" % (self.app_url)},
                            "jbossas":  {   "create":   "%s/data.jsp?action=create&size=%s" % (self.app_url, self.filesize),
                                            "delete":   "%s/data.jsp?action=delete" % (self.app_url),
                                            "show"  :   "%s/data.jsp?action=show" % (self.app_url)},
                            "perl"  :   {   "create":   "%s/data.pl?action=create&size=%s" % (self.app_url, self.filesize),
                                            "delete":   "%s/data.pl?action=delete" % (self.app_url),
                                            "show"  :   "%s/data.pl?action=show" % (self.app_url)},
                            "python":   {   "create":   "%s/create?size=%s" % (self.app_url, self.filesize),
                                            "delete":   "%s/delete" % (self.app_url),
                                            "show"  :   "%s/show" % (self.app_url)},
                            "ruby"  :   {   "create":   "%s/create?size=%s" % (self.app_url, self.filesize),
                                            "delete":   "%s/delete" % (self.app_url),
                                            "show"  :   "%s/show" % (self.app_url)},
        }
        self.url_dict["jbosseap"] = self.url_dict["jbossas"]
        self.url_dict["jbossews"] = self.url_dict["jbossas"]
        self.url_dict["jbossews-2.0"] = self.url_dict["jbossas"]
        self.url_dict["jbossews-1.0"] = self.url_dict["jbossas"]
        self.url_dict["ruby-1.9"] = self.url_dict["ruby"]
        self.url_dict["python-2.7"] = self.url_dict["python"]

        self.step("Copy sample app to git repo")
        if self.test_variant in ('php'):
            cmd = "cp -f %s/app_template/bigdata/datadir/data.php %s/php/" % (OpenShiftTest.WORK_DIR, self.git_repo)
        elif self.test_variant in ('jbossas', 'jbosseap','jbossews','jbossews-2.0','jbossews-1.0'):
            cmd = "cp -f %s/app_template/bigdata/datadir/data.jsp %s/src/main/webapp/" % (OpenShiftTest.WORK_DIR, self.git_repo)
        elif self.test_variant in ('perl'):
            cmd = "cp -f %s/app_template/bigdata/datadir/data.pl %s/perl/" % (OpenShiftTest.WORK_DIR, self.git_repo)
        elif self.test_variant in ('python','python-2.7'):
            cmd = "cp -f %s/app_template/bigdata/datadir/application %s/wsgi/" % (OpenShiftTest.WORK_DIR, self.git_repo)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            cmd = "cp -f %s/app_template/bigdata/datadir/{config.ru,Gemfile} %s/ && cd %s/ ; bundle check ; bundle install" % (OpenShiftTest.WORK_DIR, self.git_repo, self.git_repo)
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to copy sample app to local git repo")

        self.step("Git push all the changes")
        cmd = "cd %s && git add . && git commit -amt && git push" % (self.git_repo)
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Git push failed")

        self.step("Wait for the app to become available")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, "The bigfile doesnot exist", "-H 'Pragma: no-cache' -L", 5, 4)
        self.assert_equal(ret, 0, "The app doesn't become available in reasonable time")

        # This step may take very long time
        self.step("Access the 'create' page to create a big file")
        self.info("This step may take a very long time")
        url = self.url_dict[self.test_variant]["create"]
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        ret = common.command_get_status(cmd, timeout=-1)

        self.step("Check the bigfile exists")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, "The bigfile exists", "-H 'Pragma: no-cache' -L", 5, 6)
        self.assert_equal(ret, 0, "The bigfile doesn't exist")

        self.step("Take snapshot of the app")
        self.info("This step may take a very long time(more than half an hour). If it hangs forever, please terminate this script and test manually")
        cmd = "rm -f %s.tar.gz ; rhc snapshot save %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        ret = common.command_get_status(cmd, timeout=-1)
        self.assert_equal(ret, 0, "Failed to save snapshot")

        self.step("Destroy the app")
        ret = common.destroy_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True)
        self.assert_equal(ret, 0, "Failed to destroy app: %s" % (self.app_name))

        self.step("Create a new app with the same name")
        ret = common.create_app(self.app_name, common.app_types[self.test_variant], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "Failed to re-create %s app: %s" % (self.app_type, self.app_name))

        self.step("Use the snapshot tarball to restore it")
        self.info("This step may take a very long time. If it hangs forever, please terminate this script and test manually")
        cmd = "rhc snapshot restore %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        ret = common.command_get_status(cmd, timeout=-1)
        self.assert_equal(ret, 0, "Failed to restore the new app")

        self.step("Check if the bigfile is restored")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, "The bigfile exists", "-H 'Pragma: no-cache' -L", 5, 6)
        self.assert_equal(ret, 0, "The bigfile isn't successfully restored")

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(BigDataTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
