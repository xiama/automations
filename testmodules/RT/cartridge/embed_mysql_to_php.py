"""
Michal Zimen
mzimen@redhat.com
Apr 05, 2012
[rhc-cartridge] embed MySQL instance to PHP application
https://tcms.engineering.redhat.com/case/122451/?from_plan=4962
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
        self.summary = "[rhc-cartridge] embed MySQL instance to an PHP application"
        self.app_type = common.app_types["php"]
        self.app_name = "php4mysql"
        self.mysql_v = common.cartridge_types['mysql']
        self.steps_list = []

        common.env_setup()
    
    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysqlToPhp(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a PHP app", common.create_app, 
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

        def add_page(app_name):
            new_page = """<?php
$con=mysql_connect($_ENV["OPENSHIFT_MYSQL_DB_HOST"].":".$_ENV["OPENSHIFT_MYSQL_DB_PORT"], 
                   $_ENV["OPENSHIFT_MYSQL_DB_USERNAME"], 
                   $_ENV["OPENSHIFT_MYSQL_DB_PASSWORD"]) or die(mysql_error());

mysql_select_db($_ENV["OPENSHIFT_APP_NAME"], $con);
mysql_query("DROP TABLE IF EXISTS ucctalk", $con);
mysql_query("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))",$con);
mysql_query("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')",$con);
$result=mysql_query("SELECT * FROM ucctalk",$con);
while($row=mysql_fetch_array($result))
{
    echo $row['speaker'],", ",$row['title'],"<br>";
}
mysql_close($con);
?>"""
            new_filename = "mysql.php"
            f = open("%s/php/%s"%(self.app_name, new_filename), "w")
            f.write(new_page)
            f.close()
            cmd = "cd %s; git add php/%s && git commit -a -m 'changes' && git push"%(self.app_name, new_filename)
            (status, output) = common.command_getstatusoutput(cmd)
            return status

        self.steps_list.append(testcase.TestCaseStep(
                "Create a page which does some operation with mysql database like mysql.php:",
                add_page,
                function_parameters=[self.app_name],
                expect_description="The page should be added without errros",
                expect_return=0))

        def verify(app_name):
            url = OSConf.get_app_url(self.app_name)
            return common.grep_web_page(url+"/mysql.php", 'Jeremy')

        self.steps_list.append(testcase.TestCaseStep("Verify the MySQL functionality...",
                verify,
                function_parameters=[self.app_name],
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
    suite.add_test(EmbedMysqlToPhp)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
