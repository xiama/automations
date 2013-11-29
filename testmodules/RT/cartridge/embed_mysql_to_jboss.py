"""
Michal Zimen
mzimen@redhat.com
Apr 04, 2012
[rhc-cartridge] embed MySQL instance to JBossAS application
https://tcms.engineering.redhat.com/case/???/
"""
import os

import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge] embed MySQL instance to an JBossAS application"
        self.app_type = common.app_types["jbossas"]
        self.app_name = "jboss4mysql"
        self.mysql_v = common.cartridge_types['mysql']
        common.env_setup()

    def finalize(self):
        pass

class EmbedMysqlToJboss(OpenShiftTest):
    def test_method(self):
        self.add_step("Create a JBoss app", common.create_app, 
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description = "the app should be created successfully",
                expect_return=0)
    
        self.add_step("Embed mysql to the app", 
                common.embed,
                function_parameters=[self.app_name, 
                                     "add-" + common.cartridge_types['mysql']],
                expect_description="the mysql cartridge should be embedded successfully",
                expect_return=0)

        def config_app(app_name):
            cmd = """cd %s && sed -i '/MysqlDS"/ {s/false/true/}' .openshift/config/standalone.xml; git commit -a -m 'changes' && git push"""%self.app_name
            (status, output) = common.command_getstatusoutput(cmd)
            return 0

        self.add_step("Modify JBoss ", 
                config_app,
                function_parameters = [self.app_name],
                expect_description = "The config file should be modified successfully",
                expect_return = 0)

        def add_page(app_name):
            new_page = """<%@ page contentType="text/html" language="java" import="java.sql.*" %>
<%@ page import="javax.naming.*" %>
<%@ page import="javax.sql.*" %>
<%
InitialContext ctx = new InitialContext();
DataSource ds = (DataSource) ctx.lookup("java:jboss/datasources/MysqlDS");
Connection connection=ds.getConnection();
Statement statement = connection.createStatement();
statement.executeUpdate("DROP TABLE IF EXISTS ucctalk");
statement.executeUpdate("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))");
statement.executeUpdate("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')");
ResultSet rs = statement.executeQuery("SELECT * FROM ucctalk");
ResultSetMetaData rmeta = rs.getMetaData();
int numColumns=rmeta.getColumnCount();
while(rs.next()) {
out.print(rs.getString(1));
out.print(", ");
out.print(rs.getString(2));
out.print("<br>");
}
out.print("<br>");
rs.close();
statement.close();
connection.close();
%>"""
            new_filename = "src/main/webapp/mysql.jsp"
            f = open("%s/%s"%(self.app_name, new_filename), "w")
            f.write(new_page)
            f.close()
            cmd = "cd %s; git add %s && git commit -a -m 'changes' && git push"%(self.app_name, new_filename)
            (status, output) = common.command_getstatusoutput(cmd)
            return status

        self.add_step("Create a page which does some operation with "
                      "mysql database under ./src/main/webapp , like mysql.jsp:",
                add_page,
                function_parameters = [self.app_name],
                expect_description = "The page should be added without errros",
                expect_return = 0)

        def verify(app_name):
            url = OSConf.get_app_url(self.app_name)
            return common.grep_web_page(url+"/mysql.jsp", 
                                        'Jeremy', 
                                        "-H 'Pragma: no-cache' -L", 5, 6)
            

        self.add_step("Verify the MySQL functionality...",
                verify,
                function_parameters = [self.app_name],
                expect_description = "The page should be added without errros",
                expect_return = 0)

        self.add_step("Remove embedded mysql from the app", 
                common.embed,
                function_parameters = [self.app_name, 
                                       "remove-" + common.cartridge_types['mysql']],
                expect_description = "the mysql should be removed successfully",
                expect_return = 0)

        self.run_steps()


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EmbedMysqlToJboss)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
