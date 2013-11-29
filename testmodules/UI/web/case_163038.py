#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_163038.py
#  Date:      2012/07/25 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Check_jenkins_page(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Check cartridge page
        web.go_to_developer()
        time.sleep(5)
        web.click_element_by_link_text("Build with Jenkins")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''Build with Jenkins''', '''//div[@id='content']/div/div/div/div[3]/div/h1/div''') 
        web.assert_text_equal_by_xpath('''Jenkins (https://wiki.jenkins-ci.org) is a full featured continuous integration (CI) server that can run builds, tests, and other scheduled tasks and integrate with your OpenShift applications.''', '''//div[@id='node-10295']/div/p''') 
        web.click_element_by_link_text("https://wiki.jenkins-ci.org")  
        time.sleep(2)
        web.check_title("Home - Jenkins - Jenkins Wiki")
        web.go_back()
        web.assert_text_equal_by_xpath('''With Jenkins, you have access to a full library of plugins (https://wiki.jenkins-ci.org/display/JENKINS/Plugins) and a vibrant, thriving community of users who have discovered a new way to do development. The basic work flow is:''', '''//div[@id='node-10295']/div/p[2]''')
        web.click_element_by_link_text("https://wiki.jenkins-ci.org/display/JENKINS/Plugins")
        web.check_title("Plugins - Jenkins - Jenkins Wiki")
        web.go_back() 
        web.assert_text_equal_by_xpath('''Commit and push new code to your repo.''', '''//div[@id='node-10295']/div/ol/li''') 
        web.assert_text_equal_by_xpath('''Jenkins waits for this commit, runs a full series of tests (customized by the developer)''', '''//div[@id='node-10295']/div/ol/li[2]''')
        web.assert_text_equal_by_xpath('''With OpenShift, if the tests and build are successful, the new code gets deployed. If it fails, the old code continues to run with no downtime related to the push.''', '''//div[@id='node-10295']/div/ol/li[3]''') 
        web.assert_text_equal_by_xpath('''Users can review the persistent build history maintained by Jenkins''', '''//div[@id='node-10295']/div/ol/li[4]''')
        web.assert_text_equal_by_xpath('''How can you get started? First, make sure you are running the latest rhc tools (gem update rhc or yum update rhc). Then follow these steps:''', '''//div[@id='node-10295']/div/p[4]''') 
        web.assert_text_equal_by_xpath('''Step 1 - Create Jenkins''', '''//div[@id='node-10295']/div/h3''')
        web.assert_text_equal_by_xpath('''$ rhc app create -a jenkins -t jenkins-1.4''', '''//div[@id='node-10295']/div/pre/code''') 
        web.assert_text_equal_by_xpath('''Note the administrator username and password that is created and returned from rhc. This will be needed to administer Jenkins.''', '''//div[@id='node-10295']/div/p[5]''') 
        web.assert_text_equal_by_xpath('''Step 2 - Create an Application with Embedded Jenkins''', '''//div[@id='node-10295']/div/h3[2]''')
        web.assert_text_equal_by_xpath('''For a new application:''', '''//div[@id='node-10295']/div/p[6]''')
        web.assert_text_equal_by_xpath('''$ rhc app create -a jboss1 -t jbossas-7 --enable-jenkins''', '''//div[@id='node-10295']/div/pre[2]/code''') 
        web.assert_text_equal_by_xpath('''For an existing application:''', '''//div[@id='node-10295']/div/p[7]''')
        web.assert_text_equal_by_xpath('''$ rhc app cartridge add -a jboss1 -c jenkins-client-1.4''', '''//div[@id='node-10295']/div/pre[3]/code''') 
        web.assert_text_equal_by_xpath('''This will create a Jenkins Job specifically configured for the application including parameters such as the builder size, DNS resolution timeout, and the application's git repo URL. These parameters and more can be managed via the Jenkins web UI.''', '''//div[@id='node-10295']/div/p[8]''')
        web.assert_text_equal_by_xpath('''Step 3 - Modify and Push your Application''', '''//div[@id='node-10295']/div/h3[3]''')
        web.assert_text_equal_by_xpath('''$ git push''', '''//div[@id='node-10295']/div/pre[4]/code''')
        web.assert_text_equal_by_xpath('''This will trigger the build/test/deploy sequence in Jenkins.''', '''//div[@id='node-10295']/div/p[9]''')
        web.assert_text_equal_by_xpath('''When a build is triggered, Jenkins first needs to schedule the build. The scheduling process involves creating a temporary builder for the application. On the Jenkins side, a Node (aka Slave) is created. In OpenShift, a corresponding builder Application is created named appnamebldr. If the Node/builder already exists at scheduling then the existing builder will be used and the build will immediately fire. NOTE: This Node and builder Application will consume one Gear. Nodes and builder Applications are automatically deleted and the corresponding Gear is freed after 15 idle minutes.''', '''//div[@id='node-10295']/div/p[10]''')
        web.assert_text_equal_by_xpath('''To troubleshoot errors that occur during the build/test/deploy phase with Jenkins, from a git push, etc. there are three logs that will indicate the problem in most cases.''', '''//div[@id='node-10295']/div/p[11]''')
        web.assert_text_equal_by_xpath('''Logging for Application level errors (e.g. compilation failures, test failures) is available via the Jenkins web UI under the corresponding Node's build history.''', '''//div[@id='node-10295']/div/p[12]''')
        web.assert_text_equal_by_xpath('''Logging for Jenkins level errors (e.g. DNS timeouts, builder configuration) is available in the Jenkins logs at:''', '''//div[@id='node-10295']/div/p[13]''')
        web.assert_text_equal_by_xpath('''$ rhc app tail -a jenkins''', '''//div[@id='node-10295']/div/pre[5]/code''')
        web.assert_text_equal_by_xpath('''$ rhc app tail -a jboss1''', '''//div[@id='node-10295']/div/pre[6]/code''')
        web.click_element_by_link_text("Subscribe To This Thread")
        web.check_title("Confirm your subscription | OpenShift by Red Hat")
        web.go_back() 
        web.click_element_by_link_text("Subscribe To: Posts Of Type Page")
        web.check_title("Confirm your subscription | OpenShift by Red Hat")
        web.go_back()
        web.click_element_by_link_text("Subscribe To Ccoleman@redhat.com")
        web.check_title("Confirm your subscription | OpenShift by Red Hat")
      
        self.tearDown()

        return self.passed("Case 163038 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Check_jenkins_page)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_163038.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
