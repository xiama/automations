#!/usr/bin/env python
import os, sys
from common import consts
import testcase, common, OSConf
import rhtest
import database
import time
import random
import re
# user defined packages
import openshift
import fileinput

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.config.test_variant
        except:
            self.test_variant = 'jbossas'
        self.info("VARIANT: %s"%self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.git_repo = './' + self.app_name
        common.env_setup()
        self.steps_list = []
        self.domain_name = common.get_domain_name()
        
    def finalize(self):
        pass

class ScalingSupport(OpenShiftTest):
    def configure_scale_up_test_application(self):
        if self.test_variant == "php":
            #
            # PHP
            #
            new_file = open(self.git_repo + "/php/gear.php", "w")
            new_file.write("<?php\n")
            new_file.write("header(\"Content-Type: text/plain\");\n")
            new_file.write("echo $_ENV[\"OPENSHIFT_GEAR_DNS\"];\n")
            new_file.write("?>")
            new_file.close()
        elif self.test_variant == "nodejs":
            #
            # NODEJS
            # Only gear usage testing so far
            #
            try:
                for line in fileinput.input(self.git_repo + "/server.js", inplace = 1):
                    if re.search("Routes for /health", line):
                        print "        self.routes['/gear.js'] = function(req, res) {"
                        print "            res.send(process.env.OPENSHIFT_GEAR_DNS, {'Content-Type': 'text/plain'});"
                        print "        };"
                    print line,
            except Exception as e:
                fileinput.close()
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            #
            # Rack
            # Only gear usage testing so far
            #
            try:
                for line in fileinput.input(self.git_repo + "/config.ru", inplace = 1):
                    if re.search("map '/health' do", line):
                        print "map '/gear.rb' do"
                        print "  gear_dns = proc do |env|"
                        print "    [ 200, { 'Content-Type' => 'text/plain'}, ENV['OPENSHIFT_GEAR_DNS'] ]"
                        print "  end"
                        print "  run gear_dns"
                        print "end"
                        print
                    print line
            except Exception as e:
                fileinput.close()
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()
        elif self.test_variant in ("jbossas", "jbosseap"):
            #
            # JBOSS
            #
            gear_file = open(self.git_repo + "/src/main/webapp/gear.jsp", "w")
            gear_file.write("<%@ page contentType=\"text/plain\" language=\"java\" import=\"java.sql.*\" %>\n")
            gear_file.write("<%@ page import=\"javax.naming.*\" %>\n")
            gear_file.write("<%@ page import=\"java.util.*\" %>\n")
            gear_file.write("<%@ page trimDirectiveWhitespaces=\"true\" %>\n")
            gear_file.write("<%\n")
            gear_file.write("Map map = System.getenv();\n")
            gear_file.write("out.print(map.get(\"OPENSHIFT_GEAR_DNS\"));\n")
            gear_file.write("%>\n")
            gear_file.close()
        elif self.test_variant == "perl":
            #
            # Perl
            #
            gear_file = open(self.git_repo + "/perl/gear.pl", "w")
            gear_file.write("#!/usr/bin/perl\n")
            gear_file.write("print 'Content-type: text/plain\r\n\r\n';")
            gear_file.write("print $ENV{'OPENSHIFT_GEAR_DNS'};")
            gear_file.close()
        elif self.test_variant in ("python", "wsgi","python-2.7","python-3.3"):
            #
            # Python-2.6
            #
            try:
                print "H %s" % (self.git_repo + "/wsgi/application")
                for line in fileinput.input(self.git_repo + "/wsgi/application", inplace = 1):
                    if re.search("PATH_INFO.+/env", line):
                        print "    elif environ['PATH_INFO'] == '/gear.py':"
                        print "        response_body = os.environ['OPENSHIFT_GEAR_DNS']"
                    print line,
            except Exception as e:
                fileinput.close()
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()

        configuration_steps = [
            "cd %s" % ( self.git_repo ),
            "git add .",
            "git commit -a -m testing_gears_and_sessions",
            "git push"
        ]

        return common.command_get_status(" && ".join(configuration_steps))

    def number_of_gears(self):
        time.sleep(30)
        app_url = OSConf.get_app_url(self.app_name)
        gears = list()
        suffix = {
            "php" : ".php",
            "nodejs" : '.js',
            "ruby" : ".rb",
            "ruby-1.9" : ".rb",
            "rack" : ".rb",
            "jbossas" : ".jsp",
            "jbosseap" : ".jsp",
            "perl" : ".pl",
            "python" : ".py",
            "wsgi" : ".py",
            "python-3.3" : ".py",
            "python-2.7" : ".py",
        }

        # Checking the output of gear dns script more times
        for i in range(1, 11):
            gear = common.fetch_page(app_url + "/gear" + suffix[self.test_variant])
            #let's check the format
            if self.config.options.run_mode == 'OnPremise':
                re_str="example.com"
            else:
                re_str="rhcloud.com"

            if re.search(r".*%s$"%(re_str), gear):
                if gear not in gears:
                    self.info("GEAR: [%s]"%gear)
                    gears.append(gear)

        return len(gears)


    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep(
            "Creating a scalable application",
            common.create_app,
            function_parameters = [ self.app_name, self.app_type, self.user_email, self.user_passwd, True, self.git_repo, True ],
            expect_description = "The application must be created successfully",
            expect_return = 0
            ))
        self.steps_list.append(testcase.TestCaseStep(
            "Scaling up via REST API",
            common.scale_up,
            function_parameters = [ self.app_name, self.domain_name ],
            expect_description = "The application must scale-up successfully",
            expect_return = 0
            ))

        for operation in [ "stop", "restart", "reload", "force-stop", "start" ]:
            self.steps_list.append(testcase.TestCaseStep(
            "Checking operation '%s'" % operation,
            "rhc app %s %s -l %s -p '%s' %s" % ( operation, self.app_name, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = "Operation must be successfull",
            expect_return = 0
            ))

        # Checking web-page availability with refreshing
        for i in range(1,6):
            self.steps_list.append(testcase.TestCaseStep(
                "Checking web-page #%d" % ( i ),
                common.check_web_page_output,
                function_parameters = [ self.app_name ],
                expect_description = "The application must be available in the browser",
                expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Configuring the test application",
            self.configure_scale_up_test_application,
            expect_description = "The application must be configured successfully",
            expect_return = 0
            ))

        self.steps_list.append(testcase.TestCaseStep(
            "Checking the number of gears",
            self.number_of_gears,
            expect_description = "The number of gears must be '2'",
            expect_return = 2
            ))

        self.steps_list.append(testcase.TestCaseStep(
            "Scaling down via REST API",
            common.scale_down,
            function_parameters = [ self.app_name, self.domain_name],
            expect_description = "The application must scale-down successfully",
            expect_return =0 
        ))
        
        self.steps_list.append(testcase.TestCaseStep(
            "Checking web-page availability",
            common.check_web_page_output,
            function_parameters = [ self.app_name ],
            expect_description = "The application must be available in the browser",
            expect_return = 0
            ))

        case= testcase.TestCase("Scaling support", self.steps_list)
        case.run()
        
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ScalingSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
