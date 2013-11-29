#!/usr/bin/env python
import os, sys

import common
import rhtest
import glob
import openshift
import shutil
import helper

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        etc_dir = common.get_etc_dir()
        common.env_setup()
        self.domain_name = common.getRandomString(10)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.key_files = "%s/libra_key/id_rsa*" %(etc_dir)
        if self.get_run_mode() == "OnPremise":
            self.pem_file = "%s/onpremise/onpremise.pem" %(etc_dir)
        else:
            self.pem_file = "%s/libra.pem" %(etc_dir)
        self.max_gears = common.DEV_MAX_GEARS

        cf = self.config
        self.rest = cf.rest_api

    def finalize(self):
        pass


class SetupSSH(OpenShiftTest):
    def test_method(self):
        if not os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
            # only copy the pre-configured id_rsa if one does not exist
            self.info("Copy already prepared libra ssh key file")
            try:
                shutil.os.makedirs(os.path.expanduser("~/.ssh/"))
            except:
                pass
            for filename in glob.glob(self.key_files):
                shutil.copy(filename, os.path.expanduser("~/.ssh/"))
                os.chmod(os.path.join(os.path.expanduser("~/.ssh/"), filename),
                         0400)
            
            #common.prepare_libra_sshkey()
            #common.clean_up(user_email, user_passwd)
        if not os.path.exists(os.path.join(os.path.expanduser("~/.ssh/"),
                                           os.path.basename(self.pem_file))):
            shutil.copy(self.pem_file, os.path.expanduser("~/.ssh/"))
        self.info("Change permission of %s to 600" %(self.pem_file))
        os.chmod(self.pem_file, 0600)

        #helper.setup_ssh_config()

        self.info("Remove ssh known hosts in case host key changes")
        path = os.path.expanduser("~/.ssh/known_hosts")
        if os.path.exists(path):
            os.remove(path)
        
        self.info("Remove 'default' ssh key for user")
        self.rest.key_delete('default')

        self.info("Add ssh key")
        status, resp = self.rest.key_add({})
        import json
        jresp = json.loads(resp)
        status = jresp['status']
        print status
        self.assert_equal(status, 'created', "Failed to add/update ssh key for user")
        
        '''
        self.info("Update 'default' ssh key for user")
        status, resp = self.rest.key_update({})
        '''

        return self.passed("%s passed" % self.__class__.__name__)


class SetupEnv(OpenShiftTest):
    def test_method(self):
        if self.get_run_mode() == 'DEV' or self.get_run_mode() == 'OnPremise':
            self.info("Set max gears to %s" % (self.max_gears))
            ret = common.set_max_gears(self.user_email, self.max_gears)
            self.assert_equal(ret, 0, "Failed to set max gears")

            #if common.is_multinode_env():
            #    common.setup_multi_node_env()
        return self.passed("%s passed" % self.__class__.__name__)


class CreateDomain(OpenShiftTest):
    def test_method(self):

        self.info("Create/Alter domain for express user")

        try:
            status, res = self.rest.domain_get()
        except openshift.OpenShiftNullDomainException:
            status, res = self.rest.domain_create(self.domain_name)
            self.assert_equal(status, 201, "Domain should be created/altered successfully")
        #else:
        #we don't need to update domain! (it's enough if exists)
        #    #altering
        #    status, ret = self.rest.domain_update(self.domain_name)


        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SetupSSH)
    suite.add_test(SetupEnv)
    suite.add_test(CreateDomain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
