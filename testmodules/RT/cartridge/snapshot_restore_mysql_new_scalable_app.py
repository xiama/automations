#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Jun 27, 2012
[US2003][RT]Snapshot and restore MySQL data to new scalable jbossas-7 app
[US2003][RT]Snapshot and restore MySQL data to new scalable jbosseap-6 app
[US2004][RT]Snapshot and restore MySQL data to new scalable php-5.3 app
[US2004][RT]Snapshot and restore MySQL data to new scalable perl-5.10 app
[US2005][RT]Snapshot and restore MySQL data to new scalable python-2.6 app
[US2006][RT]Snapshot and restore MySQL data to new scalable ruby-1.8 app
[US2006][RT]Snapshot and restore MySQL data to new scalable ruby-1.9 app
[US2007][RT]Snapshot and restore MySQL data to new scalable nodejs-0.6 app
[US2513][cartridge]snapshot and restore mysql in a new scaling app - jbossEWS
"""
import common, testcase, OSConf
import rhtest
import subprocess, commands
import re, os, time
PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    ITEST = ['DEV', 'INT', 'STG']
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

    def initialize(self):
        self.steps_list = []
        self.summary = """[US2003][RT]Snapshot and restore MySQL data to new scalable jbossas-7 app
[US2003][RT]Snapshot and restore MySQL data to new scalable jbosseap-6 app
[US2004][RT]Snapshot and restore MySQL data to new scalable php-5.3 app
[US2004][RT]Snapshot and restore MySQL data to new scalable perl-5.10 app
[US2005][RT]Snapshot and restore MySQL data to new scalable python-2.6 app
[US2006][RT]Snapshot and restore MySQL data to new scalable ruby-1.8 app
[US2006][RT]Snapshot and restore MySQL data to new scalable ruby-1.9 app
[US2007][RT]Snapshot and restore MySQL data to new scalable nodejs-0.6 app"""
        try:
            self.test_variant = self.config.test_variant
        except:
            self.test_variant = "jbossas"
        self.domain_name = common.get_domain_name()
        self.app_name = "snapshot" + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = self.app_name
        common.env_setup()

    def finalize(self):
        pass


class SnapshotRestoreMysqlScalableTest(OpenShiftTest):

    def modify_app(self):
        self.app_uuid = OSConf.get_app_uuid(self.app_name)
        self.mysql_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["username"]
        self.mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["password"]
        self.mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["database"]
        self.mysql_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["url"]
        self.mysql_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["port"]
        if self.test_variant in ("jbossas","jbosseap","jbossews", "jbossews2"):
            cmd = "cd '%s/src/main/webapp/' &&  cp '%s/app_template/bigdata/mysql/mysql.jsp' . && mkdir WEB-INF/lib && cp '%s/app_template/bigdata/mysql/mysql-connector-java-5.1.20-bin.jar' WEB-INF/lib && sed -i -e 's/#host/%s/g' mysql.jsp && sed -i -e 's/#port/%s/g' mysql.jsp && sed -i -e 's/#dbname/%s/g' mysql.jsp && sed -i -e 's/#user/%s/g' mysql.jsp && sed -i -e 's/#passwd/%s/g' mysql.jsp && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "python":
            cmd = "cd '%s/wsgi/' && cp '%s/app_template/bigdata/mysql/application' . && sed -i -e 's/#host/%s/g' application && sed -i -e 's/#port/%s/g' application && sed -i -e 's/#dbname/%s/g' application && sed -i -e 's/#user/%s/g' application && sed -i -e 's/#passwd/%s/g' application && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "php":
            cmd = "cd '%s/php/' && cp '%s/app_template/bigdata/mysql/mysql.php' . && sed -i -e 's/#host/%s/g' mysql.php && sed -i -e 's/#port/%s/g' mysql.php && sed -i -e 's/#dbname/%s/g' mysql.php && sed -i -e 's/#user/%s/g' mysql.php && sed -i -e 's/#passwd/%s/g' mysql.php && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "perl":
            cmd = "cd '%s/perl/' && cp '%s/app_template/bigdata/mysql/mysql.pl' . && sed -i -e 's/#host/%s/g' mysql.pl && sed -i -e 's/#port/%s/g' mysql.pl && sed -i -e 's/#dbname/%s/g' mysql.pl && sed -i -e 's/#user/%s/g' mysql.pl && sed -i -e 's/#passwd/%s/g' mysql.pl && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "nodejs":
            cmd = "cd '%s/' && cp '%s/app_template/bigdata/mysql/server.js' . && sed -i -e 's/#host/%s/g' server.js && sed -i -e 's/#port/%s/g' server.js && sed -i -e 's/#dbname/%s/g' server.js && sed -i -e 's/#user/%s/g' server.js && sed -i -e 's/#passwd/%s/g' server.js && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "ruby" or self.test_variant == "ruby-1.9":
            cmd = "cd '%s/' && cp %s/app_template/bigdata/mysql/{config.ru,Gemfile} . ; bundle check ; bundle install ; sed -i -e 's/#host/%s/g' config.ru && sed -i -e 's/#port/%s/g' config.ru && sed -i -e 's/#dbname/%s/g' config.ru && sed -i -e 's/#user/%s/g' config.ru && sed -i -e 's/#passwd/%s/g' config.ru && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        (ret, output) = common.command_getstatusoutput(cmd)
        return ret

    def modify_app2(self):
        self.mysql_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["username"]
        self.mysql_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["password"]
        self.mysql_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["database"]
        self.mysql_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["url"]
        self.mysql_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mysql"]]["port"]
        if self.test_variant in ("jbossas","jbosseap","jbossews", "jbossews2"):
            cmd = "cd '%s/src/main/webapp/' && git pull && cp '%s/app_template/bigdata/mysql/mysql.jsp' . && sed -i -e 's/#host/%s/g' mysql.jsp && sed -i -e 's/#port/%s/g' mysql.jsp && sed -i -e 's/#dbname/%s/g' mysql.jsp && sed -i -e 's/#user/%s/g' mysql.jsp && sed -i -e 's/#passwd/%s/g' mysql.jsp && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "python":
            cmd = "cd '%s/wsgi/' && git pull && cp '%s/app_template/bigdata/mysql/application' . && sed -i -e 's/#host/%s/g' application && sed -i -e 's/#port/%s/g' application && sed -i -e 's/#dbname/%s/g' application && sed -i -e 's/#user/%s/g' application && sed -i -e 's/#passwd/%s/g' application && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "php":
            cmd = "cd '%s/php/' && git pull && cp '%s/app_template/bigdata/mysql/mysql.php' . && sed -i -e 's/#host/%s/g' mysql.php && sed -i -e 's/#port/%s/g' mysql.php && sed -i -e 's/#dbname/%s/g' mysql.php && sed -i -e 's/#user/%s/g' mysql.php && sed -i -e 's/#passwd/%s/g' mysql.php && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "perl":
            cmd = "cd '%s/perl/' && git pull && cp '%s/app_template/bigdata/mysql/mysql.pl' . && sed -i -e 's/#host/%s/g' mysql.pl && sed -i -e 's/#port/%s/g' mysql.pl && sed -i -e 's/#dbname/%s/g' mysql.pl && sed -i -e 's/#user/%s/g' mysql.pl && sed -i -e 's/#passwd/%s/g' mysql.pl && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "nodejs":
            cmd = "cd '%s/' && git pull && cp '%s/app_template/bigdata/mysql/server.js' . && sed -i -e 's/#host/%s/g' server.js && sed -i -e 's/#port/%s/g' server.js && sed -i -e 's/#dbname/%s/g' server.js && sed -i -e 's/#user/%s/g' server.js && sed -i -e 's/#passwd/%s/g' server.js && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        elif self.test_variant == "ruby" or self.test_variant == "ruby-1.9":
            cmd = "cd '%s/' && git pull && cp %s/app_template/bigdata/mysql/config.ru . ; bundle check ; bundle install ; sed -i -e 's/#host/%s/g' config.ru && sed -i -e 's/#port/%s/g' config.ru && sed -i -e 's/#dbname/%s/g' config.ru && sed -i -e 's/#user/%s/g' config.ru && sed -i -e 's/#passwd/%s/g' config.ru && git add . && git commit -amt && git push" % (self.git_repo, OpenShiftTest.WORK_DIR, self.mysql_host, self.mysql_port, self.mysql_dbname, self.mysql_user, self.mysql_passwd)
        (ret, output) = common.command_getstatusoutput(cmd)
        return ret
        

    def insert_data(self, size):
        self.app_url = OSConf.get_app_url(self.app_name)
        size = str(size)
        url_suffix = {  "jbossas"   :   "/mysql.jsp?action=insert&size=%s" % (size),
                        "python"    :   "/insert?size=%s" % (size),
                        "php"       :   "/mysql.php?action=insert&size=%s" % (size),
                        "perl"      :   "/mysql.pl?action=insert&size=%s" % (size),
                        "nodejs"    :   "/insert?size=%s" % (size),
                        "ruby"      :   "/mysql?action=insert&size=%s" % (size),
        }
        url_suffix["jbosseap"] = url_suffix["jbossas"]
        url_suffix["jbossews"] = url_suffix["jbossas"]
        url_suffix["jbossews2"] = url_suffix["jbossas"]
        url_suffix["ruby-1.9"] = url_suffix["ruby"]
        url = self.app_url + url_suffix[self.test_variant]
        ret = common.grep_web_page(url, "%s records have been inserted into mysql" % (size), "-H 'Pragma: no-cache' -L", 5, 8)
        return ret

    def delete_data(self):
        url_suffix = {  "jbossas"   :   "/mysql.jsp?action=delete",
                        "python"    :   "/delete",
                        "php"       :   "/mysql.php?action=delete",
                        "perl"      :   "/mysql.pl?action=delete",
                        "nodejs"    :   "/delete",
                        "ruby"      :   "/mysql?action=delete",
        }
        url_suffix["jbosseap"] = url_suffix["jbossas"]
        url_suffix["jbossews"] = url_suffix["jbossas"]
        url_suffix["jbossews2"] = url_suffix["jbossas"]
        url_suffix["ruby-1.9"] = url_suffix["ruby"]
        url = self.app_url + url_suffix[self.test_variant]
        ret = common.grep_web_page(url, "All the records have been deleted from mysql database", "-H 'Pragma: no-cache' -L", 5, 8)
        return ret

    def check_data(self, regex):
        url_suffix = {  "jbossas"   :   "/mysql.jsp?action=show",
                        "python"    :   "/show",
                        "php"       :   "/mysql.php?action=show",
                        "perl"      :   "/mysql.pl?action=show",
                        "nodejs"    :   "/show",
                        "ruby"      :   "/mysql?action=show",
        }
        url_suffix["jbosseap"] = url_suffix["jbossas"]
        url_suffix["jbossews"] = url_suffix["jbossas"]
        url_suffix["jbossews2"] = url_suffix["jbossas"]
        url_suffix["ruby-1.9"] = url_suffix["ruby"]
        url = self.app_url + url_suffix[self.test_variant]
        ret = common.grep_web_page(url, regex, "-H 'Pragma: no-cache' -L", 5, 8, True)
        return ret

    def test_method(self):
        size = 10
        # 1. Create app
        self.steps_list.append(testcase.TestCaseStep("Create an %s app: %s" % (self.test_variant, self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", True],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 2. Embed mysql to it
        self.steps_list.append(testcase.TestCaseStep("Embed mysql-5.1 to it",
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="mysql should be embedded successfully",
                expect_return=0))
        # 3. Copy the sample app to git repo and git push
        self.steps_list.append(testcase.TestCaseStep("Copy the sample app to git repo and git push",
                self.modify_app,
                expect_description="The git repo should be modified and git push",
                expect_return=0))
        # 4. Visit the 'insert' page to insert data into mysql
        self.steps_list.append(testcase.TestCaseStep("Visit the 'insert' page to insert data into mysql",
                self.insert_data,
                function_parameters=[size],
                expect_description="The data should be inserted into mysql",
                expect_return=0))
        # 5. Check the data has been inserted
        self.steps_list.append(testcase.TestCaseStep("Check the data has been inserted",
                self.check_data,
                function_parameters=[[r"There are \d+ records in database", r"This is testing data for testing snapshoting and restoring big data in mysql database"],],
                expect_description="The data should be inserted into mysql",
                expect_return=0))
        # 6. Save snapshot of the app
        self.steps_list.append(testcase.TestCaseStep("Save snapshot of the app",
                "rhc snapshot save %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="Snapshot should be saved",
                expect_return=0))
        # 7.Destroy the app 
        self.steps_list.append(testcase.TestCaseStep("Destroy the app",
                common.destroy_app,
                function_parameters=[self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True],
                expect_description="The app should be destroyed",
                expect_return=0))
        # 8. Create a new app
        self.steps_list.append(testcase.TestCaseStep("Create a new %s app: %s" % (self.test_variant, self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", True],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 9. Embed mysql to the new app
        self.steps_list.append(testcase.TestCaseStep("Embed mysql-5.1 to the new app",
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="mysql should be embedded successfully",
                expect_return=0))
        # 10. Use the tarball to restore the new app
        self.steps_list.append(testcase.TestCaseStep("Use the tarball to restore the new app",
                "sleep 10 ; rhc snapshot restore %s -f %s.tar.gz -l %s -p '%s' %s" % (self.app_name, self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="The data should be restored",
                expect_return=0))
        # 11. Modify the new app
        #self.steps_list.append(testcase.TestCaseStep("Copy the sample app to git repo and git push",
        #        self.modify_app2,
        #        expect_description="The git repo should be modified and git push",
        #        expect_return=0))
        # 
        # No need to modify the new app now, since the MySql info will be fetched via env vars.
        # Otherwise, auto jobs will fail since git-push will do nothing.
        # 12. Check the data to see if it's restored
        self.steps_list.append(testcase.TestCaseStep("Check the data to see if it's restored",
                self.check_data,
                function_parameters=[["There are \d+ records in database", "This is testing data for testing snapshoting and restoring big data in mysql database"],],
                expect_description="The data should be restored",
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreMysqlScalableTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
