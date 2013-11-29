#!/usr/bin/python

#
#  File name: nodejs_mysql.py
#  Date:      2012/03/02 11:59
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import testcase, common, OSConf
import rhtest

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US590][runtime][rhc-cartridge]Embed MySQL instance to nodejs application"
        self.app_name = 'nodejs1'
        self.app_type = 'nodejs'
        self.tcms_testcase_id = 137748
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class NodejsMysqlSupport(OpenShiftTest):
    def test_method(self):

        self.steps_list.append(testcase.TestCaseStep("Create a Node.js",
                common.create_app,
                function_parameters=[self.app_name, common.app_types[self.app_type], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True],
                expect_return=0))

        self.steps_list.append(testcase.TestCaseStep("Embed with MySQL" ,
                common.embed,
                function_parameters = [self.app_name, 'add-%s'%common.cartridge_types['mysql'],self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_return=0))

        def upload_server(app_name):
            mysql = OSConf.get_apps()[app_name]['embed'][common.cartridge_types['mysql']]
            try:
                f = open('%s/server.js'%app_name,'w')
                f.write('''#!/bin/env node
//  OpenShift sample Node application

var express = require('express');
var fs      = require('fs');
var mysql   = require('mysql');
var client = mysql.createClient({
    user:'%s',
    password :'%s'
});
client.host ='%s';
client.port = %s;
client.database = '%s';

//  Local cache for static content [fixed and loaded at startup]
var zcache = { 'index.html': '' };
zcache['index.html'] = fs.readFileSync('./index.html'); //  Cache index.html

// Create "express" server.
var app  = express.createServer();


/*  =====================================================================  */
/*  Setup route handlers.  */
/*  =====================================================================  */

// Handler for GET /health
app.get('/health', function(req, res){
    res.send('1');
});

// Handler for GET /asciimo
app.get('/asciimo', function(req, res){
    var link="https://a248.e.akamai.net/assets.github.com/img/d84f00f173afcf3bc81b4fad855e39838b23d8ff/687474703a2f2f696d6775722e636f6d2f6b6d626a422e706e67";
    res.send("<html><body><img src='" + link + "'></body></html>");
});

// Handler for GET /
app.get('/', function(req, res){
    res.send(zcache['index.html'], {'Content-Type': 'text/html'});
});
// Handler for GET /data1.js
app.get('/data1.js', function(req, res){
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id INT PRIMARY KEY, data VARCHAR(20))");
    client.query("INSERT INTO info VALUES(1, '#OPENSHIFT_1#')");
    //client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /data2.js
app.get('/data2.js', function(req, res){
    client.query("DROP TABLE IF EXISTS info");
    client.query("CREATE TABLE info(id INT PRIMARY KEY, data VARCHAR(20))");
    client.query("INSERT INTO info VALUES(1, '#OPENSHIFT_2#')");
    //client.end();
    res.send('Please visit /show.js to see the data', {'Content-Type': 'text/plain'});
});
// Handler for GET /show.js
app.get('/show.js', function(req, res){
    client.query(
        'SELECT data FROM info',
        function selectCb(err, results, fields) {
            if (err) {
                res.send('Failed to get data from database', {'Content-Type': 'text/plain'});
                throw err;
            }
            else {
                res.send(results[0]['data'], {'Content-Type': 'text/plain'});
            }
        }
    );
    //client.end();
});


//  Get the environment variables we need.
var ipaddr  = process.env.OPENSHIFT_INTERNAL_IP;
var port    = process.env.OPENSHIFT_INTERNAL_PORT || 8080;

if (typeof ipaddr === "undefined") {
   console.warn('No OPENSHIFT_INTERNAL_IP environment variable');
}

//  terminator === the termination handler.
function terminator(sig) {
   if (typeof sig === "string") {
      console.log('%%s: Received %%s - terminating Node server ...',
                  Date(Date.now()), sig);
      process.exit(1);
   }
   console.log('%%s: Node server stopped.', Date(Date.now()) );
}

//  Process on exit and signals.
process.on('exit', function() { terminator(); });

['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGILL', 'SIGTRAP', 'SIGABRT', 'SIGBUS',
 'SIGFPE', 'SIGUSR1', 'SIGSEGV', 'SIGUSR2', 'SIGPIPE', 'SIGTERM'
].forEach(function(element, index, array) {
    process.on(element, function() { terminator(element); });
});

//  And start the app on that interface (and port).
app.listen(port, ipaddr, function() {
   console.log('%%s: Node server started on %%s:%%d ...', Date(Date.now() ), ipaddr, port);
});'''%(mysql['username'], mysql['password'], mysql['url'], mysql['port'], mysql['database']))

                f.close()
                command = '''cd %s && 
                            chmod +x server.js &&
                            git add server.js &&
                            git commit -m "Added server.js" -a &&
                            git push'''%app_name

                (status, output) = common.command_getstatusoutput(command)

            except Exception as e:
                self.info("ERROR: %s"%str(e))
                return 255

            return status

        self.steps_list.append(testcase.TestCaseStep("Add server.js file" ,
                upload_server,
                function_parameters = [self.app_name],
                expect_return=0))

        def verify(app_name):
            url = OSConf.get_app_url(app_name)
            r = common.grep_web_page("%s/data1.js"%url, 'Please visit /show.js to see the data')
            r += common.grep_web_page("%s/show.js"%url, 'OPENSHIFT_1')
            r += common.grep_web_page("%s/data2.js"%url, 'Please visit /show.js to see the data')
            r += common.grep_web_page("%s/show.js"%url, 'OPENSHIFT_2')
            return r

        self.steps_list.append(testcase.TestCaseStep("Verify it the web output" ,
                verify,
                function_parameters = [self.app_name],
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
    suite.add_test(NodejsMysqlSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of nodejs_mysql.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
