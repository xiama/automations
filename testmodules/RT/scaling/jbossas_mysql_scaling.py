#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

import testcase, common, OSConf
import rhtest

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = 'jboss' + common.getRandomString()
        try:
            self.app_type = common.app_types[self.get_variant()]
        except:
            self.app_type = common.app_types["jbossas"]

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        pass


class  JbossasMysqlScaling(OpenShiftTest):
    def check_mysql_result(self):
        app_url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page("http://%s/mysql_scalable.jsp" % app_url, "Tim Bunce, Advanced Perl DBI", "-H 'Pragma: no-cache'", delay=10, count=12)

    def prepare_jsp_file(self):
        try:
            fr = open("%s/cartridge/app_template/mysql/mysql_scalable.jsp"%(WORK_DIR + "/../"), "r")
        except Exception as e:
            print str(e)
            return False
        jsp = fr.read()
        fr.close()
        try:
            fw = open("%s/src/main/webapp/mysql_scalable.jsp" %self.app_name, "w")
            fw.write(jsp)
            fw.close()
        except Exception as e:
            self.error(str(e))
            return False

        try:
            fw = open("%s/pom.xml"%self.app_name, "w")
            self.info("Generate a pom.xml file")
            fw.write("""<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>%s</groupId>
  <artifactId>%s</artifactId>
  <packaging>war</packaging>
  <version>1.0</version>
  <name>%s</name>
  <licenses>
      <license>
          <name>Apache License, Version 2.0</name>
          <url>http://www.apache.org/licenses/LICENSE-2.0.html</url>
      </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.jboss.spec</groupId>
      <artifactId>jboss-javaee-6.0</artifactId>
      <version>1.0.0.Final</version>
      <type>pom</type>
      <scope>provided</scope>
    </dependency>
    <dependency>
        <groupId>mysql</groupId>
        <artifactId>mysql-connector-java</artifactId>
        <version>5.1.20</version>
    </dependency>
  </dependencies>
  <profiles>
    <profile>
     <!-- When built in OpenShift the 'openshift' profile will be used when invoking mvn. -->
     <!-- Use this profile for any OpenShift specific customization your app will need. -->
     <!-- By default that is to put the resulting archive into the 'deployments' folder. -->
     <!-- http://maven.apache.org/guides/mini/guide-building-for-different-environments.html -->
     <id>openshift</id>
     <build>
        <finalName>%s</finalName>
        <plugins>
          <plugin>
            <artifactId>maven-war-plugin</artifactId>
            <version>2.1.1</version>
            <configuration>
              <outputDirectory>deployments</outputDirectory>
              <warName>ROOT</warName>
            </configuration>
          </plugin>
        </plugins>
      </build>
    </profile>
  </profiles>
</project>""" % (self.app_name, self.app_name, self.app_name, self.app_name))
            fw.close()
        except Exception as e:
            self.error(str(e))
            return False

        return True

    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Create a scalable %s app: %s" % (self.app_type, self.app_name),
            common.create_scalable_app,
            function_parameters = [self.app_name, self.app_type, self.user_email, self.user_passwd, True, "./" + self.app_name],
            expect_description = "App should be created successfully",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "embed mysql to %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "add-" + common.cartridge_types["mysql"], self.user_email, self.user_passwd ],
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Prepare template files",
            self.prepare_jsp_file,
            expect_return = True))

#    step = testcase.TestCaseStep(
#            "update config file",
#            "sed -i '/MysqlDS\"/ {s/false/true/}' %s/.openshift/config/standalone.xml" % (self.app_name),
#            expect_return = 0)
#    steps.append(step)

        self.steps_list.append(testcase.TestCaseStep(
            "git push codes",
            "cd %s && git add . && git commit -am 'update app' && git push" % self.app_name,
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result",
            self.check_mysql_result,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-up the application via Rest API",
            common.scale_up,
            function_parameters = [self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result - again",
            self.check_mysql_result,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Scale-donw the application via Rest API",
            common.scale_down,
            function_parameters = [self.app_name,],
            expect_description = "Operation must be successfull",
            expect_return = 0,
            try_interval=5,
            try_count=6))

        self.steps_list.append(testcase.TestCaseStep(
            "Check MySql Result - again",
            self.check_mysql_result,
            expect_description = "MySQL operation must be successfull",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "Remove mysql from %s" % self.app_name,
            common.embed,
            function_parameters = [ self.app_name, "remove-" + common.cartridge_types["mysql"] ],
            expect_description = "Operation must be successfull",
            expect_return = 0))

        case = testcase.TestCase("[US2099][US2307][RT][rhc-cartridge]Embed mysql to scalable apps: jbossas, jbosseap", self.steps_list)
        case.run()

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JbossasMysqlScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
