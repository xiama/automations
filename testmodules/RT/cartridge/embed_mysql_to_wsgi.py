"""
Michal Zimen
mzimen@redhat.com
Apr 05, 2012
[rhc-cartridge] embed MySQL instance to WSGI/PYTHON application
https://tcms.engineering.redhat.com/case/122453/?from_plan=4962
"""
import os
import sys

import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[rhc-cartridge] embed MySQL instance to an WSGI application"
        self.app_type = common.app_types["python"]
        self.app_name = "python4mysql"
        self.mysql_v = common.cartridge_types['mysql']
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysqlToWsgi(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a WSGI app", common.create_app, 
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
        
        self.steps_list.append(testcase.TestCaseStep("Embed mysql to the app", 
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types['mysql']],
                expect_description="the mysql cartridge should be embedded successfully",
                expect_return=0))

        def mod_config_ru(app_name):
            cmd = """cd %s && cat <<'EOF' >>wsgi/application &&

import MySQLdb

def mysql():
    content=""
    try:
        con=MySQLdb.connect(host=os.getenv("OPENSHIFT_MYSQL_DB_HOST"), user=os.getenv("OPENSHIFT_MYSQL_DB_USERNAME"), passwd=os.getenv("OPENSHIFT_MYSQL_DB_PASSWORD"), db=os.getenv("OPENSHIFT_APP_NAME"), port=int(os.getenv("OPENSHIFT_MYSQL_DB_PORT")))
        cursor = con.cursor()
        cursor.execute("DROP TABLE IF EXISTS ucctalk")
        cursor.execute("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))")
        cursor.execute("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')")
        cursor.execute("SELECT * FROM ucctalk")
        alldata = cursor.fetchall()
        if alldata:
            for rec in alldata:
                content+=rec[0]+", "+rec[1]+"\\n"
        cursor.close()
        con.commit ()
        con.close()
    except Exception, e:
        content = str(e)
    return content

EOF
sed -i '/response_body = "1"/a\\
\telif environ["PATH_INFO"] == "/mysql":\\
\t\tresponse_body = mysql()' wsgi/application &&
git commit -m "changes" -a && git push"""%self.app_name
            (status, output) = common.command_getstatusoutput(cmd)
            return status

        self.steps_list.append(testcase.TestCaseStep("Modify config.ru for accepting /mysql",
                mod_config_ru,
                function_parameters=[self.app_name],
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
                    function_parameters=[self.app_name, "remove-" + common.cartridge_types['mysql']],
                    expect_description="the mysql should be removed successfully",
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
    suite.add_test(EmbedMysqlToWsgi)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
