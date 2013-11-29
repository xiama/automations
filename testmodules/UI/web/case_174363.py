#!/usr/bin/env python
# coding=utf-8
#
#  File name: case_174360.py
#  Date:      2012/07/17 11:23
#  Author: mgao@redhat.com   
#

import rhtest
import time

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        pass

    def finalize(self):
        pass


class CreateAppWithoutSSHKey(OpenShiftTest):
    def test_method(self):
        web = self.config.web

        web.login()
        #web.delete_app("ruby19")
        #create a ruby1.9 app
        web.create_app("ruby-1.9","ruby19")

        #check wether the links are correct
        time.sleep(5)
       
        #ADD ssh key
        web.input_by_id("key_raw_content", '''ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA2AcMMWvrfpIcoHMM/SQbpdlqa8TVb5Y1lJcHovJxHzTHXb18KW7MJ2dvQZdcxfAaGboG1hq5HfUhN/mnubv0QJLsFcVKkpd5Pmi/jnM1NBN5qRo+ZvXR0lU1qssYp0fsCn8K7s6lQALApuAFb+U0vW+3o2i2cJ659TouPRnJhuOHdWmdj5cLDPQRoVh+2RhXOuXcFqryJtyruymC4r92RkikTtHhchBtv2Xsdzn8zwUIWLg3k/CcXuOIHTxw3kAMe5j2qYJ+OLJ/4L9THhA0Zg0szdTYh1k076bIXdVJOiBgUZu+tXRCy2aSn1k0rnp8graLxXx2hicD5tidmIhsBQ== root@mgao''')
        web.driver.find_element_by_id("key_submit").click()
        time.sleep(2)
        web.assert_text_equal_by_xpath("Install the Git client for your operating system, and from your command line run",'''//div[@id='content']/div/div/div/div[2]/div/section[2]/div/div/p[6]''') 


        #delete ssh key
        web.go_to_account()
        web.click_element_by_xpath('''//tr[@id='default_sshkey']/td[3]/a''')
        time.sleep(2)
        
        
         
        #delete a python app
        web.delete_app("ruby19")


        self.tearDown()

        return self.passed(" case_174360--CreateAppWithoutSSHKey passed successfully.")


    def tearDown(self):
        self.config.web.driver.quit()
        self.assert_equal([], self.config.web.verificationErrors)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(CreateAppWithoutSSHKey)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of case_174360.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
