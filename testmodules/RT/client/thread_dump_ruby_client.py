#!/usr/bin/env python
import re

import common
import proc
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        supported_variants = ["jbossas", "ruby", "ruby-1.9"]
        self.info("[US1413][UI]Generate thread dump for jboss app from ruby client")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.variant = self.get_variant()
        except:
            self.variant = 'jbossas'

        if self.variant not in supported_variants:
            raise rhtest.TestSuiteAbort("Unsupported test variant: %s"%self.variant)

        self.app_type = common.app_types[self.variant]
        self.info("VARIANT: %s"%self.variant)
        self.app_name = common.getRandomString(10)
        common.env_setup()

    def finalize(self):
        self.info("Killing subprocess: rhc tail")
        #self.p.print_output()
        self.p.kill()


class ThreadDumpRubyClient(OpenShiftTest):
    def create_proc(self, cmd):
        self.p = proc.Proc(cmd)
        return 0

    def test_method(self):
        # 1.Create an app
        (retcode, output) = rhtest.TestStep(self,
                "1. Create a %s app"%self.variant,
                common.create_app,
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.user_email, 
                                     self.user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0)()

        # 2.Create thread dump log file
        (retcode, output) = rhtest.TestStep(self,
                "2.Create thread dump log file",
                "rhc threaddump %s -l %s -p '%s' %s" % (self.app_name, 
                                                        self.user_email, 
                                                        self.user_passwd,
                                                        common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="the app should be created successfully",
                expect_return=0,
                expect_str = ["RESULT:\nSuccess"])()

        # 3.Use rhc tail to tail thread dump log file in a subprocess
        try:
            obj = re.search(r"The thread dump file.* -f ([^\s]+)", output)
            logfile = obj.group(1)
        except:
            return self.abort("Unable to find logfile from recent stdout")
        cmd = "stdbuf -o0 rhc tail %s -l %s -p '%s' -f %s -o '-n +1' %s" %(self.app_name, 
                                                                    self.user_email, 
                                                                    self.user_passwd, 
                                                                    logfile,
                                                                    common.RHTEST_RHC_CLIENT_OPTIONS)
        (retcode, output) = rhtest.TestStep(self,
                "3.Run 'rhc tail' in a subprocess",
                self.create_proc,
                function_parameters=[cmd],
                expect_return = 0,
                expect_description="'rhc tail' should be started")()

        # 4.Check the output
        if self.variant == 'jbossas':
            regex = ["DeploymentScanner-threads",
                     "Periodic Recovery",
                     "Transaction Reaper"]
        elif self.variant in ("ruby", "ruby-1.9"):
            regex = ["Current thread", 
                     "backtrace dump"]

        for r in regex:
            (retcode, output) = rhtest.TestStep(self,
                    "4.Check the output",
                    self.p.grep_output,
                    function_parameters=[r, 3, 5, 0, False],
                    expect_description="'%s' should be found in the output" % (r),
                    expect_return=0)()

        # 5.Check the output
        if self.variant == 'jbossas':
            regex = "DestroyJavaVM"

            (retcode, output) = rhtest.TestStep(self,
                    "5.Check the output",
                    self.p.grep_output,
                    function_parameters=[regex, 3, 5, 0, False],
                    expect_description="'%s' should be found in the output" % (regex),
                    expect_return=0)()

        # 8.Restart the app
        (retcode, output) = rhtest.TestStep(self,
                "6.Restart the app",
                "rhc app restart %s -l %s -p '%s' %s" % (self.app_name,
                                                            self.user_email, 
                                                            self.user_passwd,
                                                            common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_description="App should be restarted",
                expect_return=0)()

        # 9.Check the output
        if self.variant == 'jbossas':
            common.sleep(30)
            #regex = "CORBA Naming Service started"
            regex = ["ORB Run Thread"]
        elif self.variant in ("ruby", "ruby-1.9"):
            regex = ["spawn_rack_application",
                     "spawn_application"]
        for r in regex:
            (retcode, output)= rhtest.TestStep(self,
                    "7.Check the output",
                    self.p.grep_output,
                    function_parameters=[r, 3, 5, 0],
                    expect_description="'%s' should be found in the output" % (r),
                    expect_return=0)()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ThreadDumpRubyClient)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
