#!/usr/bin/env python
import os
import common
import rhtest
import socket
import re

# http://www.linuxfoundation.org/collaborate/workgroups/networking/netem
# http://lartc.org/howto/lartc.qdisc.classful.html
PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types["php"]
        self.app_name = common.getRandomString(10)
        common.env_setup()
        self.eth_device='eth0'
        self.info("Shaped device: %s"%self.eth_device)
        self.timeout = 90 #seconds (should be greater then default)

    def finalize(self):
        self.reset_emulation()


class TimeoutOptionTesting(OpenShiftTest):
    def reset_emulation(self):
        try:
            self.debug("\nCheck TC rules before action:")
            common.command_get_status("sudo tc qdisc show dev %s"%self.eth_device)
            self.debug("\nRemoving TC rule...")
            common.command_get_status("sudo tc qdisc del dev %s root"%self.eth_device)
            self.debug("\nCheck TC rules after action:")
            common.command_get_status("sudo tc qdisc show dev %s"%self.eth_device)
            self.debug("\nDestroying app...")
            common.destroy_app(self.app_name, self.user_email, self.user_passwd)
            os.system("rm -rf %s"%self.app_name)
        except:
            pass

    def emulate_delay(self):
        if not re.search(r"^\d+\.\d+\.\d+\.\d+",self.get_instance_ip()):
            ips = socket.gethostbyname_ex(self.get_instance_ip())[2]
            ip = [i for i in ips if i.split('.')[0] != '127'][0]
        else:
            ip = self.get_instance_ip()
        commands = [
            "sudo tc qdisc add dev "+self.eth_device+" root handle 1: prio ",
            "sudo tc qdisc add dev "+self.eth_device+" parent 1:3 handle 30: tbf rate 2kbit buffer 1600 limit 3000 ",
            "sudo tc qdisc add dev "+self.eth_device+" parent 30:1 handle 31: netem delay 21s ",   #should generate delay bigger than default (20s)
            #"sudo tc qdisc add dev "+self.eth_device+" parent 30:1 handle 31: netem loss 99%% ",
            #"sudo tc filter add dev "+self.eth_device+" protocol ip parent 1:0 prio 3 u32 match ip src %s/32 flowid 1:3"%ip,
            "sudo tc filter add dev "+self.eth_device+" protocol ip parent 1:0 prio 3 u32 match ip dst %s/32 flowid 1:3"%ip]
        return common.command_get_status(" && \n".join(commands))

    def test_method(self):
        self.add_step("Simulate bad network: Set network delay as 5s using tc (This script must be run as root)",
                      self.emulate_delay,
                      #command="sudo tc qdisc add dev %s root netem delay 5s"%self.eth_device,
                      expect_return=0)

        self.add_step("DEBUG", "sudo tc qdisc show dev %s "%self.eth_device)
        self.add_step("Try to create app without timeout option (default is 20s)",
                      "rhc app create %s %s -l %s -p '%s' --no-git --insecure" %(self.app_name, 
                                                                       self.app_type, 
                                                                       self.user_email, 
                                                                       self.user_passwd),
                      expect_description="Should get executation exprired response message. App can not be created",
                      expect_return="!0",
                      expect_str=["Timeout::Error"],
                      try_count=2)

        ''' it's very hard to simulate such condition to test both scenarious in delayed environment'''
        self.add_step("DEBUG", "sudo tc qdisc show dev %s "%self.eth_device)
        self.add_step("Create the same app with timeout option %ds"%self.timeout,
                      "rhc app create %s %s -l %s -p '%s' --no-git --timeout %d --insecure" %(self.app_name, 
                                                                                    self.app_type, 
                                                                                    self.user_email, 
                                                                                    self.user_passwd, 
                                                                                    self.timeout),
                      expect_description="App is created successfully",
                      try_count=2,
                      expect_return=0)

        self.add_step("DEBUG", "sudo tc qdisc show dev %s "%self.eth_device)
        self.add_step("Destroy the same app without timeout option (default is 10s)",
                      "rhc app destroy %s -l %s -p '%s' --confirm --insecure" %(self.app_name,
                                                                  self.user_email, 
                                                                  self.user_passwd),
                      expect_description="Should get executation exprired response message. App can not be destroyed",
                      expect_return="!0",
                      try_count=2,
                      expect_str=["execution expired"])

        self.add_step("DEBUG", "sudo tc qdisc show dev %s "%self.eth_device)
        self.add_step("Destroy the same app with timeout option %d"%self.timeout,
                      "rhc app destroy %s -l %s -p '%s' --confirm --timeout %d --insecure" %(self.app_name, 
                                                                               self.user_email, 
                                                                               self.user_passwd, 
                                                                               self.timeout),
                      expect_description="App is destroyed successfully",
                      try_count=2,
                      expect_return=0)

        self.info("[US1110][rhc-client] timeout option testing")
        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(TimeoutOptionTesting)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
