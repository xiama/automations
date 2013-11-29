#!/usr/bin/python

"""
Attila Nagy
Nov 13, 2012
"""

import rhtest
import common
import fileinput
import re
from hot_deploy_test import HotDeployTest

class NodeJSHotDeployWithoutJenkins(HotDeployTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['nodejs']
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "[US2747][RT]Hot deployment support for application - without Jenkins - nodejs-0.6"
        
    def configuration(self):
        self.log_info("Modifying the application to check PID")
        self.config.file_name = "pid.js"
        self.info("Editing file '%s'..." % 'server.js')
        try:
            for line in fileinput.input("./%s/server.js" % ( self.config.application_name ), inplace = True):
                print line,
                if re.search(r'// Routes for /health, /asciimo and /', line):
                    print 
                    print "        self.routes['/pid.js'] = function(req, res) {"
                    #print "\t\t\tres.send(fs.readFileSync(process.env.OPENSHIFT_HOMEDIR + '/%s/run/node.pid').toString());" % self.config.application_type
                    print "            res.send(fs.readFileSync(process.env.OPENSHIFT_HOMEDIR + '/nodejs/run/node.pid').toString());"
                    print "        };"
                    print
        except Exception as e:
            fileinput.close()
            print type(e)
            print e.args
            self.fail("Configuration of the test-application must be successful")
        finally:
            fileinput.close()
        self.deploy()
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NodeJSHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
