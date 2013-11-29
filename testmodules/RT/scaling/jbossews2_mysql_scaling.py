#!/usr/bin/env python
import os, sys
import shutil

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase, common, OSConf
import rhtest
import subprocess

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = 'jbossews2' + common.getRandomString(8)
        try:
            self.app_type = common.app_types[self.get_variant()]
        except:
            self.app_type = common.app_types["jbossews2"]

        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False

        common.env_setup()

    def finalize(self):
        pass



class Jbossews2Mysql(OpenShiftTest):
    def check_mysql_result(self):
        app_url = OSConf.get_app_url(self.app_name)
        common.grep_web_page("%s/mysql.jsp?action=insert&size=10" % (app_url), "records have been inserted into mysql", delay=10, count=12)

        return common.grep_web_page("%s/mysql.jsp?action=show" % (app_url), "This is testing data for testing snapshoting and restoring big data in mysql database", delay=10, count=12)

    def prepare_jsp_file(self):
        try:
            mysql = OSConf.get_embed_info(self.app_name,common.cartridge_types['mysql'])
            self.info(mysql)
        except Exception as e:
            self.error(str(e))
            return False
        # Prepare jsp file
        fr = file("%s/../cartridge/app_template/bigdata/mysql/mysql.jsp" % (WORK_DIR), "r")
        jsp = fr.read()
        fr.close()
        fw = file("%s/src/main/webapp/mysql.jsp" % (self.app_name), "w")
        fw.write(jsp)
        fw.close()
        # Prepare mysql connector
        os.mkdir("%s/src/main/webapp/WEB-INF/lib" % (self.app_name))
        shutil.copyfile("%s/../cartridge/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar" % (WORK_DIR), "%s/src/main/webapp/WEB-INF/lib/mysql-connector-java-5.1.20-bin.jar" % (self.app_name))
        return True

    def test_method(self):
        ret = common.create_app(self.app_name, self.app_type, self.user_email, self.user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "App creation failed")

        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mysql to app")

        ret = self.prepare_jsp_file()
        self.assert_equal(ret, True, "Failed to prepare jsp file and mysql connector")

        ret = common.command_get_status("cd %s && git add . && git commit -amt && git push" % (self.app_name))
        self.assert_equal(ret, 0, "Failed to git push")

        self.assert_equal(self.check_mysql_result(), 0, "Mysql doesn't work")

        if self.scalable:
            ret = common.scale_up(self.app_name)
            self.assert_equal(ret, 0, "Failed to scale up app")

            self.assert_equal(self.check_mysql_result(), 0, "Mysql doesn't work after scale up")

            ret = common.scale_down(self.app_name)
            self.assert_equal(ret, 0, "Failed to scale down app")

            self.assert_equal(self.check_mysql_result(), 0, "Mysql doesn't work after scale down")

        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["mysql"])
        self.assert_equal(ret, 0, "Failed to remove mysql-5.1 from app")

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Jbossews2Mysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
