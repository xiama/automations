#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import testcase, common, OSConf
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
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'ruby'

    	common.env_setup()
   	self.steps_list = []

    def finalize(self):
        pass


class RHCTailFilesCheck(OpenShiftTest):
    def run_rhc_tail(self, app_name, arguments=None):
        "Should return non zero if the command"
        global rhc_tail
        url = OSConf.get_app_url(app_name)
        for i in range(1):  #touch that app
            common.grep_web_page(url,'OpenShift')
        cmd="rhc-tail-files -a %s -l %s -p %s "%(app_name, self.user_email, self.user_passwd)
        if arguments!=None:
            cmd += arguments
        print "CMD=%s"%cmd
        rhc_tail = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        # make stdin a non-blocking file
        try:
            fd = rhc_tail.stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        except Exception as e:
            print "ERROR: %s"%str(e)
            return 1

        time.sleep(10)
        st = rhc_tail.poll()
        if (st==None):
            st=777
        return st

    def do_changes(self, app_name):
        uuid= OSConf.get_app_uuid(app_name)
        try:
            cmd = "echo Jn316 >> /var/lib/openshift/%s/%s/logs/error_log-*"%(uuid, app_name)
            (status, output) = common.run_remote_cmd(None, cmd, True)
            cmd = "echo Jn316 >> /var/lib/openshift/%s/%s/logs/access_log-*"%(uuid, app_name)
            (status, output) = common.run_remote_cmd(None, cmd, True)
        except:
            return 1

        return 0

    def verify():
        global rhc_tail
        text = None
        try:
            time.sleep(10)
            text = rhc_tail.stdout.read()
        except Exception as e:
            print "ERROR: %s"%str(e)
            return 1
        print "DEBUG",text
        obj = re.search(r"Jn316", text, re.MULTILINE)
        if obj:
            return 0

        return 1


    def test_method(self):
        rhc_tail = None
        ret_code = 0
        try:
            step=testcase.TestCaseStep("Let's have an app",
                                      common.create_app,
                                      function_parameters=[self.app_name, common.app_types[self.app_type], self.user_email, self.user_passwd, False],
                                      expect_return=0)

            (status, output) = step.run()


            step = testcase.TestCaseStep("Run rhc-tail-files",
                                     run_rhc_tail,
                                     function_parameters=[self.app_name],
                                     expect_return=777)

            (status, output) = step.run()

            step=testcase.TestCaseStep("Append some data to log files directly.",
                                   do_changes,
                                   function_parameters=[self.app_name],
                                   expect_return=0)

            (status, output) = step.run()


            step=testcase.TestCaseStep("VERIFY rhc-tail-files", verify, expect_return=0)

            (status, output) = step.run()
            "We can now kill the process"
            rhc_tail.send_signal(signal.SIGINT)
            rhc_tail.kill()

            step = testcase.TestCaseStep("Check direct call",
                    run_rhc_tail,
                    function_parameters=[self.app_name,
                                         "--file %s/logs/access_log-%s-000000-EST"%(self.app_name,time.strftime("%Y%m%d",time.localtime()))],
                    expect_return=777)
            (status, output) = step.run()
            time.sleep(10)
            text = rhc_tail.stdout.read()
            obj = re.search(r"HTTP",text)
            if obj==None:
                raise testcase.TestCaseStepFail("Unable to launch't rhc-tail-files --files")
            rhc_tail.send_signal(signal.SIGINT)
            rhc_tail.terminate()

            '''
            step = testcase.TestCaseStep("Check --file *", 
                    run_rhc_tail,
                    function_parameters=[self.app_name, '--file "*"'],
                    expect_return=1)
            (status, output) = step.run()
            text = rhc_tail.stdout.read()
            print "\nDEBUG",text
            print "\nEND__DEBUG\n"
            if (rhc_tail.poll()==None):
                rhc_tail.send_signal(signal.SIGINT)
                rhc_tail.terminate()

            '''
            step = testcase.TestCaseStep("Check --file .ssh/",
                    run_rhc_tail,
                    function_parameters=[self.app_name, "--file .ssh/"],
                    expect_description="We shouldn't be allowed",
                    expect_return=None)
            (status, output) = step.run()
            text = rhc_tail.stdout.read()
            print "\nDEBUG",text
            print "END__DEBUG\n"
            obj = re.search(r"Could not find any files matching glob",text)
            if obj==None:
                raise testcase.TestCaseStepFail("rhc-tail-files could read .ssh/ files")

            if (rhc_tail.poll()==None):
                rhc_tail.send_signal(signal.SIGINT)
                rhc_tail.terminate()

        except testcase.TestCaseStepFail as f:
            print "ERROR: %s"%str(f)
            ret_code=1
        except Exception as e:
            print "ERROR: %s"%str(e)
            ret_code=254

        finally:
            common.command_get_status("rm -rf %s"%self.app_name)
            if (rhc_tail != None):
                try:
                    rhc_tail.send_ctrl_c()
                    rhc_tail.send_signal(signal.SIGINT)
                    rhc_tail.kill()
                    rhc_tail.terminate()
                except:
                    pass

       # sys.exit(ret_code)
	
	if step.testcase_status == 'PASSED':
	    return self.passed("%s passed" % self.__class__.__name__)
	if step.testcase_status == 'FAILED':
	    return self.failed("%s failed" % self.__class__.__name__)
	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RHCTailFilesCheck)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
