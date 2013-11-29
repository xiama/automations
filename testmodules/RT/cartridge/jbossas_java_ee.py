#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Aug 2, 2012
"""
import rhtest
import common
import OSConf
import os
import pycurl
from shutil import rmtree
from time import sleep

class JBossJavaEETest(rhtest.Test):

    def initialize(self):
        self.application_name = common.getRandomString()
        self.git_repo = './%s' % self.application_name
        self.summary = '[US2296][Runtime][rhc-cartridge] EE6 application with JNDI, remote EJBs, and JMS [P1]'
        common.env_setup()

    def finalize(self):
        rmtree(self.git_repo)
    
    def test_method(self):
        self.info('=' * 80)
        self.info('Creating the application')
        self.info('=' * 80)
        ret = common.create_app(
            self.application_name,
            common.app_types['jbossas'],
            self.config.OPENSHIFT_user_email,
            self.config.OPENSHIFT_user_passwd
        )
        self.assert_equal(ret, 0, "Failed to create app")

        self.info('=' * 80)
        self.info('Deploying the application')
        self.info('=' * 80)
        deployment_steps = [
            'cp -v %s %s' % ( os.path.dirname(__file__) + '/app_template/sfsbTest-1.0.war', self.git_repo + '/deployments' ),
            'cd %s' % self.git_repo,
            'git add .',
            'git commit -a -m "Adding testing app"',
            'git push'
        ]
        common.command_get_status(' && '.join(deployment_steps))
        self.info('Waiting for the application...')
        sleep(60)

        self.info('=' * 80)
        self.info('Invoking testing servlet')
        self.info('=' * 80)
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, 'http://' + OSConf.get_app_url(self.application_name) + '/sfsbTest-1.0/SfsbServlet')
        curl.setopt(pycurl.VERBOSE, 1)
        curl.perform()
        self.info('Asserting that the return code is 200')
        self.assert_equal(curl.getinfo(pycurl.HTTP_CODE), 200)

        self.info('=' * 80)
        self.info('Verifying server.log')
        self.info('=' * 80)
        ( ret_code, ret_output ) = common.run_remote_cmd(self.application_name, 'cat %s/logs/server.log' % self.application_name)
        pattern_list = [
            'java:module/EntityTesterBean',
            'java:module/StatelessBean1!org.jboss.jndiTest.StatelessBean1Local',
            'Received new cluster view',
            'MBeans were successfully registered to the platform mbean server',
            'Started repl cache from ejb container',
            'Added a new EJB receiver in cluster context ejb for node',
            'Stateless called',
            'JMS message sent',
        ]
        missing_pattern =  [ ]
        for pattern in pattern_list:
            result = 'OK'
            if ret_output.find(pattern) == -1:
                missing_pattern.append(pattern)
                result = 'FAIL'
            self.info("Looking for pattern '%s'... %s" % ( pattern, result ))
        self.info('Asserting that all the patterns are found...')
        self.assert_equal(len(missing_pattern), 0)
 
        # Everything is OK
        return self.passed(self.summary)
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JBossJavaEETest)
    #### user can add multiple sub tests here.
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
