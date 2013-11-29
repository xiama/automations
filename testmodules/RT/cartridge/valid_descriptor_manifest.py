#!/usr/bin/python

#
#  File name: valid_descriptor_manifest.py
#  Date:      2012/02/24 04:21
#  Author:    mzimen@redhat.com
#

import sys
import os
import testcase
import common
import commands
import rhtest

class OpenShiftTest(rhtest.Test):
    ITEST = "DEV"
    INTERACTIVE = False

    def initialize(self):
        self.summary ="[rhc-cartridge][US-1664] Valid cartridge descriptor mainfest.yaml"
        self.tcms_testcase_id = 128860
        self.steps_list = []

        common.env_setup()

    def finalize(self):
        pass

class ValidDescriptorManifest(OpenShiftTest):

    def test_method(self):
        (status, output) = common.run_remote_cmd_as_root('rpm -qa | grep ^openshift-origin-cartridge- | grep -v abstract')
        if status!=0:
            self.error('Unable get the list of cartridges...')
            return self.failed("%s failed" % self.__class__.__name__)

        cartridges = output.splitlines()
        for cart in cartridges:
            rpm = RPMPackage(cart)
            #print 'Cartridge RPM: ' + cart
            #print " Manifest.yml exists? ",
            self.steps_list.append(testcase.TestCaseStep("Valid descriptors for %s"%cart, 
                        rpm.existManifestFile,
                        function_parameters=[], 
                        expect_return=True))


        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

class RPMPackage:

    def __init__(self, package):
        self.package = package
        self.manifestfile = None

    def getFileList(self):
        #return commands.getoutput('rpm -ql ' + self.package).splitlines()
        (status, output) = common.run_remote_cmd_as_root('rpm -ql ' + self.package)
        return output.splitlines()

    def getManifestFilePath(self):
        return self.manifestfile

    def existManifestFile(self):
        filelist = self.getFileList()
        existManifestFile = False
        for file in filelist:
            if file.endswith('manifest.yml'):
                existManifestFile = True
                self.manifestfile = file
                break
        return existManifestFile


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ValidDescriptorManifest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of valid_descriptor_manifest.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
