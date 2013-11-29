#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-07-23

[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support
https://tcms.engineering.redhat.com/case/138803/
"""
import os
import common
import OSConf
import rhtest
import time
import pexpect
import re

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'jbossews-2.0'
            self.info("WARN: Missing variant, used `%s` as default" % (self.test_variant))
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        if self.scalable:
            self.scalable = True

        self.file_path = {  'jbossas'   : 'src/main/webapp/index.html',
                            'python'    : 'wsgi/application',
                            'ruby'      : 'config.ru',
                            'php'       : 'php/index.php',
                            'perl'      : 'perl/index.pl',
                        }
        self.file_path['jbosseap'] = self.file_path['jbossas']
        self.file_path['jbossews'] = self.file_path['jbossas']
        self.file_path['jbossews-2.0'] = self.file_path['jbossas']
        self.file_path['ruby-1.9'] = self.file_path['ruby']

        self.summary = "[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support"
        self.app_name = "hotdeploy" + common.getRandomString(4)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name)
        common.env_setup()

    def finalize(self):
        pass



class HotDeploy(OpenShiftTest):
    def get_pids(self, app_name):
        pids = []
        if self.app_type.split('-')[0] in ('jbossas', 'jbosseap'):
            cmd = "ssh %s 'ps aux | grep -i standalone'" % (OSConf.get_ssh_url(app_name))
        elif 'jbossews' in self.app_type:
            cmd = "ssh %s 'ps aux | grep '/bin/bash'" % (OSConf.get_ssh_url(app_name))
        else:
            cmd = "ssh %s 'ps aux | grep bin/httpd'" % (OSConf.get_ssh_url(app_name))
        child = pexpect.spawn(cmd)
        for line in child.readlines():
            match = None
            if self.app_type.split('-')[0] in ('jbossas', 'jbosseap'):
                if 'jre' in line or 'standalone.sh' in line:
                    print line
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            elif 'jbossews' in self.app_type:
                if 'jbossews//bin/tomcat' in line:
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            else:
                if 'httpd -C Include' in line:
                    match = re.search(r'^\d+\s+(\d+)', line, re.M)
            if match:
                if match.group(1) not in pids:
                    pids.append(int(match.group(1)))
        pids.sort()
        return pids

    def compare_pid(self, lst1, lst2):
        if len(lst1) > len(lst2):
            return False
        for i in range(len(lst1)):
            if lst1[i] != lst2[i]:
                return False
        return True

    def test_method(self):
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", self.scalable)
        self.assert_equal(ret, 0, "App creation failed")
        # Add hot_deploy marker
        ret = common.command_get_status("touch %s/.openshift/markers/hot_deploy" % (self.app_name))
        self.assert_equal(ret, 0, "Failed to create hot_deploy marker")
        # Record the pids
        pid_lst1 = self.get_pids(self.app_name)
        print 'pid list: %s' % pid_lst1
        self.assert_not_equal(len(pid_lst1), 0, "Failed to get pid")
        # Make some changes and git push
        self.str1 = 'Welcome to OpenShift'
        self.str2 = common.getRandomString()
        cmd = "sed -i -e 's/%s/%s/g' %s/%s" % (self.str1, self.str2, self.app_name, self.file_path[self.test_variant])
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to modify the app")
        # Git push all the changes
        (ret, output) = common.command_getstatusoutput("cd %s && git add . && git commit -amt && git push" % (self.app_name))
        self.assert_equal(ret, 0, "Failed to git push")
        self.assert_not_match('Waiting for stop to finish', output, "'Waiting for stop to finish' shouldn't be found in the output")
        # Verify the changes
        ret = common.check_web_page_output(self.app_name, '', self.str2)
        self.assert_equal(ret, 0, "The changes doesn't take effect")
        # Get the pid and compare
        pid_lst2 = self.get_pids(self.app_name)
        print 'pid before git push: %s' % (pid_lst1)
        print 'pid after  git push: %s' % (pid_lst2)
        self.assert_not_equal(len(pid_lst2), 0, "Failed to get pid")
        ret = self.compare_pid(pid_lst1, pid_lst2)
        self.assert_true(ret, 'PID changed after deploying')
        # Create jenkins server
        ret = common.create_app("jenkins", common.app_types['jenkins'])
        self.assert_equal(ret, 0, "Failed to create jenkins server")
        # Add jenkins-client to the app
        ret = common.embed(self.app_name, 'add-' + common.cartridge_types['jenkins'])
        self.assert_equal(ret, 0, "Failed to add jenkins-client to the app")
        # Make some changes
        self.str1 = self.str2
        self.str2 = common.getRandomString()
        cmd = "sed -i -e 's/%s/%s/g' %s/%s" % (self.str1, self.str2, self.app_name, self.file_path[self.test_variant])
        ret = common.command_get_status(cmd)
        self.assert_equal(ret, 0, "Failed to modify the app")
        # Git push all the changes
        ret = common.trigger_jenkins_build(self.app_name)
        self.assert_true(ret, "Failed to do jenkins build")
        # Verify the changes
        ret = common.check_web_page_output(self.app_name, '', self.str2)
        self.assert_equal(ret, 0, "The changes doesn't take effect")
        # Compare the pids
        pid_lst1 = pid_lst2
        pid_lst2 = self.get_pids(self.app_name)
        print 'pid before git push: %s' % (pid_lst1)
        print 'pid after  git push: %s' % (pid_lst2)
        self.assert_not_equal(len(pid_lst2), 0, "Failed to get pid")
        ret = self.compare_pid(pid_lst1, pid_lst2)
        self.assert_true(ret, 'PID changed after deploying')
        return self.passed()


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(HotDeploy)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
