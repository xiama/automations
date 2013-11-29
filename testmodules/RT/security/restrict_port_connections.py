#
#  File name: restrict_port_connections.py
#  Date:      2012/02/29 05:36
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re


import rhtest
import testcase
import common
import OSConf

class ObserverGenerator(object):
    @classmethod
    def get_application(self):
        return '''
#!/usr/bin/python
import os

virtenv = os.environ['APPDIR'] + '/virtenv/'
os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.6/site-packages')
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass
#
# IMPORTANT: Put any additional includes below this line.  If placed above this
# line, it's possible required libraries won't be in your searchable path
# 
import urllib2
import socket
import json

contests=[ "127.0.250.1", "127.0.250.129", "127.0.251.1",
           "127.0.251.129", "127.0.252.1" ]
binders=[ "127.0.250.2", "127.0.250.130", "127.0.251.2",
           "127.0.251.130", "127.0.252.2" ]
cmirror=[ "169.254.250.1", "169.254.250.129", "169.254.251.1",
           "169.254.251.129", "169.254.252.1" ]
bmirror=[ "169.254.250.2", "169.254.250.130", "169.254.251.2",
           "169.254.251.130", "169.254.252.2" ]

def application(environ, start_response):

    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value) for key, value in sorted(environ.items())]
        response_body = '\\n'.join(response_body)

    elif environ['PATH_INFO'] == '/open':
        ctype = 'application/json'
        body = dict()
        try:
            #callurl = "http://" + contests[int(environ['QUERY_STRING'])-1] + ":8080/health"
            callurl = "http://" + environ['QUERY_STRING'] + ":8080/health"
            body['callurl'] = callurl
            body['reason'] = "OK: %s"%(urllib2.urlopen(callurl).read())
            body['return'] = 0
        except urllib2.URLError, e:
            body['return'] = 113
            body['reason'] = "URL Error: %s" % str(e)
            response_body = json.dumps(body)
        except urllib2.HTTPError, e:
            response_body = '{"return" : 1, "reason" : "HTTP Error: %s"}' % str(e)
        except Exception, e:
            body['return'] = 1
            body['reason'] = "Other Error: %s" % str(e)

        response_body = json.dumps(body)
            
    elif environ['PATH_INFO'] == "/bind":
        try:
            sockhop = (binders[int(environ['QUERY_STRING'])-1], 8080)
            socksrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socksrv.bind(sockhop)
            socksrv.close()
            response_body = "Successfully Opened %s:%d" % sockhop
        except Exception, e:
            response_body = "Exception: %s\\n\\n" % str(e)
            
    elif environ['PATH_INFO'] == '/mopen':
        try:
            callurl = "http://" + cmirror[int(environ['QUERY_STRING'])-1] + ":8080/health"
            response_body = urllib2.urlopen(callurl).read()
            response_body += "\\n\\n"
        except urllib2.URLError, e:
            response_body = "URL Error: %s\\n\\n" % str(e)
        except urllib2.HTTPError, e:
            response_body = "HTTP Error: %s\\n\\n" % str(e)
        except Exception, e:
            response_body = "Other Error: %s\\n\\n" % str(e)
            
    elif environ['PATH_INFO'] == "/mbind":
        try:
            sockhop = (bmirror[int(environ['QUERY_STRING'])-1], 8080)
            socksrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socksrv.bind(sockhop)
            socksrv.close()
            response_body = "Successfully Opened %s:%d" % sockhop
        except Exception, e:
            response_body = "Exception: %s\\n\\n" % str(e)

    elif environ['PATH_INFO'] == "/mbopen":
        try:
            sockhop = (bmirror[int(environ['QUERY_STRING'])-1], 8080)
            socksrv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socksrv.connect(sockhop)
            socksrv.close()
            response_body = "Successfully Opened %s:%d" % sockhop
        except Exception, e:
            response_body = "Exception: %s\\n\\n" % str(e)

    else:
        ctype = 'text/html'
        ctype = 'application/json'
        response_body = '{ "return" : "200"}'
    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
    start_response(status, response_headers)
    return [response_body]

#
# Below for testing only
#
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()'''


class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US1656][Runtime][Security] Restrict port connections"
        self.app_name = 'portcon'
        self.app_type = 'python'
        try:
            self.app_type2 = self.config.test_variant
        except:
            self.app_type2 = 'php'
        tcms_testcase_id = 129219
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name, self.app_name2))

class RestrictPortConnections(OpenShiftTest):
    def test_method(self):
        self.info("1. Create an observer app") 
        ret = common.create_app(self.app_name, 
                                common.app_types[self.app_type], 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd, 
                                True)
        self.assert_equal(ret,0, "App should be created")


        self.info("2. Modify the observer %s"%self.app_name)
        ret = common.command_get_status('''
                                  cd %s &&
                                  cat <<EOF >wsgi/application &&
%s
EOF
                                  git commit -m "Changed APP" -a && git push
                                  '''%(self.app_name, ObserverGenerator.get_application()))
        self.assert_equal(ret,0, "App should be created")

        for app_t in ('php', 'python', 'perl', 'rack'):
            self.app_name2 = "%s%s"%(self.app_name,app_t)

            self.info("3x. Create target App %s"%self.app_name2) 
            ret = common.create_app(self.app_name2,
                                    common.app_types[app_t], 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd,
                                    False)
            self.assert_equal(ret,0, "Second application should be deployed.")

            self.info("4x. Verify http connection to %s"%self.app_name2)
            self.verify(self.app_name, self.app_name2, [('return',113)])
            self.assert_equal(ret,0, "It should not be allowed to connect from %s->%s"%(self.app_name, self.app_name2))

            self.info("5x. Delete it") 
            ret = common.destroy_app(self.app_name2, 
                                    self.config.OPENSHIFT_user_email, 
                                    self.config.OPENSHIFT_user_passwd)
            self.assert_equal(ret,0, "App should be destroyed")

            self.info("6x. Verify self") 
            self.verify(self.app_name, self.app_name, [('return',0)])
            self.assert_equal(ret,0, "App should be verified")


        return self.passed("%s passed" % self.__class__.__name__)

    def get_internal_ip_address(self, app_name):
        (status, output) = common.run_remote_cmd(app_name,'echo IP=$OPENSHIFT_INTERNAL_IP')
        obj = re.search(r"IP=(\d+\.\d+\.\d+\.\d+)",output)
        if obj:
            #print "DEBUG: OPENSHIFT_INTERNAL_IP=%s"%obj.group(1)
            return obj.group(1)
        print "ERROR: Unable to get internal IP"
        return None

    def verify(self, app_name, target_app_name, conditions):
        url = OSConf.get_app_url(app_name)
        tocheck_url = self.get_internal_ip_address(target_app_name)
        return common.check_json_web_page("%s/open?%s"%(url, tocheck_url), conditions)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RestrictPortConnections)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of restrict_port_connections.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
