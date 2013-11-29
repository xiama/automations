#
#  File name: jboss_env_vars.py
#  Date:      2012/03/02 01:00
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import testcase
import common
import OSConf
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1174] [rhc-cartridge] Import environment variables as system properties for jbossas-7.0 application"
        self.app_name = 'jbossenv'
        self.app_type = 'jbossas'
        tcms_testcase_id = 	122366
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class JbossEnvVars(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a JBoss app",
                common.create_app,
                function_parameters=[self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Embed with MySQL",
                common.embed,
                function_parameters=[self.app_name, 'add-%s'%common.cartridge_types['mysql'], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        #3
        self.steps_list.append(testcase.TestCaseStep("Embed with MySQL",
                '''
                cd %s &&
                cat <<'EOF' >src/main/webapp/test.jsp &&
<%%@ page contentType="text/html" language="java" import="java.sql.*" %%>
<%%@ page import="javax.naming.*" %%>
<%%@ page import="javax.sql.*" %%>


<%%
out.println("Welcome~");

String action=request.getParameter("action");
out.println("-"+request.getParameter("action")+"-");

if (action == null) {
  action="";
}

String context = "";
if (action.equals("create")) {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
  Statement statement = connection.createStatement();
  statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
  statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
  statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('speaker1', 'title1')");
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\\\\n";
  }
  rs.close();
  statement.close();
  connection.close();

  out.print(context);
} else if (action.equals("modify")) {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
  Statement statement = connection.createStatement();
  statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
  statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
  statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('speaker2', 'title2')");
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\\\\n";
  }
  rs.close();
  statement.close();
  connection.close();

  out.print(context);
} else {
  InitialContext ctx = new InitialContext();
  DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
  Connection connection=ds.getConnection();
  Statement statement = connection.createStatement();
  ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
  ResultSetMetaData rmeta = rs.getMetaData();
  int numColumns=rmeta.getColumnCount();
  while(rs.next()) {
    context = context + rs.getString(1) + ", " + rs.getString(2) + "\\\\n";
  }
  rs.close();
  statement.close();
  connection.close();

  out.print(context);
}


%%>
EOF
        git add src/main/webapp/test.jsp && 
        git commit -m "Added test.jsp" -a &&
        git push
'''%(self.app_name),
                expect_return=0))

        def verify(self):
            url = OSConf.get_app_url(self.app_name)
            r = common.grep_web_page("http://%s/test.jsp?action=create"%url, ['Welcome~','-create-','speaker1, title1'])
            return r

        #4
        self.steps_list.append(testcase.TestCaseStep("Verify the test.jsp",
                verify,
                function_parameters = [self],
                expect_return=0))


        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
            case.add_clean_up("rm -rf %s"%(self.app_name))
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
    suite.add_test(JbossEnvVars)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of jboss_env_vars.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
