#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Jun 27, 2012
[US2307][RT][rhc-cartridge]Auto scaling test
"""
import common, testcase, OSConf
import rhtest
import subprocess, commands
import re
import os
import time
from helper import get_instance_ip
PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


code_dict = {   "jbosseap"  :   r"""<%@ page session="false" %>
<%@ page contentType="text/html" language="java" %>
<%@ page import="javax.naming.*" %>
<%@ page import="java.io.*"  %>
<%@ page import="java.util.*"  %>
<%@ page import="java.text.*"  %>
<%
Map map = System.getenv();
out.print("App DNS " + map.get("OPENSHIFT_GEAR_DNS"));
%>
""",
                "php"   :   r"""<html>
<body>
<?php
    echo "App DNS ".$_ENV["OPENSHIFT_GEAR_DNS"]."<br />";
?>
</body>
</html>""",
                "perl"  :   r"""#!/usr/bin/perl
print "Content-type: text/html\r\n\r\n";
print "App DNS ".$ENV{"OPENSHIFT_GEAR_DNS"};""",
                "ruby"  :   r"""require "thread-dump"
map "/health" do
  health = proc do |env|
    [200, { "Content-Type" => "text/html" }, ["1"]]
  end
  run health
end
map "/" do
  welcome = proc do |env|
    [200, { "Content-Type" => "text/plain" }, ["App DNS " + ENV["OPENSHIFT_GEAR_DNS"]]]
  end
  run welcome
end""",
                "python"    :   r"""#!/usr/bin/python
