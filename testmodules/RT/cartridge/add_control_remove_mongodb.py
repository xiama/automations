#!/usr/bin/env python

import os
import testcase
import common
import OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1209][US1347][Runtime][cartridge]embed MongoDB to all kinds of app\n[US1209][Runtime][cartridge]Control embed mongodb"
        try:
            test_name = self.get_variant()
        except:
            self.info("Missing variant, used 'php' as default")
            test_name = 'php'

        try:
            self.environment = self.config.options.run_mode
        except:
            self.info("Missing self.config.options.run_mode, used 'DEV' as default")
            self.environment = "DEV"
        self.info("VARIANT: %s"%test_name)
        self.app_type = common.app_types[test_name]
        self.app_name = common.getRandomString(10)
        tcms_testcase_id=121913
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s* "%(self.app_name))

class AddControlRemoveMongodb(OpenShiftTest):
    def test_method(self):
        app_name = self.app_name
        self.steps_list.append(testcase.TestCaseStep("Create a %s application" %(self.app_type),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0,
                expect_description="App should be created successfully"))

#this will be as __OUTPUT__[2]
        self.steps_list.append(testcase.TestCaseStep("Get app url",
                OSConf.get_app_url_X,
                function_parameters = [self.app_name]))

#this will be as __OUTPUT__[3]
        self.steps_list.append(testcase.TestCaseStep("Get app uuid",
                OSConf.get_app_uuid_X,
                function_parameters = [self.app_name]))

        #4
        self.steps_list.append(testcase.TestCaseStep("Embed MongoDB to this app",
                common.embed,
                function_parameters=[self.app_name, 
                                     "add-%s"%common.cartridge_types['mongodb'], 
                                     self.config.OPENSHIFT_user_email, 
                                     self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        #5
        self.steps_list.append(testcase.TestCaseStep("Get embeded mongo info - password",
                OSConf.get_embed_info_X,
                function_parameters=[self.app_name, common.cartridge_types["mongodb"], "password"]))

        #6
        self.steps_list.append(testcase.TestCaseStep("Get embeded mongo info - url",
                OSConf.get_embed_info_X,
                function_parameters=[self.app_name, common.cartridge_types["mongodb"], "url"]))

        mongo_shell_write_input_file = "./mongo_shell_write_input"
        mongo_shell_read_input_file  = "./config.mongo_shell_read_input"
        test_Collection_name = "test"
        test_data = "TesterName"

        #7
        command = """echo -e 'use %s\ndb\nshow collections\ndb.%s.save({"name":"%s"})\nexit\n' >%s""" %(self.app_name, test_Collection_name, test_data, mongo_shell_write_input_file)
        self.steps_list.append(testcase.TestCaseStep("Write mongo shell input file - write",
                command, 
                expect_return=0))

        command = """echo -e 'use %s\ndb\nshow collections\ndb.%s.find()\nexit\n' >%s""" %(self.app_name, test_Collection_name, mongo_shell_read_input_file)
        #8
        self.steps_list.append(testcase.TestCaseStep("Write mongo shell input file - read",
                command,
                expect_return=0))

        #9
        self.steps_list.append(testcase.TestCaseStep("Do some write operation to mongodb",
                """ssh -t -t %s@%s rhcsh mongo < %s""" ,
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_write_input_file),                     
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_write_input_file],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift shell", "MongoDB shell", self.app_name],
                unexpect_string_list=["errmsg"]))

        #10
        self.steps_list.append(testcase.TestCaseStep(
                "Do some query operation to mongodb to check write operation is succesful",
                """ssh -t -t %s@%s rhcsh mongo < %s""", 
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift shell", "MongoDB shell", app_name, test_Collection_name, test_data],
                unexpect_string_list=["errmsg"]))

        #11
        self.steps_list.append(testcase.TestCaseStep("Stop this embed db using 'rhc cartridge stop'",
                "rhc cartridge stop %s -a %s -l %s -p '%s' %s" 
                    %(common.cartridge_types['mongodb'], app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS), 
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Check this db status",
                "rhc cartridge status %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['mongodb'], app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0,
                expect_string_list=["MongoDB is stopped"]))

        #12
        self.steps_list.append(testcase.TestCaseStep(
                "Try to do some query operation to mongodb to check db is NOT running",
                """ssh -t -t %s@%s rhcsh mongo < %s""" ,
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
                expect_return = "!0",
                expect_string_list=["Welcome to OpenShift shell", "MongoDB shell", "connect failed"],
                unexpect_string_list=[test_data,]))

        #13
        self.steps_list.append(testcase.TestCaseStep("Start this embed db using 'rhc cartridge start'",
                "rhc cartridge start %s -a %s -l %s -p '%s' %s" 
                    %(common.cartridge_types['mongodb'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0))

        #14
        self.steps_list.append(testcase.TestCaseStep("Check this db status",
                "rhc cartridge status %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['mongodb'], app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0,
                expect_string_list=["MongoDB is running"]))

        #15
        self.steps_list.append(testcase.TestCaseStep(
                "Do some query operation to mongodb to check db is running",
                """ssh -t -t %s@%s rhcsh mongo < %s""" ,
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift shell", 
                                    "MongoDB shell", 
                                    self.app_name, 
                                    test_Collection_name, 
                                    test_data],
                unexpect_string_list=["errmsg"]))

        #16
        self.steps_list.append(testcase.TestCaseStep("Re-start this embed db using 'rhc cartridge restart'",
                "rhc cartridge restart %s -a %s -l %s -p '%s' %s" 
                    %(common.cartridge_types['mongodb'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0))

        #17
        self.steps_list.append(testcase.TestCaseStep(
                "Do some query operation to mongodb to check db is running",
                """ssh -t -t %s@%s rhcsh mongo < %s""",
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift shell", 
                                    "MongoDB shell", 
                                    self.app_name, 
                                    test_Collection_name, 
                                    test_data],
                unexpect_string_list=["errmsg"]))

        #18
        self.steps_list.append(testcase.TestCaseStep("Reload this embed db using 'rhc cartridge reload'",
                "rhc cartridge reload %s -a %s -l %s -p '%s' %s" %(common.cartridge_types['mongodb'], self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                expect_return=0))

        #19
        self.steps_list.append(testcase.TestCaseStep(
                "Do some query operation to mongodb to check db is running",
                """ssh -t -t %s@%s rhcsh mongo < %s""" ,
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
                expect_return=0,
                expect_string_list=["Welcome to OpenShift shell", "MongoDB shell", self.app_name, test_Collection_name, test_data],
                unexpect_string_list=["errmsg"]))

        #20
        self.steps_list.append(testcase.TestCaseStep("Remove MongoDB from this app",
                common.embed,
                function_parameters=[app_name, 
                                    "remove-%s"%common.cartridge_types["mongodb"], 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        if self.environment == "STG":
            _expect_string_list=["Welcome to OpenShift shell", "MongoDB shell", "connect failed"]
        else:
            _expect_string_list=["Welcome to OpenShift shell", "MongoDB shell"]

        #21
        self.steps_list.append(testcase.TestCaseStep(
                "Try to do some query operation to mongodb to check db is NOT running",
                """ssh -t -t %s@%s rhcsh mongo < %s""" ,
                    #%("__OUTPUT__[3]", "__OUTPUT__[2]", mongo_shell_read_input_file),
                string_parameters = [OSConf.get_app_uuid_X(self.app_name), 
                                     OSConf.get_app_url_X(self.app_name), 
                                     mongo_shell_read_input_file],
#               expect_return="!0",
                expect_string_list=_expect_string_list,
                unexpect_string_list=[test_data]))


        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AddControlRemoveMongodb)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
