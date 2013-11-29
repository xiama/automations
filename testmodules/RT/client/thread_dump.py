#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-08-15

[US2123][UI][rhc-client]threaddump for ruby-1.9 app
https://tcms.engineering.redhat.com/case/177961/
"""
import os
import common
import re
import OSConf
import rhtest
import pexpect
import time

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `ruby` as default")
            self.test_variant = 'jbossews'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        if self.test_variant in ('ruby', 'ruby-1.9'):
            self.str_list = ['backtrace dump', 'abstract_request_handler.rb', 'install_useful_signal_handlers', 'call', 'accept_and_process_next_request', 'main_loop', 'start_request_handler']
        elif self.test_variant in ('jbossas', 'jbosseap', 'jbossews', 'jbossews2','jbossews-2.0'):
            self.str_list = ['ContainerBackgroundProcessor', 'ConnectionValidator', 'IdleRemover', 'server-timer', 'DestroyJavaVM', 'MSC service', 'Reference Reaper', 'Finalizer', 'Reference Handler', 'Finalizer', 'Reference Handler', 'Heap']
        self.summary = "[US2123][UI][rhc-client]threaddump for %s app" % (self.test_variant)
        self.app_type = common.app_types[self.test_variant]
        self.app_name = "threaddump" + common.getRandomString(4)
        self.git_repo = "./%s" % (self.app_name)
        self.match_rate = 0.3
        common.env_setup()

    def finalize(self):
        try:
            self.child.sendcontrol('c')
        except:
            pass


class ThreaddumpTest(OpenShiftTest):
    def test_method(self):
        self.step("Create %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd, 
                                scalable=self.scalable, 
                                disable_autoscaling=False)
        self.assert_equal(ret, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))

        self.step("Add databases to the app")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to add mysql")

        ret = common.embed(self.app_name, "add-" + common.cartridge_types["postgresql"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to add postgresql")

        #ret = common.embed(self.app_name, "add-" + common.cartridge_types["mongodb"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        #self.assert_equal(ret, 0, "Failed to add mongodb")

        self.step("Applications must be accessed by their URL before you can take a thread dump")
        app_url = OSConf.get_app_url(self.app_name)
        cmd = "curl %s" %(app_url)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(ret, 0, "Fail to access app")

        self.step("Generate threaddump file")
        cmd = "rhc threaddump %s -l %s -p '%s' %s" % (  self.app_name, 
                                                        self.config.OPENSHIFT_user_email, 
                                                        self.config.OPENSHIFT_user_passwd,
                                                        common.RHTEST_RHC_CLIENT_OPTIONS)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(ret, 0, "Failed to generate threaddump file for %s app: %s" % (self.app_type, self.app_name))
        self.debug("OUTPUT: %s" % output)
        match = re.search(r'(?<=The thread dump file will be available via: ).*$', output, re.M)
        #match = re.search(r'(?<=rhc tail %s )-f \S+' % (self.app_name), output)
        self.assert_not_equal(match, None, "Failed to find command to see the threaddump file")

        self.step("Check the threaddump file")
        #tail_cmd = "rhc tail %s " % (self.app_name) + match.group(0) + " -l %s -p '%s'" % (self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        tail_cmd = match.group(0) + " -l %s -p '%s'" % (self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        print "Command: %s" % (tail_cmd)
        self.child = pexpect.spawn(tail_cmd)
        time.sleep(10)
        match_num = 0.0
        for s in self.str_list:
            try:
                # increase the timeout from 3 to 10
                self.child.expect(s, timeout=20)
                match_num += 1
            except pexpect.TIMEOUT:
                pass
        rate = match_num/len(self.str_list)
        if rate >= self.match_rate:
            self.info("Successfully matched %d%% strings in the list" % (int(rate*100)))
            return self.passed()
        else:
            self.info("Only matched %d%% strings in the list. The lowest match rate is %f%%" % (int(rate*100), int(self.match_rate*100)))
            return self.failed()



class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ThreaddumpTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