import os
virtenv = os.environ["APPDIR"] + "/virtenv/"
os.environ["PYTHON_EGG_CACHE"] = os.path.join(virtenv, "lib/python2.6/site-packages")
virtualenv = os.path.join(virtenv, "bin/activate_this.py")
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
def application(environ, start_response):
    ctype = "text/plain"
    if environ["PATH_INFO"] == "/health":
        response_body = "1"
    else:
        response_body = "App DNS " + os.environ["OPENSHIFT_GEAR_DNS"]

    status = "200 OK"
    response_headers = [("Content-Type", ctype), ("Content-Length", str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]""",
                "python-2.7"    :   r"""#!/usr/bin/env python
import os

def application(environ, start_response):
    ctype = "text/plain"
    if environ["PATH_INFO"] == "/health":
        response_body = "1"
    else:
        response_body = "App DNS " + os.environ["OPENSHIFT_GEAR_DNS"]

    status = "200 OK"
    response_headers = [("Content-Type", ctype), ("Content-Length", str(len(response_body)))]
    start_response(status, response_headers)
    return [response_body]""",
                "nodejs"    :   r"""#!/bin/env node
var express = require("express");
var app  = express.createServer();
app.get("/health", function(req, res){
    res.send("1");
});
app.get("/", function(req, res){
    res.send("App DNS " + process.env.OPENSHIFT_GEAR_DNS, {"Content-Type": "text/plain"});
});
var ipaddr  = process.env.OPENSHIFT_NODEJS_IP;
var port    = process.env.OPENSHIFT_NODEJS_PORT || 8080;
if (typeof ipaddr === "undefined") {
   console.warn("No OPENSHIFT_INTERNAL_IP environment variable");
}
function terminator(sig) {
   if (typeof sig === "string") {
      console.log("%s: Received %s - terminating Node server ...",
                  Date(Date.now()), sig);
      process.exit(1);
   }
   console.log("%s: Node server stopped.", Date(Date.now()) );
}
process.on("exit", function() { terminator(); });
["SIGHUP", "SIGINT", "SIGQUIT", "SIGILL", "SIGTRAP", "SIGABRT", "SIGBUS",
 "SIGFPE", "SIGUSR1", "SIGSEGV", "SIGUSR2", "SIGPIPE", "SIGTERM"
].forEach(function(element, index, array) {
    process.on(element, function() { terminator(element); });
});
app.listen(port, ipaddr, function() {
   console.log("%s: Node server started on %s:%d ...", Date(Date.now() ),
               ipaddr, port);
});
""",
    }
code_dict["jbossas"] = code_dict["jbosseap"]
code_dict["ruby-1.9"] = code_dict["ruby"]
code_dict["python-3.3"] = code_dict["python-2.7"]

class OpenShiftTest(rhtest.Test):
    ITEST = ['DEV', 'INT', 'STG']

    def initialize(self):
        #check the presence of /usr/bin/ab command
        if not os.path.exists("/usr/bin/ab"):
            raise rhtest.TestIncompleteError("Missing /usr/bin/ab file: (No httpd-tools package?))")
        self.steps_list = []
        self.summary = "[US2307][RT][rhc-cartridge]Auto scaling test"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.test_variant = "python-3.3"
        self.domain_name = common.get_domain_name()
        self.app_name = self.test_variant.split('-')[0] + "auto"
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = self.app_name
        self.proc = None
        # Support for Node.js-0.10 cart
        if self.test_variant == "nodejs-0.10":
            self.test_variant = "nodejs"
        common.env_setup()

    def finalize(self):
        if self.proc.poll() == None:
            self.proc.kill()


class AutoScalingTest(OpenShiftTest):

    def trigger_autoscale(self):
        url = OSConf.get_app_url(self.app_name)
        if self.config.options.run_mode == 'DEV':
            self.proc = subprocess.Popen(["/usr/bin/ab", "-c 200", "-t 60", "https://" + url + "/"])
        else:
            self.proc = subprocess.Popen(["/usr/bin/ab", "-c 70", "-t 60", "https://" + url + "/"])

    def remove_dup(self, lst):
        if lst == []:
            return []
        lst.sort()
        result = []
        result.append(lst[0])
        for i in range(len(lst) - 1):
            if lst[i] != lst[i+1]:
                result.append(lst[i+1])
        return result
                
    def confirm_autoscale(self):
        url = OSConf.get_app_url(self.app_name)
        # check if all gears are available
        gear_lst = []
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        for i in range(20):
            (ret, output) = common.command_getstatusoutput(cmd, quiet=True)
            if ret != 0:
                time.sleep(3)
            else:
                pattern = re.compile(r'(?<=App DNS ).+com', re.M)
                match = pattern.search(output)
                if match == None:
                    time.sleep(3)
                elif match.group(0) not in gear_lst:
                    gear_lst.append(match.group(0))
        self.debug("Gears found: " + ' '.join(gear_lst))
        if len(gear_lst) >= 2:
            return 0
        else:
            return 2

    def test_method(self):
        instance_ip = get_instance_ip()
        if self.config.options.run_mode == 'DEV':
			instance_ip = 'dev.rhcloud.com' 
        global code_dict
        # 1. Create app
        self.steps_list.append(testcase.TestCaseStep("Create an %s app: %s" % (self.test_variant, self.app_name),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", True, "small", -1, False],
                expect_description="the app should be created successfully",
                expect_return=0))
        # 2. Write some code to show the gear DNS
        file_path = {   "jbosseap"  :   "%s/src/main/webapp/index.jsp" % (self.git_repo),
                        "jbossas"   :   "%s/src/main/webapp/index.jsp" % (self.git_repo),
                        "php"       :   "%s/php/index.php" % (self.git_repo),
                        "perl"      :   "%s/perl/index.pl" % (self.git_repo),
                        "python"    :   "%s/wsgi/application" % (self.git_repo),
                        "python-2.7"    :   "%s/wsgi/application" % (self.git_repo),
                        "python-3.3"    :   "%s/wsgi/application" % (self.git_repo),
                        "ruby"      :   "%s/config.ru" % (self.git_repo),
                        "nodejs"    :   "%s/server.js" % (self.git_repo),
        }
        cmd = "rm -f %s/src/main/webapp/index.html ; echo '%s' > '%s'" % (self.git_repo, code_dict[self.test_variant], file_path[self.test_variant])
        #cmd = "rm -f %s; echo '%s' > '%s'" % (file_path[self.test_variant], code_dict[self.test_variant], file_path[self.test_variant])
        if self.test_variant in ("jbossas", "jbosseap"):
            cmd += """; sed -i '/<system-properties>/ a\\\n<property name="org.apache.catalina.session.StandardManager.MAX_ACTIVE_SESSIONS" value="-1"/>' %s/.openshift/config/standalone.xml""" % (self.git_repo)
        self.steps_list.append(testcase.TestCaseStep("Write some code to show the gear DNS",
                cmd,
                expect_description="the code should be written successfully",
                expect_return=0))
        # 3. Git push all the changes
        self.steps_list.append(testcase.TestCaseStep("Git push all the changes",
                "cd %s && git add . && git commit -amt && git push && sleep 30" % (self.git_repo),
                expect_description="the changes should be git push successfully",
                expect_return=0))
        # 4. Confirm the app is available
        self.steps_list.append(testcase.TestCaseStep("Confirm the app is available",
                common.grep_web_page,
                function_parameters=[OSConf.get_app_url_X(self.app_name), "App DNS", "-H 'Pragma: no-cache' -L", 5, 30],
                expect_description="the app should be avaiable",
                expect_return=0))
        # 5. Establish multiple parallel connections to the app to trigger auto-scaling
        self.steps_list.append(testcase.TestCaseStep("Establish multiple parallel connections to the app to trigger auto-scaling",
                self.trigger_autoscale,
                expect_description="auto-scaling should be triggered",
                ))
        # 6. Confirm auto-scaling is triggered
        self.steps_list.append(testcase.TestCaseStep("Confirm auto-scaling is triggered",
                self.confirm_autoscale,
                expect_description="auto-scaling should be triggered",
                try_count=60,
                try_interval=10,
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
    suite.add_test(AutoScalingTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
