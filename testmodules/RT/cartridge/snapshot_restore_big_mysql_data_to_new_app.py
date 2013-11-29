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
            self.test_variant = 'php'
        self.summary = "[rhc-cartridge]snapshot/restore big mysql data to new app"
        self.app_name = self.test_variant.split('-')[0] + "bigmysql" + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name)
        self.record_count = 500000 # amount of records to be inserted
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        common.env_setup()

    def finalize(self):
        os.system("rm -f %s*" % (self.app_name))


class BigMysqlDataTest(OpenShiftTest):

    def test_method(self):
        self.step("Create %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, common.app_types[self.test_variant], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))

        self.app_url = OSConf.get_app_url(self.app_name)
        self.url_dict = {   "php"   :   {   "insert":   "%s/mysql.php?action=insert&size=%s" % (self.app_url, self.record_count),
                                            "delete":   "%s/mysql.php?action=delete" % (self.app_url),
                                            "show"  :   "%s/mysql.php?action=show" % (self.app_url)},
                            "jbossas":  {   "insert":   "%s/mysql.jsp?action=insert&size=%s" % (self.app_url, self.record_count),
                                            "delete":   "%s/mysql.jsp?action=delete" % (self.app_url),
                                            "show"  :   "%s/mysql.jsp?action=show" % (self.app_url)},
                            "perl"  :   {   "insert":   "%s/mysql.pl?action=insert&size=%s" % (self.app_url, self.record_count),
                                            "delete":   "%s/mysql.pl?action=delete" % (self.app_url),
                                            "show"  :   "%s/mysql.pl?action=show" % (self.app_url)},
                            "python":   {   "insert":   "%s/insert?size=%s" % (self.app_url, self.record_count),
                                            "delete":   "%s/delete" % (self.app_url),
                                            "show"  :   "%s/show" % (self.app_url)},
                            "ruby"  :   {   "insert":   "%s/mysql?action=insert&size=%s" % (self.app_url, self.record_count),
                                            "delete":   "%s/mysql?action=delete" % (self.app_url),
                                            "show"  :   "%s/mysql?action=show" % (self.app_url)},
        }
        self.url_dict["jbosseap"] = self.url_dict["jbossas"]
        self.url_dict["ruby-1.9"] = self.url_dict["ruby"]

        self.step("Embed mysql to the app")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mysql to the app")

        self.step("Copy sample app to git repo and git push")
        #self.mysql_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["username"]
        #self.mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["password"]
        #self.mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["database"]
        #self.mysql_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["url"]
        #self.mysql_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["port"]
        if self.test_variant in ('php'):
            cmd = "cd '%s/php/' && cp -f '%s/app_template/bigdata/mysql/mysql.php' . && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR)
        elif self.test_variant in ('jbossas', 'jbosseap'):
            cmd = "cd '%s/src/main/webapp/' &&  cp -f '%s/app_template/bigdata/mysql/mysql.jsp' . && mkdir WEB-INF/lib && cp -f '%s/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar' WEB-INF/lib && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, OpenShiftTest.WORK_DIR)
        elif self.test_variant in ('perl'):
            cmd = "cd '%s/perl/' && cp -f '%s/app_template/bigdata/mysql/mysql.pl' . && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR)
        elif self.test_variant in ('python'):
            cmd = "cd '%s/wsgi/' && cp -f '%s/app_template/bigdata/mysql/application' . && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            cmd = "cd '%s/' && cp -f %s/app_template/bigdata/mysql/{config.ru,Gemfile} . ; bundle check ; bundle install ; git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR)
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to copy sample app to local git repo and git push")

        self.step("Wait for the app to become available")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, 'There is no record in database', "-H 'Pragma: no-cache' -L", 5, 6)
        self.assert_equal(ret, 0, "The app doesn't become available in reasonable time")

        self.step("Access the 'insert' page to insert a large amount of records into the mysql database")
        self.info("This step may take a very long time")
        url = self.url_dict[self.test_variant]["insert"]
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        ret = common.command_get_status(cmd, timeout=-1)

        time.sleep(220)
        self.step("Check mysql data exists")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, ["There are %s records in database" % (self.record_count), "This is testing data for testing snapshoting and restoring big data in mysql database"],
                                    "-H 'Pragma: no-cache' -L", 5, 6, True)
        self.assert_equal(ret, 0, "The MySQL data doesn't exist")

        self.step("Take snapshot of the app")
        self.info("This step may take a very long time. If it hangs forever, please terminate this script and test manually")
        cmd = "rm -f %s.tar.gz ; rhc snapshot save %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        ret = common.command_get_status(cmd, timeout=-1)
        self.assert_equal(ret, 0, "Failed to save snapshot")

        self.step("Destroy the app")
        ret = common.destroy_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True)
        self.assert_equal(ret, 0, "Failed to destroy app: %s" % (self.app_name))

        self.step("Create a new app with the same name")
        ret = common.create_app(self.app_name, common.app_types[self.test_variant], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "Failed to re-create %s app: %s" % (self.app_type, self.app_name))

        self.step("Embed mysql to the new app")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mysql to the app")

        self.step("Use the snapshot tarball to restore it")
        self.info("This step may take a very long time. If it hangs forever, please terminate this script and test manually")
        cmd = "rhc snapshot restore %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        ret = common.command_get_status(cmd, timeout=-1)
        self.assert_equal(ret, 0, "Failed to restore the new app")

