"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US945][rhc-cartridge] Add modules to jboss server
https://tcms.engineering.redhat.com/case/122489/
"""

import os, sys
# user defined packages
import testcase
import common
import OSConf
import rhtest
import openshift

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "Add modules to jboss server"
        self.app_type = common.app_types["jbossas"]
        self.app_name = "jbossmodule"

        self.steps_list = []
        common.env_setup()
    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class AddModulesToJbossServer(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep("Create a jbossas-7 application",
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0,
                expect_description="%s app should be created successfully" %(self.app_name)))

        target_dir1 = "%s/.openshift/config/modules/org/jboss/test/modules/main/" %(self.app_name)
        target_dir2 = "%s/src/main/webapp/WEB-INF/lib" %(self.app_name)
        target_dir3 = "%s/src/main/webapp" %(self.app_name)
        source_file1 = "%s/app_template/jboss_module/TestClass.jar" %(WORK_DIR)
        source_file2 = "%s/app_template/jboss_module/module.xml" %(WORK_DIR)
        source_file3 = "%s/app_template/jboss_module/test.jar" %(WORK_DIR)
        source_file4 = "%s/app_template/jboss_module/modules.jsp" %(WORK_DIR)
        cmd = """mkdir -p %s %s && 
                 cp %s %s %s && 
                 cp %s %s && 
                 cp %s %s""" %(target_dir1, target_dir2, 
                               source_file1, source_file2, target_dir1, 
                               source_file3, target_dir2, 
                               source_file4, target_dir3)
        self.steps_list.append(testcase.TestCaseStep("Add customized jboss module to app",
                cmd,
                expect_return=0,
                expect_description="File and directories are added to your git repo successfully"))

        self.steps_list.append(testcase.TestCaseStep("Do git commit",
                "cd %s && git add . && git commit -m test && git push" %(self.app_name),
                expect_return=0,
                expect_description="File and directories are added to your git repo successfully"))

        def get_app_url(self):
            def closure():
                return OSConf.get_app_url(self.app_name)+"/modules.jsp"
            return closure

        self.steps_list.append(testcase.TestCaseStep("Access jboss module page",
                common.grep_web_page,
                function_parameters = [get_app_url(self), 
                                       "org.jboss.test.modules", "-H 'Pragma: no-cache'", 3, 5],
                expect_return=0,
                expect_description="Access page successfully"))

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
    suite.add_test(AddModulesToJbossServer)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
