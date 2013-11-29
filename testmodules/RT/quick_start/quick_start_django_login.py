#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
import OSConf
import re
import pycurl
import os
from time import sleep
from StringIO import StringIO
import urllib

# user defined packages
from quick_start_django import QuickStartDjango

class QuickStartDjangoLogin(QuickStartDjango):
    
    def __init__(self, config):
        QuickStartDjango.__init__(self, config)
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: django - Logging into admin interface"
        self.config.cookie_file = "/tmp/%s.txt" % common.getRandomString(30)

    def finalize(self):
        QuickStartDjango.finalize(self)
        if os.path.exists(self.config.cookie_file):
            os.remove(self.config.cookie_file)
        

    def deployment_steps(self):
        # Deploying
        ( ret_code, ret_output ) = QuickStartDjango.deployment_steps(self)
        
        # Looking for the admin password
        admin_password = ""
        match = re.search(r'Django application credentials.*\n.*\nremote:[^\w]*([\w]*).*\n', ret_output, re.MULTILINE)
        if match:
            admin_password = match.group(1).strip()

        self.assert_true(admin_password != "")
        self.config.admin_password = admin_password

        self.info("Admin password found: " + self.config.admin_password)

    def verification(self):
        self.log_info("Verifying")
        sleep(10) # Waiting 10 minutes for the application

        # Fetching the form to get CSRF cookie
        admin_page = "http://" + OSConf.get_app_url(self.config.application_name) + "/admin/"
        b = StringIO()
        self.info("Fetching admin form...")
        self.info("Admin page URL: " + admin_page)
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, admin_page)
        curl.setopt(pycurl.VERBOSE, 1)
        curl.setopt(pycurl.COOKIEJAR, self.config.cookie_file)
        curl.setopt(pycurl.WRITEFUNCTION, b.write)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.perform()

        match = re.search(r"name='csrfmiddlewaretoken' value='(.+)'", b.getvalue())
        csrf_cookie = ""
        if match:
           csrf_cookie = match.group(1) 
        self.info("CSRF Cookie: " + csrf_cookie)
        
        # Logging in    
        admin_page_html = StringIO()
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.WRITEFUNCTION, admin_page_html.write)
        post_data = urllib.urlencode(
            {
                'username' : 'admin' ,
                'password' : self.config.admin_password,
                'this_is_the_login_form' : 1,
                'next' : '/admin/',
                'csrfmiddlewaretoken' : csrf_cookie
            }
        )
        curl.setopt(pycurl.POSTFIELDS, post_data)
        curl.perform()

        admin_page_html_source = admin_page_html.getvalue()
        self.info("="*30)
        self.info(admin_page_html_source)
        self.info("="*30)

        self.assert_true(admin_page_html_source.find("Site administration") != -1)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartDjangoLogin)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
