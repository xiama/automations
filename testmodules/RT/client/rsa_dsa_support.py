import os
import common, OSConf
import rhtest
import re
import shutil


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1608][BI] : Allow RSA and DSA SSH keys - CLI")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types["php"]
        self.app_name = "php"+common.getRandomString(7)
        self.backup_dir = os.path.join(common.get_tmp_dir(),common.getRandomString(10))
        self.ssh_keyname="id_rsa"
        self.ssh_key = os.path.join(os.path.expanduser("~"),".ssh", self.ssh_keyname)
        common.env_setup()

    def finalize(self):
        self.revert_backup()
        common.update_sshkey()


class RsaDsaSupport(OpenShiftTest):
    
    def verify(self):
        url = OSConf.get_app_url(self.app_name)
        return common.grep_web_page(url+"/index.php", "OpenShift")

    def revert_backup(self):
        backup_key=os.path.join(self.backup_dir, self.ssh_keyname)
        if os.path.exists(backup_key) and os.path.exists(backup_key+".pub"):
            self.info("Reverting backup from %s..."%self.backup_dir)
            os.remove(self.ssh_key)
            os.remove(self.ssh_key+".pub")
            os.rename("%s"%backup_key, os.path.expanduser("~/.ssh/%s"%self.ssh_keyname))
            os.rename("%s.pub"%(backup_key), os.path.expanduser("~/.ssh/%s.pub"%self.ssh_keyname))
        else:
            self.info("No revert due to missing backup!")
        shutil.rmtree(self.backup_dir)

        return 0

    def do_backup(self):
        os.makedirs(self.backup_dir)
        self.info("Making backup into %s"%self.backup_dir)
        if not os.path.exists(self.ssh_key):
            self.error("SSH key[%s] doesn't exist!"%self.ssh_key)
            return 1
        try:
            os.rename(self.ssh_key, os.path.join(self.backup_dir, self.ssh_keyname))
            os.rename(self.ssh_key+".pub", os.path.join(self.backup_dir, self.ssh_keyname+".pub"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error(e)
            return 1
        return 0

    def gen_dsa_key(self):
        key_path=os.path.join(common.get_tmp_dir(), self.ssh_keyname)
        try:
            os.remove(key_path)
        except:
            pass
        cmd = "ssh-keygen -t dsa -N '' -f %s "%(key_path)
        r = common.cmd_get_status(cmd, quiet=True)
        if r == 0:
            os.rename(key_path, self.ssh_key)
            os.rename(key_path+".pub", self.ssh_key+".pub")
            return 0
        else:
            self.error("Unable to generate new DSA key")
            return 1

    def verify_signature(self):
        f = open(self.ssh_key+".pub", 'r')
        key = f.read()
        f.close()
        if re.match("^ssh-dss", key):
            return 0
        return 1

    def test_method(self):

        self.add_step("Backup .ssh/%s key "%self.ssh_keyname,
                self.do_backup,
                expect_return=0)

        self.add_step("Create DSA key pair and do update",
                self.gen_dsa_key,
                expect_return=0)

        self.add_step("Update the default ssh key",
                common.update_sshkey,
                expect_return=0)

        self.add_step("Verify DSA signature",
                self.verify_signature,
                expect_return=0)
        
        self.add_step("Create testing app",
                common.create_app,
                function_parameters=[self.app_name, 
                                     self.app_type, 
                                     self.user_email, 
                                     self.user_passwd, 
                                     True],
                expect_return=0)

        self.add_step("Check new app url is available...",
                self.verify, 
                expect_return=0)

        self.add_step("Modify and push the application...",
                self.modify_and_push,
                expect_return=0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)

    def modify_and_push(self):
        test_file = os.path.join("php","test.php")
        common.write_file(os.path.join(self.app_name, test_file), "<?php phpinfo(); ?>")
        cmd = "cd %s && git add %s && git commit -m 'test' -a && git push" % (self.app_name, test_file),
        (status, output) = common.cmd_get_status_output(cmd)
        if (status == 0):
            return 0
        else:
            self.error(output)
            return 1

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RsaDsaSupport)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
