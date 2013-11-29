#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com

[US2031][BusinessIntegration][Mirage] oo-admin-chk [ruby]
https://tcms.engineering.redhat.com/case/141104/
"""

import os
import sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    ITEST = "DEV"

    def initialize(self):
        self.app_name = common.getRandomString(10)
        self.app_name2 = common.getRandomString(10)
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = 'php'
        self.summary = "[US2031][BusinessIntegration][Mirage] oo-admin-chk"

    	common.env_setup()

    def finalize(self):
        pass

class RhcAdminCheck(OpenShiftTest):
    def run_rhc_admin_check(self):
        cmd = "oo-admin-chk"
        return common.run_remote_cmd(None, cmd, True)

    def remove_apps_from_mongo(self):
        mongo_script = [
            "use admin",
            "db.auth('libra', 'momo')",
            "use openshift_broker_dev",
            "u = db.user.findOne( { '_id' : '%s' } )" % self.config.OPENSHIFT_user_email,
            "u['apps'] = [ ]",
            "u['consumed_gears'] = 0",
            "db.user.save(u)" 
        ]
        run_steps = [
            'echo "%s"' % "\n".join(mongo_script),
            'mongo'          
        ]
        return common.run_remote_cmd_as_root(" | ".join(run_steps))
    
    def finalize(self):
        self.remove_apps_from_mongo()
        for app_name in [ self.app_name, self.app_name2 ]:
            uuid = OSConf.get_app_uuid(app_name)
            app_url = OSConf.get_app_url(app_name)
            common.destroy_app(app_name)
            if uuid != 1:
                common.run_remote_cmd_as_root("rm -Rf /var/lib/openshift/%s" % uuid, app_url)
                common.run_remote_cmd_as_root("rm -Rf /var/lib/openshift/%s-*" % app_name, app_url)

    def test_method(self):
        self.info("===============================")
        self.info("1. Creating an application")
        self.info("===============================")
        common.create_app(self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, clone_repo=False)
        
        self.info("===============================")
        self.info("2. oo-admin-chk")
        self.info("===============================")
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_equal(ret_code, 0)
        self.assert_true(ret_output.find("Success") != -1)
        
        self.info("===============================")
        self.info("3. Removing application directory on the node")
        self.info("===============================")
        uuid = OSConf.get_app_uuid(self.app_name)
        app_url = OSConf.get_app_url(self.app_name)
        ( ret_code, ret_output ) = common.run_remote_cmd_as_root("rm -Rf /var/lib/openshift/%s" % uuid, app_url)
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_false(ret_code == 0)
        self.assert_true(ret_output.find("does not exist on any node") != -1)
        
        self.info("===============================")
        self.info("4. Fix the problem by removing the application from MongoDB and run oo-admin-check")
        self.info("===============================")
        self.remove_apps_from_mongo()
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_equal(ret_code, 0)
        self.assert_true(ret_output.find("Success") != -1)
        
        self.info("===============================")
        self.info("5. Create another application")
        self.info("===============================")
        common.create_app(self.app_name2, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, clone_repo=False)
        
        self.info("===============================")
        self.info("6. Remove the application from MongoDB")
        self.info("===============================")
        self.remove_apps_from_mongo()
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_false(ret_code == 0)
        
        self.info("===============================")
        self.info("7. Fix the problem by removing the application directory on the node")
        self.info("===============================")
        uuid = OSConf.get_app_uuid(self.app_name2)
        app_url = OSConf.get_app_url(self.app_name2)
        common.run_remote_cmd_as_root("rm -Rf /var/lib/openshift/%s" % uuid, app_url)
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_equal(ret_code, 0)
        self.assert_true(ret_output.find("Success") != -1)
        
        self.info("===============================")
        self.info("8. Configuring consumed_gears property incorrectly (Bug 816462)")
        self.info("===============================")
        common.run_remote_cmd_as_root("oo-admin-ctl-user -l %s --setconsumedgears 999" % self.config.OPENSHIFT_user_email)
        ( ret_code, ret_output ) = self.run_rhc_admin_check()
        self.assert_false(ret_code == 0)
        
        # Everything is OK
        return self.passed(self.summary)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcAdminCheck)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
