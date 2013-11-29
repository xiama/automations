"""
Linqing Lu
lilu@redhat.com
Dec 23, 2011

"""
import os
import sys

import rhtest
import testcase
import common
import commands

# TODO: if this failed, please refer to US1657 for more details
class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary="[integration][rhc-selinux]SELinux separation - scan context of processes"
        self.white_list=["haproxy"]
        common.env_setup()

class SELinuxScanProcess(OpenShiftTest):
    def test_method(self):
        ret = common.create_app("selinuxapp", common.app_types["python"])
        self.assert_equal(ret, 0, "The app should be created.")

        self.info("Check process context")
        ret = self.check_proc_context()
        self.assert_equal(ret, 0)

        return self.passed("%s passed" % self.__class__.__name__)

    def check_proc_context(self):
        (status, output) = common.run_remote_cmd_as_root("ps auxZ")
        if status!=0:
            return 1

        result = 0
        for line in output.split('\n'):
            app_without_user = 0
            if len(line)==0:
                continue
            print line 
            if '/var/lib/openshift/' in line:
                app_without_user = 1
            try:
                uid = line.split()[1]
            except Exception as e:
                self.error("Empty line?: %s"%e)
                continue
            if uid in self.white_list:
                continue
            if uid.isdigit() and int(uid)>=500:
                self.info("WHITE")
                app_without_user = 0
                context=line.split()[0]
                if not context.split(':')[2]=='libra_t':
                    self.info("WARN: SELinux type of user's proc doesn't match libra_t: %s"%context)
                    result += 1
                    continue
                if not ('c'+uid)==context.split(',')[1]:
                    print "WARN: SELinux MCS label of user's proc doesn't match uid:",context,uid
                    result += 1
            if app_without_user == 1:
                print "WARN: Tenant's proc got illegal uid:\n",line
                result += 1
        return result

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SELinuxScanProcess)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
