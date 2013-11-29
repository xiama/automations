"""
Michal Zimen
mzimen@redhat.com
Apr 05, 2012
[rhc-cartridge] embed MySQL instance to RACK application
https://tcms.engineering.redhat.com/case/122452/?from_plan=4962
"""
import os
import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge] embed MySQL instance to an RACK application"
        try:
            variant = self.get_variant()
        except:
            variant = 'ruby'
        self.app_type = common.app_types[variant]
        self.app_name = "ruby4mysql"+common.getRandomString(4)
        self.mysql_v = common.cartridge_types['mysql']
        self.steps_list = []
        self.info("VARIANT: %s"%variant)

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysqlToRack(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a RACK app", common.create_app, 
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="The app should be created successfully",
                expect_return=0))
        
        self.steps_list.append(testcase.TestCaseStep("Embed mysql to the app", 
                common.embed,
                function_parameters = [ self.app_name, "add-%s" %self.mysql_v],
                expect_description="The mysql cartridge should be embedded successfully",
                expect_return=0))

        def mod_config_ru(self):
            cmd = """cd %s && cat <<'EOF' >>config.ru &&
require 'mysql'
map '/mysql' do
  content = ""
  begin
    dbh = Mysql.real_connect(ENV['OPENSHIFT_MYSQL_DB_HOST'], ENV['OPENSHIFT_MYSQL_DB_USERNAME'], ENV['OPENSHIFT_MYSQL_DB_PASSWORD'], ENV['OPENSHIFT_APP_NAME'], Integer(ENV['OPENSHIFT_MYSQL_DB_PORT']))
    dbh.query("DROP TABLE IF EXISTS ucctalk")
    dbh.query("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))")
    dbh.query("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')")
    content += "<p>#{dbh.affected_rows} rows were inserted:</p>"
    res = dbh.query("SELECT * FROM ucctalk")
    while row = res.fetch_row do
      content += row.join(", ")+"<br>"
    end
    res.free
  rescue MysqlError => e
    content += "Error code: #{e.errno}"
    content += "Error message: #{e.error}"
  ensure
    dbh.close if dbh
  end
  mysql = proc do |env|
    [200, { "Content-Type" => "text/html" }, [content]]
  end
  run mysql
end
EOF
git commit -m "changes" -a && git push"""%self.app_name
            (status, output) = common.command_getstatusoutput(cmd)
            return status

        self.steps_list.append(testcase.TestCaseStep("Modify config.ru for accepting /mysql",
                mod_config_ru,
                function_parameters=[self],
                expect_description="The modifications should be done without errros",
                expect_return=0))

        def verify(self):
            url = OSConf.get_app_url(self.app_name)
            return common.grep_web_page(url+"/mysql", 'Jeremy')

        self.steps_list.append(testcase.TestCaseStep("Verify the MySQL functionality...",
                verify,
                function_parameters=[self],
                expect_description="The page should be added without errros",
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Remove embedded mysql from the app", 
                common.embed,
                function_parameters = [ self.app_name, "remove-%s" %self.mysql_v],
                expect_description="The mysql should be removed successfully",
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
    suite.add_test(EmbedMysqlToRack)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
