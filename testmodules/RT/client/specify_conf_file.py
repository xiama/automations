#!/usr/bin/env python
import os, sys

import common, OSConf
import rhtest


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.domain_name = common.get_domain_name()
        self.test_rhlogin = "testrhlogin@redhat.com"
        common.env_setup()
        self.conf_file_path = "./my_express.conf"
        self.ssh_key_path = "%s/%s" %(os.getcwd(), common.getRandomString(10))
        self.info("Add -c option to client tools to specify openshift configuration file")

    def finalize(self):
        try:
            common.command_get_status("rm -f %s %s %s.pub" %(self.conf_file_path, self.ssh_key_path, self.ssh_key_path))
            common.update_sshkey()
        except Exception as e:
            self.error("ERROR in finalize(): %s"%str(e))


class SpecifyConfFile(OpenShiftTest):
    def test_method(self):
        self.add_step("Get the previous ssh key", OSConf.get_sshkey)

        self.add_step("Setup config file (instead of rhc setup)",
                      '''echo -e "libra_server=%s\ndefault_rhlogin=%s" > %s ''',
                      function_parameters = [ self.get_instance_ip(),
                                              self.user_email, 
                                              self.conf_file_path],
                      expect_return=0)

        self.add_step("Check config file to test if default rhlogin is written",
                      "cat %s" %(self.conf_file_path),
                      expect_str = [common.raw_str('default_rhlogin=%s' %(self.user_email))],
                      expect_return = 0,
                      expect_description = "The file should contain `default_rhlogin` entry")

        self.add_step("Change the default rhlogin in config file to %s" %(self.test_rhlogin),
                      "echo 'default_rhlogin=%s' >%s" %(self.test_rhlogin, self.conf_file_path),
                      expect_return=0)

        self.add_step("Generate new ssh key file",
                      "ssh-keygen -t rsa -f %s -N ''" %(self.ssh_key_path),
                      expect_return = 0)

        self.add_step("Modify %s to use the new ssh key" %(self.conf_file_path),
                      "echo 'ssh_key_file=%s' >>%s" %(self.ssh_key_path, self.conf_file_path),
                      expect_return = 0)

        self.add_step("Update the default ssh key",
                      common.update_sshkey,
                      function_parameters = [self.ssh_key_path + ".pub",
                                             "default",
                                             self.user_email,
                                             self.user_passwd,
                                             "--config %s" %(self.conf_file_path)],
                      expect_return=0)

        self.add_step("Get ssh key", OSConf.get_sshkey)

        def compare_key(key1, key2):
            print "Previous key fingerprint: %s" %(key1)
            print "New key fingerprint:      %s" %(key2)
            if key1 != key2:
                retcode = 12
            else:
                retcode = 0
            return retcode

        self.add_step("Compare key fingerprints",
                      compare_key,
                      function_parameters=["__OUTPUT__[1][1]", "__OUTPUT__[8][1]"],
                      expect_return=12)

        test_libra_server = "sldfkjasdlfkj"
        self.add_step("Modify %s to use specified libra server" %(self.conf_file_path),
                      '''echo "libra_server='%s'" >>%s''' %(test_libra_server, self.conf_file_path),
                      expect_return = 0)

        self.add_step("Run 'rhc domain show' to check libra server specifed in config file is being used",
                      "rhc domain show -l %s -p '%s' --config %s -d %s" % (self.user_email, self.user_passwd, self.conf_file_path, common.RHTEST_RHC_CLIENT_OPTIONS),
                      expect_str = ["https://%s" % (test_libra_server)])

        self.run_steps()
        
        return self.passed("%s passed" % self.__class__.__name__)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SpecifyConfFile)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
