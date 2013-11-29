#!/usr/bin/env python

import common, OSConf
import rhtest
import time
import os
# user defined packages
import proc

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.exp_file = "rhc-tail-files-%s.expect"%common.getRandomString(5)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        self.text_to_verify = 'Jn316'
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = 'ruby'
        tcms_testcase_id=122302
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -f %s"%self.exp_file)
        try:
            self.rhc_tail_proc.kill()
            return
            common.destroy_app(self.app_name)
            common.command_get_status("rm -rf %s"%self.app_name)
        except:
            pass


class RhcTailFilesCheck(OpenShiftTest):

    def run_rhc_tail(self, arguments=''):
        url = OSConf.get_app_url(self.app_name)
        for i in range(1):  #touch that app
            common.grep_web_page(url,'OpenShift')

        # Get the path of rhc
        (status, output) = common.command_getstatusoutput('which rhc')
        if status != 0:
            return self.failed("Unable to find rhc client")

        fw = open(self.exp_file, "wb")
        fw.write("""spawn -nottyinit %s tail %s -l %s -p %s %s %s
set timeout -1
expect wait_for_ever_and_ever
            """%(output.strip(), self.app_name, self.user_email, self.user_passwd, arguments, common.RHTEST_RHC_CLIENT_OPTIONS))
        fw.close()
        
        cmd=["/usr/bin/expect", self.exp_file] 

        try:
            self.rhc_tail_proc.wait(1)
            self.rhc_tail_proc.kill()
        except:
            pass

        try:
            #stdin as /dev/null is very impotant thing if we run SSH remotely, 
            #which is also this case
            self.rhc_tail_proc = proc.Proc(cmd, 
                                           shell=False, 
                                           stdin=open(os.devnull, 'rb'))
        except Exception as e:
            self.error(str(e))
            return False

        return True

    def do_changes(self):
        uuid= OSConf.get_app_uuid(self.app_name)
        try:
            for i in range(5):
                cmd = "echo %s>> /var/lib/openshift/%s/%s/logs/error_log-*"%(self.text_to_verify, uuid, "".join([a for a in common.app_types[self.app_type] if a.isalpha()]))
                (status1, output) = common.run_remote_cmd(self.app_name, cmd)
                cmd = "echo %s>> /var/lib/openshift/%s/%s/logs/access_log-*"%(self.text_to_verify, uuid, "".join([a for a in common.app_types[self.app_type] if a.isalpha()]))
                (status2, output) = common.run_remote_cmd(self.app_name, cmd)
        except Exception as e:
            self.error(str(e))
            return 1

        return status1+status2

    def verify(self):
        url = OSConf.get_app_url(self.app_name)
        for i in range(1):  #touch that app
            common.grep_web_page(url, 'OpenShift')

        return self.rhc_tail_proc.grep_output(self.text_to_verify, 3, 10)


    def test_method(self):

        rhtest.TestStep(self, "1. Let's have an %s app"%self.app_type,
                common.create_app,
                function_parameters=[self.app_name, 
                        common.app_types[self.app_type], 
                        self.user_email, 
                        self.user_passwd, 
                        False],
                expect_description="App should be created",
                expect_return=0)()

        rhtest.TestStep(self, "2. Run rhc-tail-files to monitor into background",
                self.run_rhc_tail,
                expect_description="Monitor rhc-tail-files should be run without errors",
                expect_return=True)()

        rhtest.TestStep(self, "3.Append some data to log files directly.",
                self.do_changes,
                expect_description="Data should be appended to the remote log files",
                expect_return=0)()

        rhtest.TestStep(self, "4. Verify output of 'rhc tail'", 
                self.verify,
                expect_description="Searched string should be found via web output",
                expect_return=0)()

        rhtest.TestStep(self, "5. Append some data to log files directly.",
                self.do_changes,
                expect_description="Data should be appended to the remote log files",
                expect_return=0)()

        rhtest.TestStep(self, "6. Check direct call",
                self.run_rhc_tail,
                function_parameters = ["--file /var/lib/openshift/%s/%s/logs/access_log-%s-000000-*"%(OSConf.get_app_uuid(self.app_name) , "".join([a for a in common.app_types[self.app_type] if a.isalpha()]), 
                                                                                  time.strftime("%Y%m%d",time.localtime()))],
                expect_description = "Direct parameter should work",
                expect_return=True)()

        if self.rhc_tail_proc.grep_output("HTTP", 3, 10)!=0:
            return self.failed("Unable to launch't rhc-tail-files --files")

        '''
        step = rhtest.TestStep(self, "Check --file *", 
                self.run_rhc_tail,
                function_parameters=[self.app_name, '--file "*"'],
                expect_return=1)
        (status, output) = step()
        if (rhc_tail.poll()==None):
            rhc_tail.send_signal(signal.SIGINT)
            rhc_tail.terminate()

        '''
        rhtest.TestStep(self, "7. Check --file .ssh/",
                self.run_rhc_tail,
                function_parameters = ["--file .ssh/"],
                expect_description="We shouldn't be allowed",
                expect_return=True)()

        if not self.rhc_tail_proc.grep_output("Could not find any files matching glob",3,10):
            return self.failed("rhc-tail-files could read .ssh/ files")

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcTailFilesCheck)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
