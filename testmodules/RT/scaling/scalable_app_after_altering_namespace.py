#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-07-26

[US2003,US2004,US2005,US2006,US2007,US2099][Runtime][cartridge]Scalable app after altering domain name
https://tcms.engineering.redhat.com/case/147642/
"""
import os
import re
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
        self.summary = "[US2003,US2004,US2005,US2006,US2007,US2099][Runtime][cartridge]Scalable app after altering domain name"
        self.app_name = common.getRandomString(8)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = self.app_name
        self.record_count = 30 # amount of records to be inserted
        self.domain_name = common.get_domain_name()
        self.new_domain_name = common.getRandomString(10)
        common.env_setup()

    def finalize(self):
        try:
            common.alter_domain(self.domain_name, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
        except:
            pass


class ScalingAfterAlterDomain(OpenShiftTest):

    def test_method(self):
        self.step("Create scalable %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", True)
        self.assert_equal(ret, 0, "Failed to create scalable %s app: %s" % (self.app_type, self.app_name))

        self.step("Embed mysql to the app")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mysql to the app")

        self.step("Copy sample app to git repo and git push")
        self.mysql_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["username"]
        self.mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["password"]
        self.mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["database"]
        self.mysql_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["url"]
        self.mysql_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["port"]
        if self.test_variant in ('php'):
            cmd = ("cd '%s/php/' "
                   " && cp -f '%s/../cartridge/app_template/bigdata/mysql/mysql.php' . "
                   " && sed -i -e 's/#host/%s/g' mysql.php && sed -i -e 's/#port/%s/g' mysql.php "
                   " && sed -i -e 's/#dbname/%s/g' mysql.php "
                   " && sed -i -e 's/#user/%s/g' mysql.php "
                   " && sed -i -e 's/#passwd/%s/g' mysql.php "
                   " && git add . && git commit -amt "
                   " && git push") % (self.git_repo, 
                                     OpenShiftTest.WORK_DIR, 
                                     self.mysql_host, 
                                     self.mysql_port, 
                                     self.mysql_dbname, 
                                     self.mysql_user, 
                                     self.mysql_passwd)
        elif self.test_variant in ('jbossas', 'jbosseap', 'jbossews'):
            cmd = ("cd '%s/src/main/webapp/' "
                   " &&  cp -f '%s/../cartridge/app_template/bigdata/mysql/mysql.jsp' . "
                   " && mkdir WEB-INF/lib "
                   " && cp -f '%s/../cartridge/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar' WEB-INF/lib "
                   " && sed -i -e 's/#host/%s/g' mysql.jsp "
                   " && sed -i -e 's/#port/%s/g' mysql.jsp "
                   " && sed -i -e 's/#dbname/%s/g' mysql.jsp "
                   " && sed -i -e 's/#user/%s/g' mysql.jsp "
                   " && sed -i -e 's/#passwd/%s/g' mysql.jsp "
                   " && git add . "
                   " && git commit -amt "
                   " && git push") % (self.git_repo, 
                                      OpenShiftTest.WORK_DIR, 
                                      OpenShiftTest.WORK_DIR, 
                                      self.mysql_host, 
                                      self.mysql_port, 
                                      self.mysql_dbname, 
                                      self.mysql_user, 
                                      self.mysql_passwd)
        elif self.test_variant in ('perl'):
            cmd = ("cd '%s/perl/' "
                   " && cp -f '%s/../cartridge/app_template/bigdata/mysql/mysql.pl' . "
                   " && sed -i -e 's/#host/%s/g' mysql.pl && sed -i -e 's/#port/%s/g' mysql.pl "
                   " && sed -i -e 's/#dbname/%s/g' mysql.pl "
                   " && sed -i -e 's/#user/%s/g' mysql.pl "
                   " && sed -i -e 's/#passwd/%s/g' mysql.pl "
                   " && git add . "
                   " && git commit -amt "
                   " && git push") % (self.git_repo, 
                                      OpenShiftTest.WORK_DIR, 
                                      self.mysql_host, 
                                      self.mysql_port, 
                                      self.mysql_dbname, 
                                      self.mysql_user, 
                                      self.mysql_passwd)
        elif self.test_variant in ('python'):
            cmd = ("cd '%s/wsgi/' "
                   " && cp -f '%s/../cartridge/app_template/bigdata/mysql/application' . "
                   " && sed -i -e 's/#host/%s/g' application "
                   " && sed -i -e 's/#port/%s/g' application "
                   " && sed -i -e 's/#dbname/%s/g' application "
                   " && sed -i -e 's/#user/%s/g' application "
                   " && sed -i -e 's/#passwd/%s/g' application "
                   " && git add . "
                   " && git commit -amt "
                   " && git push") % (self.git_repo, 
                                      OpenShiftTest.WORK_DIR, 
                                      self.mysql_host, 
                                      self.mysql_port, 
                                      self.mysql_dbname, 
                                      self.mysql_user, 
                                      self.mysql_passwd)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            cmd = ("cd '%s/' "
                   " && cp -f %s/../cartridge/app_template/bigdata/mysql/{config.ru,Gemfile} . "
                   " ; bundle check ; bundle install "
                   " ;  sed -i -e 's/#host/%s/g' config.ru "
                   " && sed -i -e 's/#port/%s/g' config.ru "
                   " && sed -i -e 's/#dbname/%s/g' config.ru "
                   " && sed -i -e 's/#user/%s/g' config.ru "
                   " && sed -i -e 's/#passwd/%s/g' config.ru "
                   " && git add . "
                   " && git commit -amt "
                   " && git push")% (self.git_repo, 
                                     OpenShiftTest.WORK_DIR, 
                                     self.mysql_host, 
                                     self.mysql_port, 
                                     self.mysql_dbname, 
                                     self.mysql_user, 
                                     self.mysql_passwd)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(ret, 0, "Failed to copy sample app to local git repo and git push")


        ret = common.inject_app_index_with_env(self.app_name, self.app_type)
        self.assert_equal(ret, 0, "Failed to inject app by ENV page")

        self.step(("Access the 'insert' page to insert a large amount "
                   "of records into the mysql database"))

        time.sleep(8)

        app_url=OSConf.get_app_url(self.app_name)
        if self.test_variant in ('php'):
            url = "%s/mysql.php?action=insert&size=%s" % (app_url, 
                                                          self.record_count)
        elif self.test_variant in ('jbossas', 'jbosseap', 'jbossews'):
            url = "%s/mysql.jsp?action=insert&size=%s" % (app_url, 
                                                          self.record_count)
        elif self.test_variant in ('perl'):
            url = "%s/mysql.pl?action=insert&size=%s" % (app_url, 
                                                         self.record_count)
        elif self.test_variant in ('python'):
            url = "%s/insert?size=%s" % (app_url, self.record_count)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            url = "%s/mysql?action=insert&size=%s" % (app_url, 
                                                      self.record_count)

        cmd = 'curl -H "Pragma:no-cache" -L "%s"' % (url)
        ret = common.command_get_status(cmd)

        time.sleep(4)

        self.step("Check mysql data exists")
        if self.test_variant in ('php'):
            url = "%s/mysql.php?action=show" % (app_url)
        elif self.test_variant in ('jbossas', 'jbosseap', 'jbossews'):
            url = "%s/mysql.jsp?action=show" % (app_url)
        elif self.test_variant in ('perl'):
            url = "%s/mysql.pl?action=show" % (app_url)
        elif self.test_variant in ('python'):
            url = "%s/show" % (app_url)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            url = "%s/mysql?action=show" % (app_url)
        ret = common.grep_web_page(url, 
                                   ["There are %s records in database" % (self.record_count), 
                                       ("This is testing data for testing "
                                        "snapshoting and restoring big data"
                                        " in mysql database")],
                                   '-H "Pragma:no-cache" -L', 5, 6, True)
        self.assert_equal(ret, 0, "The MySQL data doesn't exist")

        self.step("Scale up the app")
        ret = common.scale_up(self.app_name, self.domain_name)
        self.assert_equal(ret, 0, "Failed to scale up the app")

        self.step("Verify scale up")
        #gear_lst = self.verify_scale_up(url)
        gear_num = common.get_num_of_gears_by_web(self.app_name, self.app_type)
        self.assert_equal(gear_num, 2, "Unable to verify scale up")
        #self.assert_equal(len(gear_lst), 2, 
        #                  "Failed to veryfy scale up. %d gears found" % (len(gear_lst)))

        self.step("Alter domain name")
        ret = common.alter_domain(self.new_domain_name, 
                                  self.config.OPENSHIFT_user_email, 
                                  self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to alter domain")

        time.sleep(10)

        self.step("Modify domain name in program")
        if self.test_variant in ('php'):
            cmd = ("sed -i -e 's/-%s/-%s/g' %s/php/mysql.php "
                   "%s/.git/config") % (self.domain_name, 
                                       self.new_domain_name, 
                                       self.git_repo, 
                                       self.git_repo)
        elif self.test_variant in ('jbossas', 'jbosseap', 'jbossews'):
            cmd = ("sed -i -e 's/-%s/-%s/g' %s/src/main/webapp/mysql.jsp "
                   " %s/.git/config") % (self.domain_name, 
                                         self.new_domain_name, 
                                         self.git_repo, 
                                         self.git_repo)
        elif self.test_variant in ('perl'):
            cmd = ("sed -i -e 's/-%s/-%s/g' %s/perl/mysql.pl "
                   " %s/.git/config") % (self.domain_name, 
                                         self.new_domain_name, 
                                         self.git_repo, 
                                         self.git_repo)
        elif self.test_variant in ('python'):
            cmd = ("sed -i -e 's/-%s/-%s/g' %s/wsgi/application "
                   " %s/.git/config") % (self.domain_name, 
                                         self.new_domain_name, 
                                         self.git_repo, 
                                         self.git_repo)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            cmd = ("sed -i -e 's/-%s/-%s/g' "
                   " %s/config.ru %s/.git/config") % (self.domain_name, 
                                                      self.new_domain_name, 
                                                      self.git_repo, 
                                                      self.git_repo)
        cmd += " && cd %s && git commit -amt && git push" % (self.git_repo)
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to change the domain name in program")

        self.step(("Verify all gears(including mysql) works "
                   "properly after altering domain"))
        app_url = OSConf.get_app_url(self.app_name)
        if self.test_variant in ('php'):
            url = "%s/mysql.php?action=show" % (app_url)
        elif self.test_variant in ('jbossas', 'jbosseap'):
            url = "%s/mysql.jsp?action=show" % (app_url)
        elif self.test_variant in ('perl'):
            url = "%s/mysql.pl?action=show" % (app_url)
        elif self.test_variant in ('python'):
            url = "%s/show" % (app_url)
        elif self.test_variant in ('ruby', 'ruby-1.9'):
            url = "%s/mysql?action=show" % (app_url)
        ret = common.grep_web_page(url,
                                   ["There are %s records in database" % (self.record_count),
                                       ("This is testing data for testing "
                                        "snapshoting and restoring big data"
                                        " in mysql database")],
                                   '-H "Pragma:no-cache" -L', 5, 6, True)
        self.assert_equal(ret, 0, "The MySQL data doesn't exist")
        #gear_lst = self.verify_scale_up(url)
        #self.assert_equal(len(gear_lst), 2, "Failed to veryfy scale up. %d gears found" % (len(gear_lst)))
        gear_num = common.get_num_of_gears_by_web(self.app_name, self.app_type)
        self.assert_equal(gear_num, 2, "Unable to verify scale up")

        return self.passed("%s passed" % self.__class__.__name__)


    ''' Used common function instead!
    def verify_scale_up(self, url, retry_times=10):
        gear_lst = []
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        for i in range(retry_times):
            (ret, output) = common.command_getstatusoutput(cmd, quiet=True)
            if ret != 0:
                time.sleep(3)
            else:
                pattern = re.compile(r'(?<=Gear DNS: ).+com', re.M)
                match = pattern.search(output)
                if match == None:
                    time.sleep(3)
                elif match.group(0) not in gear_lst and output.find("There are %s records in database" % (self.record_count)) != -1:
                    gear_lst.append(match.group(0))
        self.debug("Gears found: " + ' '.join(gear_lst))
        return gear_lst
    '''


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ScalingAfterAlterDomain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
