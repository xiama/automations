#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US478][rhc-cartridge]Perl cartridge: Perl Dancer application
https://tcms.engineering.redhat.com/case/122403/
"""
import os,sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase,common,OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US478][rhc-cartridge]Perl cartridge: Perl Dancer application"
        self.app_name = "dancer"
        self.app_type = common.app_types["perl"]
        self.git_repo = os.path.abspath(os.curdir)+os.sep+self.app_name
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class PerlDancerApplication(OpenShiftTest):
    def test_method(self):

        # 1.Create an app
        self.steps_list.append( testcase.TestCaseStep("1. Create an perl app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Setup perl config(No check)
        cmd = "mkdir -p /usr/share/perl5/CPAN/ ; rm -f /usr/share/perl5/CPAN/Config.pm ; cp %s/app_template/Config.pm /usr/share/perl5/CPAN/Config.pm ; rm -rf /$HOME/.cpan" % (WORK_DIR)
        self.steps_list.append( testcase.TestCaseStep("2.Setup perl config(No check)",
                cmd,
                expect_description="Successfully setup perl config"))

        # 3.Install dancer and dependencies from CPAN
        cmd = "cd %s/app_template && tar xzf local-lib-1.008004.tar.gz && cd local-lib-1.008004 && perl Makefile.PL --bootstrap=~/dancerlocalperl && make install && echo 'eval $(perl -I$HOME/dancerlocalperl/lib/perl5 -Mlocal::lib=$HOME/dancerlocalperl)' >>~/localperlshell && source ~/localperlshell && export PERL_MM_USE_DEFAULT=1 && cpan YAML Dancer Plack::Handler::Apache2 && cd %s && dancer -a myapp && git rm -r perl && ln -s myapp/public perl && cd libs && ln -s ../myapp/lib/myapp.pm . && cd .. && echo 'YAML\nDancer\nPlack::Handler::Apache2' >> deplist.txt" % (WORK_DIR, self.git_repo)
        self.steps_list.append( testcase.TestCaseStep("3.Install dancer and dependencies from CPAN",
                cmd,
                expect_description="dancer should be installed successfully",
                expect_return=0))

        # 4.Create the index.pl
        cmd = "cd %s/perl && cp dispatch.cgi index.pl && sed -i -e 's/.*use FindBin.*//g' index.pl && sed -i -e \"12s/RealBin.*/ENV{'DOCUMENT_ROOT'}, '..', 'myapp', 'bin', 'app.pl');/g\" index.pl" % (self.git_repo)
        self.steps_list.append( testcase.TestCaseStep("4.Create the index.pl",
                cmd,
                expect_description="index.pl should be created",
                expect_return=0))

        # 5. Git push all the changes
        self.steps_list.append( testcase.TestCaseStep("5.Git push all the changes",
                "cd %s && git add -A && git commit -a -m 'lets dance' && git push" % (self.git_repo),
                expect_description="index.pl should be created",
                expect_return=0))

        # 6.Check app via browser
        test_html = "Perl is dancing"
        self.steps_list.append( testcase.TestCaseStep("6.Check app via browser",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), test_html, "-H 'Pragma: no-cache'", 5, 9],
                expect_description="'%s' should be found in the web page" % (test_html),
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
    suite.add_test(PerlDancerApplication)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
