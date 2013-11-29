#
#  File name: public_tcp_proxy.py
#  Date:      2012/02/14 01:32
#  Author:    mzimen@redhat.com
#

import sys
import os
import re

import rhtest
import testcase, common, OSConf

HOST=None
PORT=None

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1371][Runtime][Horizontal Scaling] Public TCP proxy solution"
        self.app_name1 = 'ctrapp1'
        self.app_name2 = 'ctrapp2'
        self.app_type = 'php'
        tcms_testcase_id = 130875
        self.steps = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name1, self.app_name2))

class PublicTcpProxy(OpenShiftTest):
    def test_method(self):
        self.steps.append(testcase.TestCaseStep(
                "Deploy app1", 
                common.create_app,
                function_parameters = [self.app_name1, 
                                       common.app_types[self.app_type], 
                                       self.config.OPENSHIFT_user_email, 
                                       self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep(
                "Deploy app2",
                common.create_app,
                function_parameters = [self.app_name2, 
                                       common.app_types[self.app_type], 
                                       self.config.OPENSHIFT_user_email, 
                                       self.config.OPENSHIFT_user_passwd, True],
                expect_return = 0))

        
        self.steps.append(testcase.TestCaseStep(
                "Call Expose hook the public ports",
                self.expose_port,
                function_parameters = [self.app_name1],
                expect_return = 0))

        self.steps.append(testcase.TestCaseStep(
                "Modify the app2 to comunicate (as client)" , 
                self.add_client,
                function_parameters = [self.app_name2],
                expect_return=0))

        self.steps.append(testcase.TestCaseStep("Check the communication.",
                self.verify_proxy,
                function_parameters = [self.app_name2],
                expect_return=0,
                expect_description="It should return a response from CtrApp1"))

        case = testcase.TestCase(self.summary, self.steps)
        case.run()
        common.destroy_app(self.app_name1, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        common.destroy_app(self.app_name2, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        os.system("rm -Rf %s" % self.app_name1)
        os.system("rm -Rf %s" % self.app_name2)
 
        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def verify_proxy(self, app_name):
        url = OSConf.get_app_url(app_name)
        return common.grep_web_page("%s/client.php"%url, 'Welcome to OpenShift')
        
    def add_client(self, app_name):
        cmd = '''
cd %s &&
cat <<'EOF' >php/client.php &&
<?php
    error_reporting(E_ALL);
    print "Hello from client.php<hr/>";
    $port = %s;
    $host = "%s";
    $url = "$host:$port";
    print "$url";
    $error_FH = fopen("error.log","w") or die("Unable to open stderr log file.");
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_HEADER, 1);
    curl_setopt($ch, CURLOPT_STDERR, $error_FH);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_VERBOSE, 1);
    print "<pre>";
    print curl_exec($ch);
    print "</pre>";
    curl_close($ch);
    print "<hr/>client.php done.";
?> 
EOF
    git add php/client.php &&
    git commit -a -m "Added client.php" &&
    git push
    '''%(app_name, PORT, HOST),
        (status, output) = common.command_getstatusoutput(cmd)
        return status

    def expose_port(self, app_name):
        global HOST
        global PORT
        uuid = OSConf.get_app_uuid(app_name)
        cmd = '/usr/libexec/openshift/cartridges/%s/info/hooks/expose-port %s %s %s ' % (common.app_types[self.app_type], app_name, common.get_domain_name(), uuid)
        (status, output) = common.run_remote_cmd(None, cmd, as_root=True)

        if status != 0:
            return status

        obj = re.search(r".*PROXY_HOST=(.*)", output, re.MULTILINE)
        if obj:
            host=obj.group(1)
            obj = re.search(r".*PROXY_PORT=(\d+)", output, re.MULTILINE)
            if obj:
                HOST= host
                PORT = obj.group(1)
            else:
                print "ERROR: Unable to catpure PROXY_PORT"
                return -1
        else:
            print "ERROR: Unable to catpure PROXY_HOST"
            return -1

        return status
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PublicTcpProxy)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of public_tcp_proxy.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
