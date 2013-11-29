#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf, proc
import rhtest
import database
import time
import random
# user defined packages
import openshift


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
	self.user_email = os.environ["OPENSHIFT_user_email"]
    	self.user_passwd = os.environ["OPENSHIFT_user_passwd"]
        self.app_type = common.app_types["jbossas"]
        self.app_name = "jbossastail"
        tcms_testcase_id=122408
    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass
def create_proc(cmd):
    return proc.Proc(cmd)


class RhcTailFilesOptionsJbossas(OpenShiftTest):
    def test_method(self):
        case = testcase.TestCase("[US504][rhc-cartridge]JBoss cartridge: tail/snapshot jboss application files", [])
        step = dict()
        output = dict()
        # 1.Create an php app
        step[1] = testcase.TestCaseStep("1. Create an jbossas app",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.user_email, self.user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0
        )
        (retcode, output[1]) = step[1].run()

        count = 1 # recording the number of step

        option_lst = [  "-o '-n 2'",
                    "-o '-c 3'",
                    "-o '-q'",
                    "-f %s/logs/boot.log -o '-v'" % (self.app_name),
                    "-o '--test'",
                    "-o '-F'",
                ]
        regex_lst = [   r"boot.log.*\n.*\n.*\n(?=\n|$)",
                    r"boot.log.*\n.{2}\n(?=\n|$)",
                    r"==> %s/logs/.*?.log" % (self.app_name),
                    r"==> %s/logs/.*?.log" % (self.app_name),
                    r"/usr/bin/tail: unrecognized option '--test'",
                    r"%s/logs/boot.log" % (self.app_name),
                ]
        for i in range(len(option_lst)):
            option = option_lst[i]
            regex = regex_lst[i]
            # 2.Run rhc tail in subprocess
            count += 1
            step[count] = testcase.TestCaseStep("%d.Run rhc tail in subprocess with option: '%s'" % (count, option),
                    create_proc,
                    function_parameters=["rhc tail %s -l %s -p '%s' %s %s" % (self.app_name, self.user_email, self.user_passwd, option, common.RHTEST_RHC_CLIENT_OPTIONS),],
                    expect_description="rhc tail should be started",
            )
            (retcode, output[count]) = step[count].run()
            p = retcode
            try:
                # 3.Check the option takes effect
                if i in (2,):
                    exp_ret = 1
                else:
                    exp_ret = 0
                count += 1
                step[count] = testcase.TestCaseStep("%d.Check if option: '%s' takes effect" % (count, option),
                        p.grep_output,
                        function_parameters=[regex, 3, 5, 0],
                        expect_description="Function should return %d" % (exp_ret),
                        expect_return=exp_ret
                )
                (retcode, output[count]) = step[count].run()
            finally:
                # 4.Kill the rhc tail subprocess
                count += 1
                step[count] = testcase.TestCaseStep("%d.Kill subprocess: rhc tail %s" % (count, option),
                        p.kill,
                        function_parameters=[],
                        expect_description="subprocess should be killed",
                        expect_return=0
                )
                (retcode, output[count]) = step[count].run()

	
	        if retcode==0:
	            return self.passed("%s passed" % self.__class__.__name__)
	        else:
	            return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcTailFilesOptionsJbossas)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
