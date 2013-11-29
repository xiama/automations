#!/usr/bin/python

"""
Attila Nagy
anagy@redhat.com

Nov 28, 2012
"""

import rhtest
import common
import os
from shutil import rmtree
from time import sleep
from jbossews_java7 import EWSJava7Test

class EWSScalingJava7Test(EWSJava7Test):

    def __init__(self, config):
        EWSJava7Test.__init__(self, config)
        self.config.scalable = True
        self.config.summary = "[US2513] Java 7 with scaling JbossEWS application"
    
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(EWSScalingJava7Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

