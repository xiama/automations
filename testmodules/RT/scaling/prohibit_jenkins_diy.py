#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
May 9, 2012

[US2089][BI] Prohibit an app of jenkins/diy type from being created as scalable app
https://tcms.engineering.redhat.com/case/145114
"""
import rhtest
#### test specific import
import common
import openshift
import json


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US2089][BI] Prohibit an app of jenkins/diy type from being created as scalable app"
        self.step = 0
        common.env_setup()

    def finalize(self):
        common.clean_up()
    

class ProhibitScalableJenkinsDiy(OpenShiftTest):
    def test_method(self):
        step = 0
        #for app_type in [ common.app_types['jenkins'], common.app_types['diy'], 'zend-5.6' ]:
        for app_type in [ common.app_types['jenkins'], common.app_types['diy'] ]:
            self.step = self.step + 1
            self.info("==========================================")
            self.info("Creating application via REST API: " + app_type)
            self.info("==========================================")
            (status, res) = self.config.rest_api.app_create("testapp%d" % self.step, app_type, 'true')
            self.info("status=%s, response=%s"%(status, res))
            self.assert_not_equal(status, 'OK', "It's possible to create a scalable app via RESt API with type " + app_type)
            #jmsg = res.json['messages']['text']
            #self.assert_not_equal(jmsg, 'Scalable app cannot be of type %s' %("'" + app_type + "'"), "Wrong returned message!")
            
            self.info("==========================================")
            self.info("Creating application in command line: " + app_type)
            self.info("==========================================")
            ( ret_code, ret_output ) = common.command_getstatusoutput("rhc app create testapp%d %s -s --no-git -l %s -p '%s' %s" % ( self.step, app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))

            self.assert_true( ret_code != 0, "It's possible to create a scalable application with type " + app_type )
            self.assert_true( ret_output.find("Scalable app cannot be of type") != -1, "Error-message must be meaningful")

        return self.passed(self.summary)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ProhibitScalableJenkinsDiy)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
