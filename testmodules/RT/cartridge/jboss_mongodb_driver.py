#!/usr/bin/python

#
#  File name: jboss_mongodb_driver.py
#  Date:      2012/02/28 06:00
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import testcase, common, OSConf
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary ="[US1613][Runtime]Add Mongo DB driver module"
        self.app_name = 'jboss1'
        self.app_type = 'jbossas'
        tcms_testcase_id = 135841
        self.steps = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))


class JbossMongodbDriver(OpenShiftTest):

    def test_method(self):
        self.steps.append(testcase.TestCaseStep("Create a JBoss app",
                common.create_app,
                function_parameters=[self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Embed mongoDB",
                common.embed,
                function_parameters = [self.app_name, 'add-%s'%common.cartridge_types['mongodb'],self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0,
                expect_description=0))

        def git_pull_n_update(app_name):
            mongo = OSConf.get_apps()[app_name]['embed'][common.cartridge_types['mongodb']]
            cmd='''
                cd %s &&
                git remote add upstream -m master git://github.com/openshift/jbossas-mongoDB-quickstart.git &&
                git pull -s recursive -X theirs upstream master &&
                git rm -r .openshift/config/modules &&
                export WEBXML='src/main/webapp/WEB-INF/web.xml' &&
                sed -i '/<param-name>host/,/init-param/ s/<param-value>.*/<param-value>%s<\/param-value>/' $WEBXML &&
                sed -i '/<param-name>port/,/init-param/ s/<param-value>.*/<param-value>%s<\/param-value>/' $WEBXML &&
                sed -i '/<param-name>db/,/init-param/ s/<param-value>.*/<param-value>%s<\/param-value>/' $WEBXML &&
                sed -i '/<param-name>user/,/init-param/ s/<param-value>.*/<param-value>%s<\/param-value>/' src/main/webapp/WEB-INF/web.xml &&
                sed -i '/<param-name>password/,/init-param/ s/<param-value>.*/<param-value>%s<\/param-value>/' src/main/webapp/WEB-INF/web.xml &&
                git commit -a -m "Removed modules and updated web.xml for mongoDB" &&
                git push
                '''%(self.app_name, mongo['url'], mongo['port'], mongo['database'], mongo['username'], mongo['password'])

            (status, output) = common.command_getstatusoutput(cmd)

            return status

        self.steps.append(testcase.TestCaseStep("Pull the remote source...",
                git_pull_n_update,
                function_parameters = [self.app_name],
                expect_return=0))

        def verify(app_name):
            app_url = OSConf.get_app_url(app_name)
            r = common.grep_web_page('%s/mongoDB'%app_url, 'Tutorial Objects Added to DB')
            r += common.grep_web_page('%s/mongoDB'%app_url, 'testCollection')
            return r

        self.steps.append(testcase.TestCaseStep("Check the web application",
                    verify,
                    function_parameters = [self.app_name],
                    expect_return=0))



        case = testcase.TestCase(self.summary, self.steps)
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
    suite.add_test(JbossMongodbDriver)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of jboss_mongodb_driver.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
