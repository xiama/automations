#!/usr/bin/python

"""
Attila Nagy
Aug 28, 2012


"""
import rhtest
import common
from hot_deploy_test import HotDeployTest
import fileinput
import re

class Ruby18HotDeployWithoutJenkins(HotDeployTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['ruby']
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "[US2443]Hot deployment support for application - without Jenkins - ruby-1.8"
        
    def configuration(self):
        self.log_info("Creating the application to check PID")
        self.config.file_name = "pid"
        self.info("Editing file '%s'..." % 'config.ru')
        try:
            for line in fileinput.input("./%s/config.ru" % ( self.config.application_name ), inplace = True):
                if re.search(r'map.+health.+do', line):
                    print "map '/pid' do"
                    print "  pidcheck = proc do |env|"
                    print "    [ 200, { 'Content-Type' => 'text/plain'}, [File.open(ENV['OPENSHIFT_HOMEDIR'] + '/%s/run/httpd.pid').readline().chomp()]]" % self.config.application_type
                    print "  end"
                    print "  run pidcheck"
                    print "end"
                    print
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
    suite.add_test(Ruby18HotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
