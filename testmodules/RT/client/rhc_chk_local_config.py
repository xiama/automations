#!/usr/bin/env python

import os 
import common
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US514][UI][rhc-client]rhc domain status ssh-agent test\n[US514][UI][rhc-client]rhc domain status remote and local pub key match\n[US514][UI][rhc-client]rhc domain status ssh files permissons")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        common.env_setup()

    def finalize(self):
        os.system("killall ssh-agent")
        self.debug("Restore libra ssh key pair")
        os.system("test -f /tmp/id_rsa && test -f /tmp/id_rsa.pub && rm -f ~/.ssh/id_rsa ~/.ssh/id_rsa.pub && mv /tmp/id_rsa* ~/.ssh/")
        self.debug("Restore remote ssh key")
        common.update_sshkey()


class RhcChkLocalConfig(OpenShiftTest):
    def test_method(self):

        self.add_step("Run rhc domain status without ssh-agent running",
                      "rhc domain status -l %s -p %s %s" % (self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                      expect_description="ssh-agent fail because ssh-agent is not running",
                      #expect_str=["Could not open a connection to your authentication agent"],
                      expect_return="!0")

        self.add_step("Run ssh-agent",
                      "ssh-agent",
                      expect_description="ssh-agent starts successfully",
                      expect_return=0,
                      expect_str=["Agent pid"],
                      output_filter="(?<=SSH_AUTH_SOCK=)[^;]*(?=;)")

        self.add_step("export SSH_AUTH_SOCK to env",
                      common.set_env,
                      function_parameters=["SSH_AUTH_SOCK", "__OUTPUT__[2]"],
                      expect_description="ssh-agent starts successfully",
                      #expect_str=["Agent pid"],
                      #output_filter=["(?<=SSH_AUTH_SOCK=)[^;]*(?=;)"],
                      expect_return=0)

        self.add_step("ssh-add libra private key",
                      "ssh-add ~/.ssh/id_rsa",
                      expect_description="libra private key added",
                      expect_return=0,
                      expect_str=["Identity added"])
         
        self.add_step("Run rhc domain status with ssh-agent running",
                      "rhc domain status -l %s -p %s %s" % (self.user_email, self.user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS),
                      expect_description="rhc domain status detected ssh-agent",
                      expect_return=0,
                      expect_str=["your system has passed all tests"])

        self.add_step("Backup the key pair",
                      "mv ~/.ssh/id_rsa ~/.ssh/id_rsa.pub /tmp/",
                      expect_description="moved libra key pair to /tmp",
                      expect_return=0,
                      expect_str=[])

        self.add_step("Generate a new pair of ssh keys",
                      "ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ''",
                      expect_description="Successfully created a key pair",
                      expect_return=0,
                      expect_str=["identification has been saved", 
                                  "public key has been saved", 
                                  "The key fingerprint is"])

        self.add_step("Compare the fingerprint of the one ssh-add holds and the new one on the filesystem",
                      "[ $(ssh-add -l | cut -d' ' -f 2) == $(ssh-keygen -lf ~/.ssh/id_rsa | cut -d' ' -f 2) ] && echo 'yes' || echo 'no'",
                      expect_description="The two fingerprints are different",
                      expect_return=0,
                      expect_str=['no'],
                      unexpect_str=['yes'])

        self.add_step("Run rhc domain status without the new key loaded",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should fail saying the key not loaded",
                      expect_return="!0",
                      expect_str=["assert !\(@@remote_pub_keys"])

        self.add_step("ssh-add new libra private key",
                      "ssh-add ~/.ssh/id_rsa",
                      expect_description="new libra private key added",
                      expect_return=0,
                      expect_str=["Identity added"])
        
        self.add_step("Compare the fingerprint of the newly added key by ssh-add and the one on the filesystem",
                      "[ $(ssh-add -l | cut -d' ' -f 2 | awk 'NR==2') == $(ssh-keygen -lf ~/.ssh/id_rsa | cut -d' ' -f 2) ] && echo 'yes' || echo 'no'",
                      expect_description="The two fingerprints are the same",
                      expect_return=0,
                      expect_str=['yes'],
                      unexpect_str=['no'])

        self.add_step("Run rhc domain status again with remote and local key dismatch",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should fail because remote and local key don't match",
                      expect_return="!0",
                      expect_str=["assert !\(@@remote_pub_keys" ])

        self.add_step("Update the remote ssh key",
                      common.update_sshkey,
                      expect_description="Remote ssh key altered successfully",
                      expect_return=0)

        self.add_step("Run rhc domain status again after altering the remote ssh key",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should pass",
                      expect_return=0,
                      expect_str=["your system has passed all tests"])

        self.add_step("Change permissions of ssh key and config file",
                      "chmod 644 ~/.ssh/id_rsa ~/.ssh/config",
                      expect_return=0)

        self.add_step("Run rhc domain status again",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should fail because files have incorrect permissions",
                      expect_return="!0",
                      expect_str = ["assert_match\(permission, perms, error_for" ],)
       
        self.add_step("Change permissions of ssh key and config file",
                      "chmod 000 ~/.ssh/id_rsa ~/.ssh/config",
                      expect_return=0)

        self.add_step("Run rhc domain status again",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should fail because files have incorrect permissions",
                      expect_return="!0",
                      expect_str=["assert_match\(permission, perms"])

        self.add_step("Change permissions of ssh key and config file",
                      "chmod 600 ~/.ssh/id_rsa ~/.ssh/config",
                      expect_return=0)

        self.add_step("Run rhc domain status again",
                      "rhc domain status -l %s -p %s" % (self.user_email, self.user_passwd),
                      expect_description="rhc domain status should pass",
                      expect_return=0,
                      expect_str=["your system has passed all tests"])

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcChkLocalConfig)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
