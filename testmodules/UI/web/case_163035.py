#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_163035.py
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


class Check_Cartridge_List(OpenShiftTest):
    def test_method(self):
        web = self.config.web
        web.login()
  
        #Create duplicate domain
        web.go_to_developer()
        time.sleep(5)
        web.click_element_by_link_text("Platform Features")
        time.sleep(5)
        web.assert_text_equal_by_xpath('''OpenShift Platform Features''', '''//div[@id='content']/div/div/div/div[3]/div/h1/div''') 
        web.assert_text_equal_by_xpath('''OpenShift supports a wide list of application technologies. Each technology is delivered as a cartridge -- a pluggable capability you can add at any time. When you create an application you start with a web platform cartridge and then can add additional capabilities as you choose. Each cartridge runs on one or more gears depending on how high your application has been scaled.''', '''//div[@id='node-10863']/div/p''') 
        web.assert_text_equal_by_xpath('''Web Cartridges''', '''//div[@id='node-10863']/div/h2''')
        web.assert_text_equal_by_xpath('''Web cartridges handle HTTP requests and serve web pages or business APIs. The OpenShift servers route traffic to your application's cartridge, and your code does the rest. If you need a place to store data, adding a database or NoSQL cartridge will automatically configure your web cartridge with the right access.''', '''//div[@id='node-10863']/div/p[2]''')
        web.click_element_by_link_text("JBoss Enterpise Application Platform 6.0")  
        time.sleep(2)
        web.check_title("OpenShift Resources for JBoss | OpenShift by Red Hat")
        web.go_back()
        web.assert_text_equal_by_xpath('''Market-leading open source enterprise platform for next-generation, highly transactional enterprise Java applications. Build and deploy enterprise Java in the cloud.''', '''//div[@id='node-10863']/div/table/tbody/tr/td[2]''')
        web.click_element_by_link_text("JBoss Application Server 7.1")
        web.check_title("OpenShift Resources for JBoss | OpenShift by Red Hat")
        web.go_back() 
        web.assert_text_equal_by_xpath('''PHP 5.3''', '''//div[@id='node-10863']/div/table/tbody/tr[3]/td''') 
        web.assert_text_equal_by_xpath('''PHP is a general-purpose server-side scripting language originally designed for Web development to produce dynamic Web pages. The mod_php Apache module is used to execute PHP applications. Popular development frameworks include: CakePHP, Symfony, and Code Igniter. Popular applications include: Drupal, Wordpress, and Mediawiki.''', '''//div[@id='node-10863']/div/table/tbody/tr[3]/td[2]''')
        web.assert_text_equal_by_xpath('''Python 2.6''', '''//div[@id='node-10863']/div/table/tbody/tr[4]/td''') 
        web.assert_text_equal_by_xpath('''Python is a general-purpose, high-level programming language whose design philosophy emphasizes code readability. The Web Server Gateway Interface (WSGI) defines a simple and universal interface between web servers and web applications or frameworks for the Python programming language. Popular development frameworks include: Django, Bottle, Pylons, Zope and TurboGears.''', '''//div[@id='node-10863']/div/table/tbody/tr[4]/td[2]''')
        web.assert_text_equal_by_xpath('''Perl 5.10''', '''//div[@id='node-10863']/div/table/tbody/tr[5]/td''') 
        web.assert_text_equal_by_xpath('''Perl is a high-level, general-purpose, interpreted, dynamic programming language. mod_perl is an optional module for the Apache HTTP server. It embeds a Perl interpreter into the Apache server, so that dynamic content produced by Perl scripts can be served in response to incoming requests, without the significant overhead of re-launching the Perl interpreter for each request.''', '''//div[@id='node-10863']/div/table/tbody/tr[5]/td[2]''')
        web.assert_text_equal_by_xpath('''Node.js 0.6''', '''//div[@id='node-10863']/div/table/tbody/tr[6]/td''') 
        web.assert_text_equal_by_xpath('''Node.js is a platform built on Chrome's JavaScript runtime for easily building fast, scalable network applications. Node.js uses an event-driven, non-blocking I/O model that makes it lightweight and efficient, perfect for data-intensive real-time applications that run across distributed devices.''', '''//div[@id='node-10863']/div/table/tbody/tr[6]/td[2]''') 
        web.assert_text_equal_by_xpath('''Ruby 1.9.3 and 1.8.7''', '''//div[@id='node-10863']/div/table/tbody/tr[7]/td''')
        web.assert_text_equal_by_xpath('''Ruby is a dynamic, reflective, general-purpose object-oriented programming language. Rack provides a minimal, modular and adaptable interface for developing web applications in Ruby. Popular development frameworks include: Ruby on Rails and Sinatra.''', '''//div[@id='node-10863']/div/table/tbody/tr[7]/td[2]''') 
        web.assert_text_equal_by_xpath('''Do-It-Yourself''', '''//div[@id='node-10863']/div/table/tbody/tr[8]/td''')
        web.assert_text_equal_by_xpath('''The Do-It-Yourself (DIY) application type is a blank slate for trying unsupported languages, frameworks, and middleware on OpenShift. See the community site for examples of bringing your favorite framework to OpenShift.''', '''//div[@id='node-10863']/div/table/tbody/tr[8]/td[2]''')
        web.assert_text_equal_by_xpath('''Databases''', '''//div[@id='node-10863']/div/h2[2]''')
        web.go_back()
        web.assert_text_equal_by_xpath('''MongoDB is a scalable, high-performance, open source NoSQL database.''', '''//div[@id='node-10863']/div/table[2]/tbody/tr/td[2]''')
        web.assert_text_equal_by_xpath('''MySQL Database 5.1''', '''//div[@id='node-10863']/div/table[2]/tbody/tr[2]/td''')
        web.assert_text_equal_by_xpath('''MySQL is a multi-user, multi-threaded SQL database server.''', '''//div[@id='node-10863']/div/table[2]/tbody/tr[2]/td[2]''')
        web.assert_text_equal_by_xpath('''MySQL Database 5.1''', '''//div[@id='node-10863']/div/table[2]/tbody/tr[2]/td''')
        web.assert_text_equal_by_xpath('''PostgreSQL Database 8.4''', '''//div[@id='node-10863']/div/table[2]/tbody/tr[3]/td''')
        web.assert_text_equal_by_xpath('''PostgreSQL is an advanced Object-Relational database management system''', '''//div[@id='node-10863']/div/table[2]/tbody/tr[3]/td[2]''')
        web.assert_text_equal_by_xpath('''Administration''', '''//div[@id='node-10863']/div/h2[3]''')
        web.assert_text_equal_by_xpath('''phpMyAdmin 3.4''', '''//div[@id='node-10863']/div/table[3]/tbody/tr/td''') 
        web.assert_text_equal_by_xpath('''Web based MySQL admin tool. Requires the MySQL cartridge to be installed first.''', '''//div[@id='node-10863']/div/table[3]/tbody/tr/td[2]''') 
        web.assert_text_equal_by_xpath('''RockMongo 1.1''', '''//div[@id='node-10863']/div/table[3]/tbody/tr[2]/td''')
        web.assert_text_equal_by_xpath('''Web based MongoDB administration tool. Requires the MongoDB cartridge to be installed first.''', '''//div[@id='node-10863']/div/table[3]/tbody/tr[2]/td[2]''')
        web.assert_text_equal_by_xpath('''Developer Productivity''', '''//div[@id='node-10863']/div/h2[4]''')
        web.click_element_by_link_text("Jenkins Server")
        web.check_title("Build with Jenkins | OpenShift by Red Hat")
        web.go_back()
        web.assert_text_equal_by_xpath('''Jenkins is a continuous integration (CI) build server that is deeply integrated into OpenShift. When you add Jenkins as an application you will enable your other applications to run complex builds whenever you push code. See the Jenkins info page for more.''', '''//div[@id='node-10863']/div/table[4]/tbody/tr/td[2]''')
        web.click_element_by_link_text("the Jenkins info page for more")
        web.check_title("Build with Jenkins | OpenShift by Red Hat")
        web.go_back()
        web.click_element_by_link_text("Jenkins Client 1.4")
        web.check_title("Build with Jenkins | OpenShift by Red Hat")
        web.go_back()
        web.assert_text_equal_by_xpath('''The Jenkins client connects to your Jenkins application and enables builds and testing of your application. Requires the Jenkins Application to be created via the new application page.''', '''//div[@id='node-10863']/div/table[4]/tbody/tr[2]/td[2]''')
        web.click_element_by_link_text("created via the new application page")
        web.check_title("OpenShift by Red Hat")
        web.go_back()
        web.assert_text_equal_by_xpath('''Cron 1.4''', '''//div[@id='node-10863']/div/table[5]/tbody/tr/td''') 
        web.assert_text_equal_by_xpath('''The Cron cartridge allows you to run command line programs at scheduled times. Use this for background jobs and periodic processing.''', '''//div[@id='node-10863']/div/table[5]/tbody/tr/td[2]''') 
         

        self.tearDown()

        return self.passed("Case 163035 test passed.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Check_Cartridge_List)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_163035.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
