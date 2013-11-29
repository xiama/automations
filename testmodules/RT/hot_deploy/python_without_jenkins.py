#!/usr/bin/python

"""
Attila Nagy
Oct 24, 2012
"""

import rhtest
import common
import fileinput
import re
from hot_deploy_test import HotDeployTest

class PythonHotDeployWithoutJenkins(HotDeployTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['python']
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "[US2747][RT]Hot deployment support for application - without Jenkins - python-2.6"
        
    def configuration(self):
        self.log_info("Creating the application to check PID")
        self.config.file_name = "pid"
        self.info("Editing file '%s'..." % 'wsgi/application')
        try:
            for line in fileinput.input("./%s/wsgi/application" % ( self.config.application_name ), inplace = True):
                if re.search(r'elif environ.+PATH_INFO.+/env.+:', line):
                    print "    elif environ['PATH_INFO'] == '/pid':"
                    print "        response_body = str(os.getppid())"
                print line,
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
    suite.add_test(PythonHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
