#!/usr/bin/python

#
#  File name: snapshot_restore_mongodb.py
#  Date:      2012/03/20 13:47
#  Author:    mzimen@redhat.com
#

import os
import common
import rhtest
import OSConf


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1209][RT][cartridge]take snapshot and restore without new app for embedded mongodb")
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = 'jbossews'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        self.mongo_type = "mongodb"

        self.info("VARIANT: %s"%self.app_type)
        self.info("SCALABLE: %s"%self.scalable)
        self.snapshot_file = "snapshot_%s.tar.gz"%self.app_name

        common.env_setup()

    def finalize(self):
        pass

class SnapshotRestoreMongodb(OpenShiftTest):
    def test_method(self):
        #1
        if self.scalable:
            self.add_step("Create scalable %s application"%self.app_type,
                    common.create_scalable_app,
                    function_parameters=[self.app_name, 
                                         common.app_types[self.app_type], 
                                         self.config.OPENSHIFT_user_email, 
                                         self.config.OPENSHIFT_user_passwd, 
                                         False],
                    expect_return=0)
        else:
            self.add_step("Create a %s application"%self.app_type,
                common.create_app,
                function_parameters=[self.app_name, 
                                     common.app_types[self.app_type], 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd, 
                                     True],
                expect_return=0)

        #2
        self.add_step("Embed with mongodb" ,
            common.embed,
            function_parameters = [self.app_name,
                                   'add-%s'%common.cartridge_types[self.mongo_type],
                                   self.config.OPENSHIFT_user_email, 
                                   self.config.OPENSHIFT_user_passwd],
            expect_return=0)

        if self.scalable:
            self.add_step("Scale up...",
                #self.config.rest_api.app_scale_up,
                common.scale_up,
                function_parameters = [self.app_name],
                expect_return=0)

        self.add_step("Insert initial data into mongoDB",
            self.process_mongo_data,
            function_parameters = ['insert', '{"name1": "Tim" }'],
            expect_return=0)

        self.add_step("Insert initial data into mongoDB",
            self.process_mongo_data,
            function_parameters = ['insert', '{"name1": "Jim" }'],
            expect_return=0)

        self.add_step("Verify recent insert into mongoDB",
            self.process_mongo_data,
            function_parameters = ['find', '{"name1": "Jim" }', "Jim"],
            expect_description = 'Entry of "Jim" should be there...',
            expect_return=0)

        self.add_step("Verify recent insert into mongoDB",
            self.process_mongo_data,
            function_parameters = ['find', '{"name1": "Tim" }', "Tim"],
            expect_description = 'Entry of "Tim" should be there...',
            expect_return=0)

        self.add_step("Make a snapshot",
            "rhc snapshot save %s -l %s -p '%s' -f %s %s"
                %(self.app_name,
                self.config.OPENSHIFT_user_email,
                self.config.OPENSHIFT_user_passwd,
                self.snapshot_file,
                common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_return=0)

        #6
        self.add_step("Drop the initial data from mongoDB",
            self.process_mongo_data,
            function_parameters=['remove', '{"name1": "Jim" }'],
            expect_description = 'Jim should be removed without errors...',
            expect_return=0)

        self.add_step("Insert Tom into mongoDB",
            self.process_mongo_data,
            function_parameters=['insert', '{"name1": "Tom" }'],
            expect_description = 'Tom should be added without errors...',
            expect_return=0)

        #7
        self.add_step("Verify recent drop from mongoDB",
            self.process_mongo_data,
            function_parameters=['find', '{"name1": "Jim" }',None,"Jim"],
            expect_description = '"Jim" should not be there...',
            expect_return = 1)
                
        self.add_step("Verify recent insert to mongoDB",
            self.process_mongo_data,
            function_parameters=['find', '{"name1": "Tom" }', "Tom"],
            expect_description = '"Tom" should be there...',
            expect_return=0)
                
        #8
        self.add_step("Restore from snapshot",
            "rhc snapshot restore %s -l %s -p '%s' -f %s %s"
            %(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, self.snapshot_file, common.RHTEST_RHC_CLIENT_OPTIONS),
            expect_description = 'Should pass',
            expect_return=0)

        #9
        self.add_step("Check if the Tim is there",
            self.process_mongo_data,
            function_parameters = ['find', '{"name1": "Tim"}', "Tim"],
            expect_description = 'Tim should be there there.',
            expect_return = 0)

        self.add_step("Check if the Jim is there",
            self.process_mongo_data,
            function_parameters = ['find', '{"name1": "Jim"}', "Jim"],
            expect_description = 'Jim should be there.',
            expect_return = 0)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)

    def process_mongo_data(self, operation, data, expect_str=None, unexpect_str=None):
        mongo_cred = OSConf.get_embed_info(self.app_name, common.cartridge_types[self.mongo_type])
        
        #print mongo_cred
        #print mongo_cred["username"]
        script = "db.test.%s(%s)"%(operation, data)
        if (operation == 'find'):
            script += ".forEach(printjson)"
        script += ";"

        js_script = "/tmp/m.js"
        mongo_cmds = "echo 'use %s;' >%s"%(self.app_name,js_script)
        mongo_cmds += "; echo '%s' >>%s"%(script, js_script)
        mongo_cmds += "; mongo --verbose -u %s -p %s %s:%s/admin < %s "%(
                            mongo_cred["username"],
                            mongo_cred["password"],
                            mongo_cred['url'],
                            mongo_cred['port'],
                            js_script)
        if operation == 'find':
            mongo_cmds += " | grep ObjectId "

        (status, output) = common.run_remote_cmd(self.app_name, mongo_cmds)

        if expect_str:
            self.assert_match(expect_str, output, "Unable to find `%s` string in the output."%expect_str)
        if unexpect_str:
            self.assert_not_match(unexpect_str, output, "Unexpected `%s` string in the output."%unexpect_str)

        return status

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SnapshotRestoreMongodb)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of snapshot_restore_mongodb.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
