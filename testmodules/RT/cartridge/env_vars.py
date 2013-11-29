"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012

[US650][Runtime][rhc-cartridge]Environment Variables
https://tcms.engineering.redhat.com/case/138802/
"""

import os,sys,re
import rhtest

import testcase
import common
import OSConf

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US650][Runtime][rhc-cartridge]Environment Variables"

        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `php` as default")
            self.test_variant = 'php'

        self.app_name = common.getRandomString(10)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]

        common.env_setup()

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EnvVars(OpenShiftTest):
    def test_method(self):
        # env vars should be found without mysql embedded
        env_lst = 'OPENSHIFT_LOG_DIR OPENSHIFT_APP_NAME OPENSHIFT_APP_UUID OPENSHIFT_TMP_DIR OPENSHIFT_HOMEDIR OPENSHIFT_REPO_DIR OPENSHIFT_GEAR_NAME OPENSHIFT_INTERNAL_PORT OPENSHIFT_RUN_DIR OPENSHIFT_INTERNAL_IP OPENSHIFT_GEAR_DIR OPENSHIFT_GEAR_TYPE OPENSHIFT_GEAR_DNS OPENSHIFT_DATA_DIR OPENSHIFT_GEAR_UUID'.split()
        # env vars should be found with mysql embedded
        env_mysql_lst = 'OPENSHIFT_DB_HOST OPENSHIFT_LOG_DIR OPENSHIFT_APP_NAME OPENSHIFT_APP_UUID OPENSHIFT_TMP_DIR OPENSHIFT_HOMEDIR OPENSHIFT_REPO_DIR OPENSHIFT_GEAR_NAME OPENSHIFT_INTERNAL_PORT OPENSHIFT_DB_PASSWORD OPENSHIFT_DB_USERNAME OPENSHIFT_RUN_DIR OPENSHIFT_INTERNAL_IP OPENSHIFT_GEAR_DIR OPENSHIFT_GEAR_TYPE OPENSHIFT_GEAR_DNS OPENSHIFT_DB_URL OPENSHIFT_DATA_DIR OPENSHIFT_GEAR_UUID OPENSHIFT_DB_TYPE OPENSHIFT_DB_PORT'.split()
        env_mongodb_lst = 'OPENSHIFT_NOSQL_DB_USERNAME OPENSHIFT_NOSQL_DB_TYPE OPENSHIFT_LOG_DIR OPENSHIFT_APP_NAME OPENSHIFT_APP_UUID OPENSHIFT_NOSQL_DB_URL OPENSHIFT_TMP_DIR OPENSHIFT_HOMEDIR OPENSHIFT_REPO_DIR OPENSHIFT_GEAR_NAME OPENSHIFT_INTERNAL_PORT OPENSHIFT_NOSQL_DB_PASSWORD OPENSHIFT_RUN_DIR OPENSHIFT_NOSQL_DB_PORT OPENSHIFT_INTERNAL_IP OPENSHIFT_GEAR_DIR OPENSHIFT_NOSQL_DB_HOST OPENSHIFT_GEAR_TYPE OPENSHIFT_GEAR_DNS OPENSHIFT_DATA_DIR OPENSHIFT_GEAR_UUID'.split()

        # 1. Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 2. Append cmd 'env' into file '<repo_path>/.openshift/action_hooks/build'
        self.steps_list.append( testcase.TestCaseStep("2.Append cmd 'env' into file '<repo_path>/.openshift/action_hooks/build'",
                "echo '\nenv' >> %s/.openshift/action_hooks/build" % (self.git_repo),
                expect_description="Successfully added 1 line to .openshift/action_hooks/build",
                expect_return=0))

        # 3.copy template to git repo and git push
        if self.test_variant == "wsgi":
            cmd = "cd %s/wsgi && rm -f application && cp -f %s/app_template/env_var/python/application application && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR)
        elif self.test_variant == "php":
            cmd = "cd %s/php && rm -f index.php && cp -f %s/app_template/env_var/php/index.php index.php && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR)
        elif self.test_variant == "perl":
            cmd = "cd %s/perl && rm -f index.pl && cp %s/app_template/env_var/perl/index.pl index.pl && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR)
        elif self.test_variant == "rack":
            cmd = "cd %s && rm -f config.ru && cp %s/app_template/env_var/ruby/config.ru config.ru && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR)
        elif self.test_variant == "nodejs":
            cmd = "cd %s && rm -f server.js && cp %s/app_template/env_var/nodejs/server.js server.js && git add . && git commit -am t && git push" % (self.git_repo, WORK_DIR)
        elif self.test_variant == "jbossas" or self.test_variant == "diy":
            cmd = "cd %s && touch testfile && git add . && git commit -am t && git push" % (self.git_repo)

        self.steps_list.append(testcase.TestCaseStep(
                "3.copy template to git repo and git push",
                cmd,
                output_callback = self.store_output,
                expect_description="Successfully copy template to git repo and git push",
                expect_return=0))

        # 4.Check env vars from the output of git push
        self.steps_list.append(testcase.TestCaseStep(
                "4.Check env vars from the output of git push",
                self.compare,
                function_parameters=[self.get_last_output, env_lst],
                expect_description="The openshift env vars should found in the output of git push",
                expect_return=True))

        if self.test_variant == "jbossas" or self.test_variant == "diy":
            self.info("%s app doesn't need to check the web page" % (self.test_variant))
        else:
        # 5.Fetch the home page of the app

        # 6.Check env vars from the web page
            self.steps_list.append( testcase.TestCaseStep("6.Check env vars from the web page",
                self.compare,
                function_parameters=[self.get_page, env_lst],
                expect_description="The openshift env vars should found in the web page",
                expect_return=True))

        i = 7
        for (cart,lst) in (("mysql-5.1",env_mysql_lst), ("mongodb-2.2",env_mongodb_lst)):
        # 7.Embed database to this app
            self.steps_list.append( testcase.TestCaseStep("%d.Embed %s to this app" % (i,cart),
                common.embed,
                function_parameters=[self.app_name, "add-" + cart, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="%s should be embedded successfully" % (cart),
                expect_return=0))

        # 8.Make some change and git push again
            self.steps_list.append( testcase.TestCaseStep("%d.Make some change and git push again" % (i),
                "cd %s && echo '\n' >> .openshift/action_hooks/build && git add . && git commit -am t && git push" % (self.git_repo),
                output_callback=self.store_output,
                expect_description="Git push should succeed",
                expect_return=0))

        # 9.Check env vars from the output of git push after embedded database
            self.steps_list.append( testcase.TestCaseStep("%d.Check env vars from the output of git push after embedding %s" % (i,cart),
                self.compare,
                function_parameters=[self.get_last_output, lst],
                expect_description="The openshift env vars should found in the output of git push",
                expect_return=True))

            # 10.Fetch the home page of the app
            if self.test_variant == "jbossas" or self.test_variant == "diy":
                self.info("%s app doesn't need to check the web page" % (self.test_variant))
            else:
                self.steps_list.append( testcase.TestCaseStep("%d.Fetch the home page of the app" % (i),
                    "curl -s -H 'Pragma: no-cache' '%s'",
                    string_parameters = [OSConf.get_app_url_X(self.app_name)],
                    expect_description="Successfully get the web page",
                    expect_return=0))
            # 11.Check env vars from the web page
                self.steps_list.append( testcase.TestCaseStep("%d.Check env vars from the web page" % (i),
                    self.compare,
                    function_parameters=[self.get_last_output, lst],
                    expect_description="The openshift env vars should found in the web page",
                    expect_return=True))
            # 12.Remove embedded database
            self.steps_list.append( testcase.TestCaseStep("%d.Remove embedded database" % (i),
                common.embed,
                function_parameters=[self.app_name, "remove-" + cart, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="%s should be embedded successfully" % (cart),
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

    def contains(self, lst1, lst2):
        '''Check if ordered list lst1 contains ordered list lst2'''
        if len(lst1) < len(lst2):
            return False
        i = 0
        for j in range(0, len(lst2)):
            if i >= len(lst1):
                return False
            while i < len(lst1) and lst2[j] != lst1[i]:
                i += 1
            i += 1
        return True

    def compare(self, output, env_lst):
        pattern = re.compile(r'OPENSHIFT[\w_]+(?=[=\s])', re.S)
        match_lst = pattern.findall(output)
        match_lst.sort()
        env_lst.sort()
        print "Environment variables found in the output/webpage:"
        print match_lst
        print "Environment variables should be found:"
        print env_lst
        return self.contains(match_lst, env_lst)

    def get_last_output(self):
        return self.output

    def store_output(self, output):
        #self.info("Saving output...\n%s"%output)
        self.output=output
        return {}

    def get_page(self):
        #self.info("get_page()")
        cmd="curl -s -H 'Pragma: no-cache' '%s'"%OSConf.get_app_url(self.app_name)
        (status, output) = common.command_getstatusoutput(cmd)
        return output
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EnvVars)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
