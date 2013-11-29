"""
Jianlin Liu
jialiu@redhat.com
Dec 30, 2011
[Security] Check polyinstantiation of /tmp and /var/tmp via git push
https://tcms.engineering.redhat.com/case/122328/?from_plan=4962
"""

import os
import sys
import re

import testcase
import common 
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[Security] Check polyinstantiation of /tmp and /var/tmp via git push"
        self.app_type = "python-2.6"
        self.app_name1 = "SecurityTestApp1"
        self.app_name2 = "SecurityTestApp2"
        tcms_testcase_id=122328

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name1, self.app_name2))

class PolyinstantiantionTmpDirGitPush(OpenShiftTest):
    def test_method(self):
        self.info("1. Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name1, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd, True)
        self.assert_equal(ret, 0, "%s app should be created successfully" %(self.app_name1))

        def rewrite_app(target_file, context):
            print "---Append test code to %s---" %(target_file)
            file = open(target_file, "a")
            file.write(context)
            file.close()

        target_file = self.app_name1 + "/setup.py"
        test_code = """
import commands
 
f = open('/tmp/wsgi_tmp_test_git_push', 'w')
f.write('testing')
f.close()
 
f = open('/var/tmp/wsgi_var_tmp_test_git_push', 'w')
f.write('testing')
f.close()
 
command1 = "ls -l /tmp/wsgi_tmp_test_git_push"
print "Command 1: %s" %(command1)
(ret1, output) = commands.getstatusoutput(command1)
print output
 
command2 = "ls -l /var/tmp/wsgi_var_tmp_test_git_push"
print "Command 2: %s" %(command2)
(ret2, output) = commands.getstatusoutput(command2)
print output
 
command = "ls -l /tmp"
print "Command: %s" %(command)
(tmp_ret, output) = commands.getstatusoutput(command)
print output
 
if ret1 == 0 and ret2 == 0:
    print "RESULT=0"
else:
    print "RESULT=1"
"""

        self.info("2. Modify setup.py")
        rewrite_app(target_file, test_code)

        self.info("3.Do git commit")
        (ret, output) = common.command_getstatusoutput("cd %s && git add . && git commit -m test && git push" %(self.app_name1))

        self.assert_equal(ret, 0)
        if (not re.search(r"RESULT=0", output)):
            self.assert_failed("Missing RESULT=0 in git output")

        self.info("Create another application")
        ret = common.create_app(self.app_name2, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd, True)
        self.assert_equal(ret, 0, "%s app#2 should be created successfully" %(self.app_name2))

        target_file = self.app_name2 + "/setup.py"
        test_code = """
import commands
 
command1 = "ls -l /tmp/wsgi_tmp_test_git_push"
print "Command 1: %s" %(command1)
(ret1, output) = commands.getstatusoutput(command1)
print output
 
command2 = "ls -l /var/tmp/wsgi_var_tmp_test_git_push"
print "Command 2: %s" %(command2)
(ret2, output) = commands.getstatusoutput(command2)
print output
 
command = "ls -l /tmp"
print "Command: %s" %(command)
(tmp_ret, output) = commands.getstatusoutput(command)
print output
 
if ret1 == 0 or ret2 == 0:
    print "RESULT=0"
else:
    print "RESULT=1"
"""
        self.info("Modify setup.py") 
        rewrite_app(target_file, test_code)
 
        self.info("Do git commit")
        (ret, output) = common.command_getstatusoutput("cd %s && git add . && git commit -m test && git push" %(self.app_name2))

        self.assert_equal(ret, 0)
        if (not re.search(r"RESULT=1", output) or not re.search(r"No such file or directory", output)):
            self.assert_failed("Missing RESULT=0 in git output")



        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PolyinstantiantionTmpDirGitPush)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
