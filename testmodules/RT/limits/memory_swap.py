#!/usr/bin/env python

import os
import common
import OSConf
import rhtest
import proc

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = ["DEV"]

    def initialize(self):
        self.exp_file='rhc_tail-%s.expect'%common.getRandomString(5)
        self.app_name = common.getRandomString(10)
        self.app_type = 'php'
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd

        common.env_setup()
        self.steps_list = []

    def finalize(self):
        os.system("rm -rf %s %s"%(self.app_name, self.exp_file))
        try:
            self.proc.kill()
        except:
            pass


class MemorySwap(OpenShiftTest):
    def change_mem_limit(self):
        #res_limit_file = "/var/lib/openshift/%s/%s/configuration/etc/php.ini"%(OSConf.get_app_uuid(self.app_name), "".join([a for a in common.app_types[self.app_type] if a.isalpha()]))
        res_limit_file = "/var/lib/openshift/%s/%s/configuration/etc/php.ini"%(OSConf.get_app_uuid(self.app_name),self.app_type)
        command = "sed -i -e 's/^memory_limit=.*/memory_limit=1280M/' %s"%res_limit_file
        #(status, output) = common.run_remote_cmd(None, command, as_root=True)
        (status, output) = common.run_remote_cmd(self.app_name, command, as_root=True)
        return status

    def create_proc(self, cmd):
        fw = open(self.exp_file, 'wb')
        fw.write('''spawn -nottyinit %s
set timeout -1
expect wait_for_ever_and_ever'''%cmd)
        fw.close()
        cmd2 = ['/usr/bin/expect', self.exp_file]
        self.proc = proc.Proc(cmd2,
                              shell=False, 
                              stdin=open(os.devnull, 'rb'))

    def verify(self, size, oom_check=False):
        if (oom_check==True):
            self.debug("Run rhc tail as monitor into background...")
            self.create_proc('/usr/bin/rhc tail %s -o "-n 20" -p %s -l %s %s'%(self.app_name, 
                                                                                self.user_passwd, 
                                                                                self.user_email,
                                                                                common.RHTEST_RHC_CLIENT_OPTIONS))

        url = OSConf.get_app_url(self.app_name)
        status = common.grep_web_page("%s/test.php?size=%s"%(url,size), 'PASS', delay=2, count=6)
            
        if (oom_check==True):
            ret = self.proc.grep_output("PHP Fatal error:\s+Allowed memory size of", 3, 10)
            self.proc.kill()
            if ret==0:
                return 2
            else:
                self.error("There was no OOM found in %s application."%self.app_name)
                return 3

        return status

    def test_method(self):
        self.add_step("Create a PHP app",
                      common.create_app,
                      function_parameters=[self.app_name, 
                                           common.app_types[self.app_type], 
                                           self.user_email, 
                                           self.user_passwd, 
                                           True],
                      expect_return=0)

        self.add_step("Change memory_limit",
                      self.change_mem_limit,
                      expect_return=0)

        self.add_step("Restart the %s"%self.app_name,
                      common.restart_app,
                      function_parameters = [self.app_name, self.user_email, self.user_passwd],
                      expect_return=0)


        self.add_step("Add greedy test app ",
                      '''cd %s && cat <<'EOF' >php/test.php &&
<?php
  $handle = fopen("/dev/zero", "r");
  $contents = fread($handle, $_GET["size"]);
  fclose($handle);
  print 'PASS';
?>
EOF
                      git add php/test.php &&
                      git commit -m "Added test.php" -a && git push'''%self.app_name,
                      expect_return=0)


        self.add_step("Check the memory_limit less than 612M",
                      self.verify,
                      function_parameters = [54857600],
                      expect_return=0)

        self.add_step("Check the memory_limit more than 612M",
                      self.verify,
                      function_parameters = [654857600, True],
                      expect_return=2)

        self.add_step("Destroy app: %s" % (self.app_name),
                      common.destroy_app,
                      function_parameters = [self.app_name],
                      expect_return = 0)

        self.info("[US1265][rhc-limits]memory swap testing")

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MemorySwap)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
