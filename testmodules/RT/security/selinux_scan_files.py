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

class OpenShiftTest(rhtest.Test):
    ITEST="DEV"
    def initialize(self):
        self.summary="[integration][rhc-selinux]SELinux separation - scan context of files"
        self.app_name = 'scanfile'
        self.app_type = common.app_types['php']

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class SelinuxScanFiles(OpenShiftTest):
    def test_method(self):
        # 1.Create an app
        self.info("Create a %s application" %(self.app_type))
        ret = common.create_app(self.app_name, 
                                self.app_type, 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd, 
                                False)
        self.assert_equal(ret, 0, "App should be created successfully")

        # 2. Scan files
        self.info("Check file context")
        ret=self.check_file_context()
        self.assert_equal(ret, 0) 

        return self.passed("%s passed" % self.__class__.__name__)

    def check_file_context(self):
        libra_fc=[['/etc/rc\.d/init\.d/libra','system_u:object_r:libra_initrc_exec_t:s0'],['/etc/rc\.d/init\.d/mcollective','system_u:object_r:libra_initrc_exec_t:s0'],['/var/lib/openshift/*','system_u:object_r:libra_var_lib_t:s0'],['/var/lib/openshift/*/.ssh','system_u:object_r:ssh_home_t:s0']]
        for libra_fc_rule in libra_fc:
            cmd='ls -Z %s'%(libra_fc_rule[0])
            (status, output) = common.run_remote_cmd_as_root(cmd)
            print output
            print "------"
            if status!=0:
                return 1
            for line in output.split('\n'):
                if len(line.split())!=4 or ('lrwxrwxrwx.' in line):
                    continue
                print line
                context_proc = line.split()[3]
                print context_proc
                context_rule = libra_fc_rule[1]
                print context_rule
                type_proc = context_proc.split(':')[2]
                type_rule = context_rule.split(':')[2]
#            if cmp(context_proc,context_rule)!=0:
#                print 'WARN:',context_proc,'differ from',context_rule
                if cmp(type_proc,type_rule)!=0:
                    print 'WARN:',type_proc,'differ from',type_rule
                    print line
                    return 1
        return 0


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SelinuxScanFiles)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