#        self.step("Modify the git repo")
#        self.mysql_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["username"]
#        self.mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["password"]
#        self.mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["database"]
#        self.mysql_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["url"]
#        self.mysql_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["port"]
#        if self.test_variant in ('php'):
#            cmd = "cd '%s/php/' && git pull && cp -f '%s/app_template/bigdata/mysql/mysql.php' . && sed -i -e 's/#host/%s/g' mysql.php && sed -i -e 's/#port/%s/g' mysql.php && sed -i -e 's/#dbname/%s/g' mysql.php && sed -i -e 's/#user/%s/g' mysql.php && sed -i -e 's/#passwd/%s/g' mysql.php && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
#        elif self.test_variant in ('jbossas', 'jbosseap'):
#            cmd = "cd '%s/src/main/webapp/' && git pull &&  cp -f '%s/app_template/bigdata/mysql/mysql.jsp' . && sed -i -e 's/#host/%s/g' mysql.jsp && sed -i -e 's/#port/%s/g' mysql.jsp && sed -i -e 's/#dbname/%s/g' mysql.jsp && sed -i -e 's/#user/%s/g' mysql.jsp && sed -i -e 's/#passwd/%s/g' mysql.jsp && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
#        elif self.test_variant in ('perl'):
#            cmd = "cd '%s/perl/' && git pull && cp -f '%s/app_template/bigdata/mysql/mysql.pl' . && sed -i -e 's/#host/%s/g' mysql.pl && sed -i -e 's/#port/%s/g' mysql.pl && sed -i -e 's/#dbname/%s/g' mysql.pl && sed -i -e 's/#user/%s/g' mysql.pl && sed -i -e 's/#passwd/%s/g' mysql.pl && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
#        elif self.test_variant in ('python'):
#            cmd = "cd '%s/wsgi/' && git pull && cp -f '%s/app_template/bigdata/mysql/application' . && sed -i -e 's/#host/%s/g' application && sed -i -e 's/#port/%s/g' application && sed -i -e 's/#dbname/%s/g' application && sed -i -e 's/#user/%s/g' application && sed -i -e 's/#passwd/%s/g' application && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
#        elif self.test_variant in ('ruby', 'ruby-1.9'):
#            cmd = "cd '%s/' && git pull && cp -f %s/app_template/bigdata/mysql/config.ru . ; bundle check ; bundle install ; sed -i -e 's/#host/%s/g' config.ru && sed -i -e 's/#port/%s/g' config.ru && sed -i -e 's/#dbname/%s/g' config.ru && sed -i -e 's/#user/%s/g' config.ru && sed -i -e 's/#passwd/%s/g' config.ru && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
#        ret = common.command_get_status(cmd)
#        self.assert_equal(ret, 0, "Failed to modify the git repo")

        self.step("Check if the MySQL data is restored")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, ["There are %s records in database" % (self.record_count), "This is testing data for testing snapshoting and restoring big data in mysql database"],
                                    "-H 'Pragma: no-cache' -L", 5, 6, True)
        self.assert_equal(ret, 0, "The MySQL data doesn't exist")

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(BigMysqlDataTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
