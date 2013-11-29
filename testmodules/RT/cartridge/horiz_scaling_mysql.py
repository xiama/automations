
#
#  File name: horiz_scaling_mysql.py
#  Date:      2012/03/09 02:30
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    def initialize(self):

        self.app_name = 'scalapp'
        try:
            self.app_type = self.config.test_variant
        except:
            self.app_type = 'php'

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class HorizScalingMysql(OpenShiftTest):
    def test_method(self):
        #1. create manually scalable APP
        ret = common.create_scalable_app(self.app_name, 
                          common.app_types[self.app_type],
                          self.config.OPENSHIFT_user_email,
                          self.config.OPENSHIFT_user_passwd)

        self.assert_equal(ret, 0, "Unable to create scalable PHP application")

        #embed with MYSQL
        ret = common.embed(self.app_name,
                "add-%s"%common.cartridge_types['mysql'], 
                self.config.OPENSHIFT_user_email, 
                self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret,0, "To embed MySQL should work")
        #or use this direct call?
        #cmd = 'curl -k -H "Accept: application/xml" -u "%s:%s" https://%s/broker/rest/domains/%s/applications/scala/cartridges -X POST -d name=%s -d cartridge=%s -d %s="%s"'%(self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, libra_server, self.config.OPENSHIFT_domain_name, self.app_name,common.cartridge_types['mysql'],'haproxy','mysql')
        #(status, output) = common.command_getstatusoutput(cmd)
        #if status!=0:
        #    print "ERROR: Unable to create scalable PHP application"
        #    sys.exit(status)

        return self.passed("%s passed" % self.__class__.__name__)
        #if case.testcase_status == 'FAILED':
        #    return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(HorizScalingMysql)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of horiz_scaling_mysql.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
