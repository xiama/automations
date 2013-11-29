#!/usr/bin/python

"""
Attila Nagy
Sept 26, 2012


"""
import rhtest
import common
from hot_deploy_test import HotDeployTest

class PHPHotDeployWithoutJenkins(HotDeployTest):
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['php']
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "[US2309] Hot deployment support for non-scaling PHP app - without Jenkins"
        
    def configuration(self):
        self.log_info("Creating the application to check PID")
        self.config.file_name = "pid.php"
        self.info("Editing file '%s'..." % self.config.file_name)
        php_file = open("./%s/php/%s" % (self.config.application_name, self.config.file_name), "w")
        php_file.write("<?php\n")
        php_file.write("header('Content-type: text/plain');")
        php_file.write("echo getmypid();")
        php_file.write("?>")
        php_file.close()
        self.deploy()
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PHPHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
