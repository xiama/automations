"""
Michal Zimen
mzimen@redhat.com
Apr 05, 2012
[rhc-cartridge] embed MySQL instance to PERL application
https://tcms.engineering.redhat.com/case/122450/?from_plan=4962
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
        self.app_type = common.app_types["perl"]
        self.app_name = "perl"+common.getRandomString(7)
        self.summary = "[rhc-cartridge] embed MySQL instance to PERL application"
        self.mysql_v = common.cartridge_types['mysql']
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class EmbedMysqlToPerl(OpenShiftTest):
    def verify(self):
        url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page(url+"/mysql.pl", 'Jeremy')

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a PERL app", common.create_app, 
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))
    
        self.steps_list.append(testcase.TestCaseStep("Embed mysql to the app", 
                common.embed,
                function_parameters=[self.app_name, "add-" + common.cartridge_types['mysql']],
                expect_description="the mysql cartridge should be embedded successfully",
                expect_return=0))

        def add_page(app_name):
            new_page = """#!/usr/bin/perl
print "Content-type: text/plain\\r\\n\\r\\n";
print " \n";
use DBI;
my $dbname = $ENV{"OPENSHIFT_APP_NAME"};
my $location = $ENV{"OPENSHIFT_MYSQL_DB_HOST"};
my $port = $ENV{'OPENSHIFT_MYSQL_DB_PORT'};
my $database = "DBI:mysql:$dbname:$location:$port";
my $db_user = $ENV{"OPENSHIFT_MYSQL_DB_USERNAME"};
my $db_pass = $ENV{"OPENSHIFT_MYSQL_DB_PASSWORD"};
my $dbh = DBI->connect($database, $db_user, $db_pass) or die "Cannot connect database";
my $sth = $dbh->prepare("DROP TABLE IF EXISTS ucctalk") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("CREATE TABLE ucctalk (speaker CHAR(30), title CHAR(60))") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("INSERT INTO ucctalk (speaker,title) VALUES ('Jeremy Zawodny', 'Optimizing MySQL'), ('Sanja Byelkin', 'Sub-Queries in MySQL'), ('Tim Bunce', 'Advanced Perl DBI')") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
my $sth = $dbh->prepare("SELECT * FROM ucctalk") or die $dbh->errstr;
$sth->execute() or die "Cannot execute SQL command:$dbh->errstr";
while (@ary = $sth->fetchrow_array())
{
    print join(", ",@ary),"\n";
}
$sth->finish();
$dbh->disconnect;"""
            new_filename = "mysql.pl"
            f = open("%s/perl/%s"%(self.app_name, new_filename), "w")
            f.write(new_page)
            f.close()
            cmd = "cd %s; git add perl/%s && git commit -a -m 'changes' && git push"%(self.app_name, new_filename)
            (status, output) = common.command_getstatusoutput(cmd)
            return status

        self.steps_list.append(testcase.TestCaseStep("Create a page which does some operation with mysql database like mysql.pl:",
                    add_page,
                    function_parameters=[self.app_name],
                    expect_description="The page should be added without errros",
                    expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Verify the MySQL functionality...",
                    self.verify,
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
    suite.add_test(EmbedMysqlToPerl)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
