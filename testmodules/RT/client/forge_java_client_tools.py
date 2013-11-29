#!/usr/bin/python

#
#  File name: forge_java_client_tools.py
#  Date:      2012/02/27 08:56
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import rhtest
import testcase, common, OSConf, pexpect

#TODO: get the version from TCMS arguments

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary= "[US1413][UI] Change SeamForge plugin to use the official Java client tools"
        self.app_name = 'forgeapp'
        tcms_testcase_id = 121961

        try:
            #TODO: this could be received from framework
            self.forge_version = os.environ["forge_version"]
        except:
            self.forge_version = '1.0.0.Final'
            #forge_version = '1.0.0.Beta3'

        common.env_setup()

        forge_dir = "%s/forge/"%os.getcwd()
        os.environ['FORGE_HOME'] = forge_dir
        os.environ['PATH'] += ":%s/bin"%forge_dir

    def finalize(self):
        os.system("rm -rf forge-*; rm -rf forge; rm -rf %s"%self.app_name )

class ForgeJavaClientTools(OpenShiftTest):
    def test_method(self):
        steps = []
        steps.append(testcase.TestCaseStep("Check Java/Expect/Maven3 version" ,
                "java -version 2>&1|grep OpenJDK && javac -version 2>&1 | grep 1.6 && expect -version && mvn -version |grep 'Apache Maven 3' && echo PASS",
                expect_string_list = ["PASS"],
                expect_description = "Javac/Expect/Maven3 should be installed",
                expect_return=0))

        steps.append(testcase.TestCaseStep("Check if domain exists",
                "rhc domain show -l %s -p '%s' %s"%(self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                unexpect_string_list=["A user with rhlogin '%s' does not have a registered domain."%self.config.OPENSHIFT_user_email],
                expect_return=0))

        steps.append(testcase.TestCaseStep("Install JbossForge",
                '''
                rm -rf $HOME/.m2 &&
                rm -rf $HOME/.forge &&
                wget 'https://repository.jboss.org/nexus/service/local/artifact/maven/redirect?r=releases&g=org.jboss.forge&a=forge-distribution&v=%s&e=zip' -O forge-package.zip  &&
                unzip forge-package.zip &&
                rm -f forge-package.zip &&
                ln -s forge-* forge 
                '''%(self.forge_version),
                expect_return=0,
                expect_description="JbossForge Installation should pass"))

        steps.append(testcase.TestCaseStep("Run basic jboss tools commands commands", 
                    self.check_jboss_forge,
                    expect_return = 0,
                    expect_description = "All of the JBossForge commands should pass"))

        steps.append(testcase.TestCaseStep("Destroy that application", 
                    common.destroy_app,
                    function_parameters = [self.app_name, 
                                           self.config.OPENSHIFT_user_email, 
                                           self.config.OPENSHIFT_user_passwd],
                    expect_description = "The application should not exist",
                    expect_return=1))

        case = testcase.TestCase(self.summary, steps)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def check_jboss_forge(self):
        expect_file = 'forge.expect'
        f = open(expect_file, 'w')

        f.write('''#!/usr/bin/expect --
#it seems that colors in shell makes problems with matching
#so, what you see is not what is in the buffer

set app_name %s
set username %s
set password %s

set send_slow {10 .001}
set send_human {.1 .3 1 .05 2}
proc dprint {msg} {
    send_user "\\nDEBUG: $msg\\n"
}

proc abort {msg} {
    send "exit\\n"
    send_user "ABORT() $msg\\n"
    exit 254
}

spawn forge/bin/forge

expect {
    -timeout 180
    "no project*\$*" { dprint "OK: found initial prompt" }
    timeout { abort "timeout: No initial prompt."}
}
#
# forge list-plugins
#
send "forge list-plugins\\n"
expect {
    -timeout 20
    "no project*\$*" { dprint "OK: forge list-plugins"}
    timeout { abort "Unable to execute forge list-plugins command" }
}

#
# new -project
#
send "new-project --named forge-openshift-demo --topLevelPackage org.jboss.forge.openshift\\n"
expect {
    "Use*as project directory*" { send "Y\\n" }
}
expect {
    -timeout 30 
    "SUCCESS*" { dprint "OK: new-project" }
    timeout {abort "timeout: new-project ..."}
}
expect {
    -timeout 60  
    "forge-openshift-demo*forge-openshift-demo*\$*" { dprint "OK: CLI" }
    timeout {abort "timeout: no prompt after new-project"}
}
expect *  ;#clean the buffer
#
# forge install plugin
#
send "forge install-plugin openshift-express\\n"
expect {
    -timeout 900
    "BUILD SUCCESS*\\n" { dprint "OK: BUILD SUCCESS" }
    timeout {abort "timeout: BUILD SUCCESS"}
}
expect {
    -timeout 20 
    "SUCCESS*Installed from" { dprint "OK: Installed from"}
    timeout { abort "timeout: Installed from" }
}
expect {
    -timeout 20 
    "forge-openshift-demo*forge-openshift-demo*\$*" { dprint "OK: Installation done."}
    timeout { abort "timeout: End of installation" }
}
expect *  ;#clean the buffer
send "\\n"
send "\\n"
expect {
    "forge-openshift-demo*forge-openshift-demo*\$*"
}
sleep 5
#
# rhc-expect setup
#
send -s "rhc-express setup --app $app_name \\n"
expect {
    "Enter your Red Hat Login" {send -s "$username\\n"}
}
sleep 5
expect {
    "Enter your Red Hat Login password" {send -s "$password\\n"}
}
sleep 5
expect {
    -timeout 180 
    "Initialized empty*" { dprint "OK: password sent"}
    "ERROR*" { abort "Something wrong with password" }
    "Caused by: *" { abort "Something wrong with password" }
    #timeout { abort "timeout:Waiting for password prompt"}
}
expect {
    -timeout 3000 
    "SUCCESS*Installed*successfully" { dprint "OK: Installation of $app_name - success" }
    "Caused by: *" { abort "Some Exception ?" }
    timeout { abort "timeout:Waiting for successful setup is never ending..."}
}

expect *  ;#clean the buffer

#
# servlet setup
#
send -s "servlet setup\\n"
expect {
    -timeout 20
    "Facet*requires packaging*" { send "Y\\n" }
    timeout { abort "???" } 
}
expect {
    -timeout 60
    "SUCCESS*Installed*successfully" { dprint "OK: Installed successfully" }
    timeout { abort "???" } 
}
expect {
    -timeout 60
    "SUCCESS*Servlet is installed" { dprint "OK: Servlet is installed" }
    timeout { abort "Unable to install servlet" } 
}
expect {
    -timeout 60
    "SUCCESS*Servlet is installed\n"
    timeout { abort "Unable to install servlet support." } 
}
#
# git add ...
#
send -s "git add pom.xml src/\\n"
expect {
    -timeout 90
    "forge-openshift-demo*forge-openshift-demo*\$*" {dprint "Git add "}
    timeout {abort "??" }
}
send -s "rhc-express deploy\\n"
expect {
    -timeout 90
    "remote: Starting application" {dprint "Starting application"}
    timeout { abort "No CLI after rhc-express deploy" }
}

#
# rhc-express status
#
send -s "rhc-express status\\n"
expect {
    -timeout 60
    "Enter your Red Hat Login*" {send -s "$username\\n"}
    timeout {abort "No Red Hat Login prompt" }
}
sleep 5
expect {
    "Enter the application name" {send -s "$app_name\\n"}
}
sleep 5
expect {
    "Enter your Red Hat Login password" {send -s "$password\\n"}
    timeout { abort "No password prompt"}
}
sleep 5
expect {
    -timeout 280 
    "forge-openshift-demo*forge-openshift-demo*\$*" {dprint "OK"}
}
expect * ; #clean the buffer
#
# rhc-express list
#
send -s "rhc-express list\\n"
expect {
    -timeout 60
    "Enter your Red Hat Login*" {send -s "$username\\n"}
    timeout {abort "No Red Hat Login prompt" }
}
sleep 5
expect {
    "Enter your Red Hat Login password" {send -s "$password\\n"}
    timeout { abort "No password prompt"}
}
expect {
    -timeout 30
    "Applications on OpenShift Express" {dprint "List - OK"}
    timeout { abort "No password prompt"}
}
expect *;
sleep 5
#
#  rhc-express destroy
#
send -s "rhc-express destroy\\n"
expect {
    -timeout 60
    "Enter your Red Hat Login*" {send -s "$username\\n"}
    timeout {abort "No Red Hat Login prompt" }
}
sleep 5
expect {
    "Enter the application name" {send -s "$app_name\\n"}
}
sleep 5
expect {
    "Enter your Red Hat Login password" {send -s "$password\\n"}
    timeout { abort "No password prompt"}
}
sleep 5
expect {
    -timeout 30
    "About to destroy application" { send -s "Y\\n" }
    timeout { abort "No destroy prompt"}
}
expect {
    -timeout 90
    "Destroyed application $app_name on" { dprint "Deleted." }
    timeout { abort "Unable to destroy application" }
}

send -s "exit\\n"
close
exit 0 '''%(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd))
        f.close()
        (status, output) = common.command_getstatusoutput("chmod +x %s;./%s"%(expect_file,expect_file))
        return status


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ForgeJavaClientTools)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of forge_java_client_tools.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
