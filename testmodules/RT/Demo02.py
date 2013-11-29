#!/usr/bin/env python

#
#  File name: Demo02.py
#  Date:      2012/05/11 14:50
#  Author:    mzimen@redhat.com
#

import sys
import subprocess
import os
import string
import re

import common, OSConf
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_name = 'CtrApp1'
        self.app_type = 'php'

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%self.app_name) 

class Demode02(OpenShiftTest):

    def create_app(self, *args, **kwargs): 
        if kwargs.has_key("some_argument"):
            print "Possible argument received: ", kwargs['some_argument']
        if kwargs.has_key("app_name"):
            print "Another argument received: ", kwargs['app_name']
            self.app_name=kwargs['app_name']

        return common.create_app(self.app_name, 
                          common.app_types[self.app_type], 
                          self.config.OPENSHIFT_user_email, 
                          self.config.OPENSHIFT_user_passwd, True)

    def embed_app(self, *args, **kwargs):
        if len(args)>0:
            cartridge=args[0]
        else:
            cartridge = 'mysql'

        return common.embed(self.app_name, 
                            "add-%s"%common.cartridge_types[cartridge], 
                            self.config.OPENSHIFT_user_email, 
                            self.config.OPENSHIFT_user_passwd)

    def add_file(self, *args, **kwargs):
        if len(args)>0:
            filename=args[0]
        else:
            filename= "testing.php"
        f = open("%s/%s"%(self.app_name, filename), "wb")
        f.write("""
<?php
phpinfo();

?>

""")
    def grep_app(self, *args, **kwargs):
        last_output = self.get_output_from_last_step()
        print "DEBUG: previous output:", last_output
        url=OSConf.get_app_url(self.app_name)
        if len(args)>0:
            find_str = args[0]
        else:
            find_str = 'OpenShift'
        return common.grep_web_page(url, find_str)
    

    def test_method(self):

        step1 = self.add_step("Create an app",
                      self.create_app,
                      function_parameters = {"some_argument": "i_dont_know"},   # also as dict() ...
                      expect_str = [            #case sensitive for re.match()
                        "Now your new domain name is being propagated worldwide",   
                        "creation returned success"],
                      expect_return=0)

        step2_embed = self.add_step("Embed it",
                      self.embed_app,
                      expect_return=0,
                      unexpect_istr = "This shouln't be there",   #case insesitive for re.match()
                      expect_description="Embed should work...")

        step3 = self.add_step("Add file",
                      self.add_file,
                      function_parameters=["filename.php"])  #default args for self.add_file

        step4 =self.add_step("Check the app via web", 
                      self.grep_app,
                      expect_return=0,
                      try_count=3,
                      try_interval=4)

        step5 = self.add_step("Git commit new file",
                      "cd %s && touch X && git add X && git commit -a -m 'xx' && git push"%self.app_name,
                      expect_description="The output of push should contain something...",
                      expect_str=["remote: "],
                      expect_return=0)

        step6 = self.add_step("Local command with arguments:", 
                "nslookup %s",
                function_parameters="www.redhat.com", #can be even string 
                expect_str = ["192.168.122.1"],
                try_count=2,
                expect_return=0)


        step1(some_argument="argument")

        step2_embed()         #use default parameters
        step2_embed("cron")   #this step doesn't require checking results, 

        (ret, output) = step3("This_is_the_file_I_want.php")
        if (ret == 0):
            self.info("Everything is ok, let's continue with step4")
            obj = re.search(r"remote:(.*)", output)
            if (obj):
                step4(obj.group(1))
            else:
                return self.failed("Unable to parse important output.")
        else:
            self.info("Despite this problem, let's do something else... git...")
            step5()

        step6()                 #nslookup with default arguments
        for url in ["www.google.com", "www.yahoo.com"]:
            step6(url)

        return self.passed()

        # or you can run this if you are satisfied with only sequence
        #return self.run_steps()


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Demode02)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of Demo02.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
