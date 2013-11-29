"""
Linqing Lu
lilu@redhat.com
Dec 30, 2011

[US548][Runtime][rhc-node] Log into user application via rhcsh for debugging
https://tcms.engineering.redhat.com/case/126301/?from_plan=4962
"""
import sys
import os

import rhtest
import common
import OSConf
import pexpect
import time


class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.app_name = 'php'
        self.app_type = common.app_types[self.app_name]
        self.summary ="[US548][Runtime][rhc-node] Log into user application via rhcsh for debugging"
        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class LoginViaRHCSH(OpenShiftTest):
    def test_method(self):
        self.add_step(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type, 
                                   self.config.OPENSHIFT_user_email,
                                   self.config.OPENSHIFT_user_passwd, 
                                   False],
            expect_description = "App should be created successfully",
            expect_return = 0)

        self.add_step("get ssh url",
            OSConf.get_ssh_url,
            function_parameters = [self.app_name])

        self.add_step("run rhcsh test with pexpect",
            self.rhcsh_test_1,
            expect_return = 0)

        self.add_step("embed mysql into app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "add-mysql-5.1"],
            expect_return = 0)

        if self.get_run_mode() != 'OnPremise':
            self.add_step("embed phpmyadmin into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-phpmyadmin-3.4"],
                 expect_return = 0)

            self.add_step("remove mysql from app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "remove-mysql-5.1"],
                expect_return = 0)
    
            self.add_step("remove phpmyadmin from app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "remove-phpmyadmin-3.4"],
                expect_return = 0)
    
            self.add_step("embed mongodb into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-mongodb-2.2"],
                expect_return = 0)
    
            self.add_step("embed rockmongo into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-rockmongo-1.1"],
                expect_return = 0)
    
            self.add_step("embed metrics into app %s"% self.app_name,
                common.embed,
                function_parameters = [self.app_name, "add-metrics-0.1"],
                expect_return = 0)

        self.add_step("run rhcsh test with pexpect",
            self.rhcsh_test_2,
            expect_return = 0)

        self.add_step("get ssh url",
            OSConf.get_ssh_url,
            function_parameters = [self.app_name])

        self.add_step("run ssh with valid command",
            "ssh __OUTPUT__[2] ls",
            expect_str = ['git', self.app_name],
            expect_return = 0)

        self.add_step("run ssh with valid command",
            "ssh -t __OUTPUT__[2] rhcsh ls -al &> ls.log")

        self.add_step("check redirected output",
            "cat ls.log",
            expect_str = ['git', self.app_name, '.gitconfig'],
            #unexpect_str = ['WARNING: This ssh terminal was started without a tty.'],
            expect_return = 0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)

    def rhcsh_test_1(self):
        app_url = OSConf.get_app_url(self.app_name)
        ssh_url = OSConf.get_ssh_url(self.app_name)
        p = pexpect.spawn('ssh %s'% ssh_url, timeout=400)
        p.logfile = sys.stdout
        #index = p.expect([OSConf.get_app_url(self.app_name), pexpect.EOF, pexpect.TIMEOUT])

        p.expect('Welcome to OpenShift shell')
        p.expect(app_url)
        p.sendline('ls -l ~/app-root/data/.bash_profile')
        p.expect('-rwx.*.bash_profile')
        #p.sendline('ls -l ~/app-root/data/.bash_history')
        #p.expect('-rwx.*.bash_history')
        p.sendline('ls')
        p.expect('git')
        p.sendline('cd %s/data/ && touch test && echo "test_text" > test ; echo $?'% self.app_type)
        p.expect('0')
        p.sendline('cat test')
        p.expect('test_text')
        p.sendline('rm -f test ; ls test || echo "ok"')
        p.expect('ok')
        p.sendline('ps -efww')
        p.expect('/usr/bin/rhcsh -i')
        p.sendline('export test="rhcsh-test"; echo $test')
        p.expect('rhcsh-test')
        p.sendline('help')
        p.expect('Help menu:')
        #p.sendline('tail_all')   ### XXX do we need tail_all test?
        #p.expect('==> /var/lib/(.*)-000000-(.*) <==')
        #p.expect('==> /var/lib/(.*)-000000-(.*) <==')
        # p.sendcontrol('c')
        #p.sendcontrol('d')
        #p.sendline('exit')
        p.expect('timed out waiting for input: auto-logout', timeout=360)
        p.expect('Connection to %s closed.'% app_url)
        return 0

    def rhcsh_test_2(self):
        app_url = OSConf.get_app_url(self.app_name)
        ssh_url = OSConf.get_ssh_url(self.app_name)
        app_uuid = OSConf.get_app_uuid(self.app_name)
        p = pexpect.spawn('ssh -t %s rhcsh'% ssh_url)
        p.logfile = sys.stdout

        p.expect('Welcome to OpenShift shell')
        p.expect(app_url)
        p.sendline('ps -efww | grep "/usr/sbin/httpd" | grep -v "grep" | wc -l')
        #p.sendline('pgrep -u %s httpd | wc -l' %(app_uuid))
        if self.get_run_mode() == 'OnPremise':
            p.expect("2")
        else:
            p.expect("6")
        p.sendline('ctl_app stop')
        time.sleep(2)
        p.expect(app_url)
        #p.expect("Waiting for stop to finish")
        p.sendline('ps -efww | grep "/usr/sbin/httpd" | grep -v "grep" | wc -l')
        #p.sendline('pgrep -u %s httpd | wc -l' %(app_uuid))
        if self.get_run_mode() == 'OnPremise':
            p.expect("0")
        else:
            p.expect(["4"])
        p.sendline('ctl_app start')
        time.sleep(2)
        p.expect(app_url)
        p.sendline('ps -efww | grep "/usr/sbin/httpd" | grep -v "grep" | wc -l')
        #p.sendline('pgrep -u %s httpd | wc -l' %(app_uuid))
        if self.get_run_mode() == 'OnPremise':
            p.expect("2")
        else:
            p.expect(["6"])
        #p.sendline('ctl_app restart')
        #time.sleep(2)
        #p.expect(app_url)
        #p.sendline('ps -efww | grep "/usr/sbin/httpd" | grep -v "grep" | wc -l')
        ##p.sendline('pgrep -u %s httpd | wc -l' %(app_uuid))
        #if self.get_run_mode() == 'OnPremise':
        #    p.expect("2")
        #else:
        #    p.expect(["6"])
        p.sendline('ctl_all stop')
        p.expect(app_url)
        time.sleep(2)
        p.sendline('ps -efww | grep -v "grep" | wc -l')
        #p.sendline('pgrep -u %s | wc -l' %(app_uuid))
        p.expect(["5"])
        p.sendline('ctl_all start')
        p.expect(app_url)
        time.sleep(2)
        p.sendline('ps -efww | grep -v "grep" | wc -l')
        #p.sendline('pgrep -u %s | wc -l' %(app_uuid))
        if self.get_run_mode() == 'OnPremise':
            p.expect(["10", "11"])
        else:
            p.expect(["17", "18"])
        p.sendline('exit')
        p.expect('Connection to %s closed.'% app_url)
        return 0

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LoginViaRHCSH)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
