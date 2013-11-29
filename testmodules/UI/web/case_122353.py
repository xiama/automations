#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_122353.py
#  Date:      2012/07/24 10:56
#  Author: yujzhang@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class Check_platform(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.go_to_platform()
  
        #Assert all the elements on platform page.
        web.assert_text_equal_by_css('''About the OpenShift Platform as a Service (PaaS)''',
            '''div.ribbon-content''')
        
        web.assert_text_equal_by_xpath('''OpenShift takes care of all the infrastructure, middleware, and management and allows the developer to focus on what they do best: designing and coding applications.''', '''//div[@id='node-11589']/div/p[2]''')
       
        web.assert_text_equal_by_xpath('How do I use OpenShift?', '''//div[@id='node-11589']/div/h2''')
        
        web.assert_text_equal_by_xpath('For a Developer to use OpenShift to take advantage of the power and elasticity of the Cloud, they need only do the following:',
            '''//div[@id='node-11589']/div/p[3]''')
        
        web.assert_text_equal_by_xpath('''Create an "Application" in OpenShift (With the command-line or via their IDE)''',
            '''//div[@id='node-11589']/div/ol/li''')
        
        web.assert_text_equal_by_xpath('Code the application (in Vi, TextMate, Eclipse, Visual Studio, or whatever)',
            '''//div[@id='node-11589']/div/ol/li[2]''')
        
        web.assert_text_equal_by_xpath('''Push the application code to OpenShift (again, with the command-line or from their IDE)''',
            '''//div[@id='node-11589']/div/ol/li[3]''')
        
        web.assert_text_equal_by_xpath('''Here's an example of the command-line approach (in this case the application was already coded and resident in the github repository):''',
            '''//div[@id='node-11589']/div/p[4]''')
        
        web.assert_text_equal_by_xpath('''That's all there is to it. Simple, right?''',
            '''//div[@id='node-11589']/div/p[5]''')
        
        web.assert_text_equal_by_xpath('Read more about getting started',
            '''//div[@id='node-11589']/div/p[6]/a''')
        
        web.assert_text_equal_by_xpath('Code anything',
            '''//div[@id='node-11589']/div/h2[2]''')
        
        web.assert_text_equal_by_xpath('''OpenShift takes a No-Lock-In approach to PaaS by providing built-in support for Node.js, Ruby, Python, PHP, Perl, and Java (the standard in today's Enterprise). In addition, OpenShift is extensible with a customizable cartridge functionality that allows enterprising developers to add any other language they wish. We've seen everything from Clojure to Cobol running on OpenShift.''',
            '''//div[@id='node-11589']/div/p[7]''')
        
        web.assert_text_equal_by_xpath('''In addition to this flexible, no-lock-in, language approach, OpenShift supports many of the popular frameworks that make a developer's life easier including frameworks ranging from Spring, to Rails, to Play. OpenShift is designed to allow Developers to work the way they want to work by giving them the languages, frameworks and tools they need for fast and easy application development.''',
            '''//div[@id='node-11589']/div/p[8]''')
        
        web.assert_text_equal_by_xpath('Blow the doors off your expectations',
            '''//div[@id='node-11589']/div/h2[3]''')
        
        web.assert_text_equal_by_xpath('Once you have your application running in the Cloud, the next thing to worry about is how it is going to handle the massive amount of usage it gets when it goes viral. Well, no worries here. OpenShift has you covered.',
            '''//div[@id='node-11589']/div/p[9]''')
        
        web.assert_text_equal_by_xpath('With Auto-Scaling, OpenShift can scale your application by adding additional instances of your application and enabling clustering. Alternatively, you can manually scale the amount of resources with which your application is deployed when needed. When your big idea takes off, OpenShift will allow it to soar.',
            '''//div[@id='node-11589']/div/p[11]''')
        
        web.assert_text_equal_by_xpath('''Under the Hood''',
            '''//div[@id='node-11589']/div/h2[4]''')
        
        web.assert_text_equal_by_xpath('''OpenShift by Red Hat is built on open-source technologies (we are one of the world's leading open source companies, after all). A decade of enhancements in these technologies contributed by the open source community has resulted in a set of very robust technology components that provide the inner-workings of the OpenShift PaaS.''',
            '''//div[@id='node-11589']/div/p[12]''')
        
        web.assert_text_equal_by_xpath('''OpenShift is built on a foundation of Red Hat Enterprise Linux (RHEL). Beyond being a leading and well respected Linux distro, RHEL provides some key capabilities that allow OpenShift to be stable, responsive, performant and secure. OpenShift leverages the multitenancy and security models within RHEL to provide fine-grained and trusted control over the compute and storage resources available to any single OpenShift application. SELinux allows OpenShift to "firewall" one user's application from another in order to insure security and survivability. Taking a "multi-tenant in the OS" approach vs. a "multi-tenant hypervisor" approach allows OpenShift to scale resources much more quickly so that your application will never lack the horsepower that it needs.''',
            '''//div[@id='node-11589']/div/p[13]''')
        
        web.assert_text_equal_by_xpath('''Add on top of RHEL, a full selection of open source Languages, Frameworks, and Middleware combined with a "Cartridge" approach that allows users to very easily select the components that their applications need whether it is a NoSQL datastore or a Business Intelligence analytics engine.''',
            '''//div[@id='node-11589']/div/p[14]''')
        
        web.assert_text_equal_by_xpath('''Easy-peasy''',
            '''//div[@id='node-11589']/div/h2[5]''')
        
        web.assert_text_equal_by_xpath('''OpenShift is designed to provide one thing for Developers: Ease of Use without Worries. OpenShift's mission is to make your job easier by taking care of all the messy IT aspects of app development and allowing you to focus on your job: Coding your Application and satisfying your customers.''',
            '''//div[@id='node-11589']/div/p[15]''')
        
        web.assert_text_equal_by_xpath('''Pricing''',
            '''//div[@id='node-11589']/div/h2[6]''')
        
        web.assert_text_equal_by_xpath('''A free Developer Preview version of OpenShift has been available for the past year. Based on requests from users for expanded capability, we are planning to expand the OpenShift offering to provide users increased capacity, functionality and support. Check the OpenShift Pricing page for an overview of what we intend to offer when a paid OpenShift service becomes available.''',
            '''//div[@id='node-11589']/div/p[16]''')
        

        #check the links
        #Read more about getting started
        web.go_to_platform()
        web.click_element_by_xpath('''//div[@id='node-11589']/div/section/a/div''')
        time.sleep(2)
        web.check_title("Get Started with OpenShift | OpenShift by Red Hat")
        
        #Read the Getting Started Guide
        web.go_to_platform()
        web.click_element_by_xpath('''//div[@id='node-11589']/div/section/a/div[2]''')
        web.check_title("Get Started with OpenShift | OpenShift by Red Hat")
 
        self.tearDown()

        return self.passed("Case 122353 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Check_platform)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_122353.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
