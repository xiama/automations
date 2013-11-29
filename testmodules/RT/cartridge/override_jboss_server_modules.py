"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1114][rhc-cartridge] Override jbossas-7 server modules with user's modules
https://tcms.engineering.redhat.com/case/122350/
"""
import os,sys,re,time

import testcase
import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1114][rhc-cartridge] Override jbossas-7 server modules with user's modules " 
        self.app_name = "overridejboss"
        self.app_type = common.app_types["jbossas"]
        self.git_repo = "./%s" % (self.app_name)

        common.env_setup()
        common.clean_up(self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)

        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class OverrideJbossServerModules(OpenShiftTest):
    def test_method(self):

        # 1. Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an jbossas app: %s" % (self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Create some directories and copy jboss modules into them
        cmd = "mkdir -p %s/.openshift/config/modules/org/joda/time/main/ && cp %s/app_template/jodatime/{JodaTime.jar,module.xml} %s/.openshift/config/modules/org/joda/time/main/ && mkdir %s/src/main/webapp/WEB-INF/lib && cp %s/app_template/jodatime/test1.jar %s/src/main/webapp/WEB-INF/lib" % (self.git_repo, WORK_DIR, self.git_repo, self.git_repo, WORK_DIR, self.git_repo)
        self.steps_list.append( testcase.TestCaseStep("2.Create some directories and copy jboss modules into them",
                cmd,
                expect_description="Copy should succeed",
                expect_return=0))

        # 3.Create time.jsp in the git repo
        time_jsp = """<HTML>
<HEAD>
        <TITLE>JBossAS7 Custom Modules Test Page</TITLE>
    <%@ page import="org.joda.time.DateTime" %>
    <%@ page import="java.util.*" %>
</HEAD>
<BODY>
<h1>Customized org.joda.time.DateTime</h1>
<pre>
<%
DateTime dt = new DateTime();
%>
<%= dt %>
</pre>
<h1>java.util.Date</h1>
<pre>
<%
Date dt1 = new Date();
%>
<%= dt1 %>
</pre>
</BODY>
</HTML>"""
        file_path = "%s/src/main/webapp/time.jsp" % (self.git_repo)
        cmd = "echo '%s' > %s" % (time_jsp, file_path)
        self.steps_list.append( testcase.TestCaseStep("3.Create time.jsp in the git repo",
                    cmd,
                    expect_description="time.jsp should be created successfully",
                    expect_return=0))

        # 4.Git push all the changes
        self.steps_list.append( testcase.TestCaseStep("4.Git push all the changes",
                "cd %s && git add . && git commit -am t && git push" % (self.git_repo),
                expect_description="time.jsp should be created successfully",
                expect_return=0))

        # 5.Check time.jsp
        def get_app_url(app_name):
            def get_app_url2():
                return OSConf.get_app_url(self.app_name) + "/time.jsp"
            return get_app_url2

        self.steps_list.append( testcase.TestCaseStep("5.Check time.jsp",
                common.grep_web_page,
                function_parameters=[get_app_url(self.app_name), "Customized org.joda.time.DateTime", "-H 'Pragma: no-cache'", 3, 6],
                expect_description="time.jsp should be able to work properly",
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
    suite.add_test(OverrideJbossServerModules)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
