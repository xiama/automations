"""
??
??
"""

import sys
import os
import string
import rhtest

import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_limit_per_user = common.get_max_gears() #string.atoi(os.environ["OPENSHIFT_app_limit_per_user"])
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types["php"]
        self.app_name_prefix = common.getRandomString(7)

class AppLimitPerUserConcurentCreation(OpenShiftTest):
    def test_method(self):
        ret_list = []
        for i in range(3):
            common.env_setup()
            step = testcase.TestCaseStep(
                    "Try %s: Create more apps than app_limit_per_user setting upon %s concurrent creation" %(i + 1, self.app_limit_per_user + 2),
                    self.concrrent_creation_step,
                    function_parameters=[1, self.app_limit_per_user + 2],
                    expect_description="No more apps beyond limit should be created")

            (ret_dict, output) = step.run()
            # print ret_dict
            if ret_dict.values().count(0) == self.app_limit_per_user:
                ret_list.append(0)
                # Init OSConf to clean these apps in next iterval
                OSConf.initial_conf()
            else:
                ret_list.append(1)
                # Init OSConf to clean these apps in next script
                OSConf.initial_conf()
                break


        #print ret_list
        if ret_list.count(1) > 0:
            print "Upon %s concurrent creation, more apps than app_limit_per_user is created - [FAIL]" %(self.app_limit_per_user + 2)
            return self.failed("%s failed" % self.__class__.__name__)
        else:
            return self.passed("%s passed" % self.__class__.__name__)


    def concrrent_creation_step(self, start, end):
        command_list = []
        for i in range(start, end + 1):
            self.app_name = "%s%s" %(self.app_name_prefix, i)
            command_list.append("rhc app create %s %s -l %s -p '%s' --no-git %s" %(self.app_name, self.app_type, self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))

        ret_dict = common.multi_subprocess(command_list)
        for i in ret_dict.keys():
            print "Command {%s} return: %s" %(i, ret_dict[i])

        return ret_dict


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppLimitPerUserConcurentCreation)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
