#!/usr/bin/python

"""
Attila Nagy
Jul 26, 2012


"""
import rhtest
import common
from hot_deploy_test import HotDeployTest

class JBossHotDeployWithoutJenkins(HotDeployTest):
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['jbossas']
        self.config.application_type_no_version = "jbossas"
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "JBoss AS Hot Deployment Test without Jenkins"       
        #self.config.pid_file = '/app-root/runtime/jbossas.pid'
        #if self.config.application_type = "jbossas-7":
        #    self.config.pid_file = '/app-root/runtime/jbossas.pid'
        #elif self.config.application_type in ["jbossews-1.0", "jbossews-2.0"]:
        #    self.config.pid_file = '/jbossews/run/jboss.pid'
        #elif self.config.application_type = "jbosseap-6":
        #    self.config.pid_file = '/app-root/runtime/jbosseap.pid'
 
    def configuration(self):
        self.log_info("Creating the application to check PID")
        self.config.file_name = "pid.jsp"
        if self.config.application_type == "jbossas-7":
            self.config.pid_file = '/app-root/runtime/jbossas.pid'
        elif self.config.application_type in ["jbossews-1.0", "jbossews-2.0"]:
            self.config.pid_file = '/jbossews/run/jboss.pid'
        elif self.config.application_type == "jbosseap-6":
            self.config.pid_file = '/app-root/runtime/jbosseap.pid'
        self.info("Editing file '%s'..." % self.config.file_name)
        jsp_file = open("./%s/src/main/webapp/%s" % (self.config.application_name, self.config.file_name), "w")
        jsp_file.write('<%@ page contentType="text/plain" %>\n')
        jsp_file.write('<%@ page trimDirectiveWhitespaces="true" %>\n')
        jsp_file.write('<%@ page import="java.io.FileReader" %>\n')
        jsp_file.write('<%@ page import="java.io.BufferedReader" %>\n')
        jsp_file.write('<%\n')
        jsp_file.write('String pid_file_name = System.getenv("OPENSHIFT_HOMEDIR") + "%s";\n' % self.config.pid_file)
        jsp_file.write('BufferedReader fileStream = new BufferedReader(new FileReader(pid_file_name));\n')
        jsp_file.write('String line = null;\n')
        jsp_file.write('while ( (line = fileStream.readLine()) !=null ) {\n')
        jsp_file.write('out.print(line);\n')
        jsp_file.write('}\n')
        jsp_file.write('%>\n')
        jsp_file.close()
        self.deploy()
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
