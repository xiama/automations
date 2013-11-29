"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US617] jboss cart pom.xml improvement
https://tcms.engineering.redhat.com/case/122455/
"""
import os,sys
import rhtest
import testcase
import common
import OSConf

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US617] jboss cart pom.xml improvement"
        self.app_name = "jbosspom"
        self.app_type = common.app_types["jbossas"]
        self.git_repo = "./%s" % (self.app_name)

        common.env_setup()
    
        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class JbossImprovedPomXml(OpenShiftTest):
    def test_method(self):
        # 1.Create an app
        self.steps_list.append(testcase.TestCaseStep(
                "1. Create an jbossas app: %s" % (self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0))

        # 2.Check pom.xml file - groupId
        cmd = "cd %s && cat pom.xml|grep groupId|grep %s" % (self.git_repo, self.app_name)
        self.steps_list.append( testcase.TestCaseStep("2.Check pom.xml file - groupId",
                cmd,
                expect_description="'%s' should be found in the groupId of pom.xml" % (self.app_name),
                expect_return=0))

        # 3.Check pom.xml file - artifactId
        cmd = "cd %s && cat pom.xml|grep artifactId|grep %s" % (self.git_repo, self.app_name)
        self.steps_list.append( testcase.TestCaseStep("3.Check pom.xml file - artifactId",
                cmd,
                expect_description="'%s' should be found in the artifactId of pom.xml" % (self.app_name),
                expect_return=0))

        # 4.Check pom.xml file - name
        cmd = "cd %s && cat pom.xml|grep name|grep %s" % (self.git_repo, self.app_name)
        self.steps_list.append( testcase.TestCaseStep("4.Check pom.xml file - name",
                cmd,
                expect_description="'%s' should be found in the name of pom.xml" % (self.app_name),
                expect_return=0))

        # 5.Check pom.xml file - warName
        cmd = "cd %s && cat pom.xml|grep warName|grep ROOT" % (self.git_repo)
        self.steps_list.append( testcase.TestCaseStep("5.Check pom.xml file - warName",
                cmd,
                expect_description="'ROOT' should be found in the warName of pom.xml",
                expect_return=0))

        # 6.Check pom.xml file - outputdirectory
        cmd = "cd %s && cat pom.xml|grep outputDirectory|grep deployments" % (self.git_repo)
        self.steps_list.append( testcase.TestCaseStep(
                "6.Check pom.xml file - outputdirectory",
                cmd,
                expect_description="'deployments' should be found in the outputDirectory of pom.xml",
                expect_return=0))

        # 7.Check pom.xml file - project.build.sourceEncoding
        cmd = "cd %s && cat pom.xml|grep project.build.sourceEncoding|grep UTF-8" % (self.git_repo)
        self.steps_list.append( testcase.TestCaseStep(
                "7.Check pom.xml file - project.build.sourceEncoding",
                cmd,
                expect_description="'UTF-8' should be found in the project.build.sourceEncoding of pom.xml",
                expect_return=0))

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
    suite.add_test(JbossImprovedPomXml)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
