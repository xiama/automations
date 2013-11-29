"""
Linqing Lu
lilu@redhat.com
Dec 23, 2011

"""

import os, sys

import testcase
import common
import rhtest

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.mypath = os.path.abspath(__file__)
        self.mydir = os.path.dirname(__file__)
        self.summary="[integration][rhc-selinux]SELinux separation - illegal operations"
        common.env_setup()
        self.app_name = 'python'
        self.app_type = common.app_types[self.app_name]

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))
        

class SelinuxIllegalOperations(OpenShiftTest):
    def test_method(self):
        #"Create an %s app: %s" % (self.app_type, self.app_name),
        ret = common.create_app(self.app_name, self.app_type)
        self.assert_equal(ret, 0, "App should be created successfully")

        #"Copy template files",
        ret = common.command_get_status("cp -f %s/data/illegal_app_content/* %s/wsgi/" % (self.mydir, self.app_name))
        self.assert_equal(ret, 0)

        #"Git push codes",
        ret = common.command_get_status("cd %s/wsgi/ && git add . && git commit -am 'update app' && git push" % self.app_name)
        self.assert_equal(ret, 0)

        #"Get app URL",
        app_url = common.get_app_url_from_user_info(self.app_name)

        #"Check feedback",
        ret = common.grep_web_page(app_url, 'RETURN VALUE:0')
        self.assert_equal(ret, 1) #the string shouldn't be there

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SelinuxIllegalOperations)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
