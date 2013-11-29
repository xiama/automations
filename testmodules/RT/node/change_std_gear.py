#
#  File name: change_std_gear.py
#  Date:      2012/02/24 07:55
#  Author:    mzimen@redhat.com
#

import sys
import os
import re

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[rhc-node] [US1823] Change STD 'gear' to new standard"
        self.app_name = common.getRandomString(10)
        self.res_limit_file = '/etc/openshift/resource_limits.conf.large'
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'jbossas'
        tcms_testcase_id = 135819
        self.steps = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class ChangeStdGear(OpenShiftTest):
    def test_method(self):

        '''self.steps.append(testcase.TestCaseStep("Verify the symlink to STD",
                        'ls -l /etc/openshift/resource_limits.conf|grep std && echo PASS',
                        expect_string_list = ['PASS'],
                        expect_return = 0))
        '''

        self.steps.append(testcase.TestCaseStep("Create a app",
                common.create_app,
                function_parameters=[self.app_name, 
                                     common.app_types[self.app_type], 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd, False],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Check the memory limits",
                self.cgsnapshot,
                expect_description = "Verify memory.limit_in_bytes=536870912 (512 MByte) & memory.memsw.limit_in_bytes = 641728512 (512 MByte + 100 MByte)", 
                expect_return=0))

        # Run the following command and in the output see the section 'group libra/<UUID>'

        self.steps.append(testcase.TestCaseStep("Create a app",
                self.repquota,
                expect_description = "Hard block limit for given user should be 1048576 (1GB)",
                expect_return=0))
    

        # Verify the file /etc/openshift/resource_limits.conf.large 

        self.steps.append(testcase.TestCaseStep("Verify limits in %s"%self.res_limit_file,
                self.verify_limits,
                expect_return=0))

        case = testcase.TestCase(self.summary, self.steps)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def cgsnapshot(self):
        uuid = OSConf.get_app_uuid(self.app_name)
        cmd="cgsnapshot -s | awk '/group libra\/%s/{yes=1} /^}/{if(yes==1) yes=0} {if(yes==1) print $0}'"%uuid
        (status, output) = common.run_remote_cmd_as_root(cmd)
        if status == 0:
            obj = re.search(r"memory.limit_in_bytes=\"536870912", output, re.MULTILINE)
            obj2 = re.search(r"memory.memsw.limit_in_bytes=\"641728512", output, re.MULTILINE)
            if obj and obj2:
                return 0
            else:
                print "ERROR: Unable to verify memory limits."
                return 1
        return 1

    def repquota(self):
        cmd = "repquota /var/ | awk '/^%s/{ print $5 }' "%OSConf.get_app_uuid(self.app_name)
        (status, output) = common.run_remote_cmd_as_root(cmd)
        obj = re.search(r"1048576", output)
        if obj:
            return 0
        return  1

    def verify_limits(self):
        cmd = "grep -c -e 'quota_blocks=1048576' -e 'memory_limit_in_bytes=1073741824' -e 'memory_memsw_limit_in_bytes=1178599424' '%s' && echo PASS"%self.res_limit_file

        (status, output) = common.run_remote_cmd_as_root(cmd)
        obj = re.search(r"PASS", output)
        if (obj):
            return 0
        return 1

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ChangeStdGear)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of change_std_gear.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
