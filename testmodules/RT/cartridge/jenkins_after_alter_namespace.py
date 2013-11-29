#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012

Refactoring:
Attila Nagy
anagy@redhat.com
Jun 12, 2012

[US1178 & US1034] [rhc-cartridge] jenkins build after alter domain namespace
https://tcms.engineering.redhat.com/case/122370/
"""
import os
import re
import rhtest
import common
import OSConf
from shutil import rmtree
import fileinput

class OpenShiftTest(rhtest.Test):
    
    def initialize(self):
        self.summary = "[US1178 & US1034] [rhc-cartridge] jenkins build after alter domain namespace"
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing OPENSHIFT_test_name, used `php` as default.")
            self.test_variant = "zend"

        self.domain_name = common.get_domain_name()
        self.new_domain_name = common.getRandomString(10)
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(10)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        self.jenkins_name = "jen"+common.getRandomString(7)
        self.sshkey_backup_dir = "/tmp/"+common.getRandomString(10)
        os.mkdir(self.sshkey_backup_dir)
        self.deployment_configuration = {
            "php": { "index" : "php/index.php" },
            "zend" : { "index" : "php/index.php" },
            "jbossas" : { "index" : "src/main/webapp/index.html" },
            "jbosseap" : { "index" : "src/main/webapp/index.html" },
            "jbossews" : { "index" : "src/main/webapp/index.html" },
            "jbossews2" : { "index" : "src/main/webapp/index.html" },
            "python" : { "index" : "wsgi/application" },
            "ruby" : { "index" : "config.ru" },
            "perl" : { "index" : "perl/index.pl" },
            "nodejs" : { "index" : "index.html" },
        }
        self.deployment_configuration["ruby-1.9"] = self.deployment_configuration["ruby"]
        self.random_string = common.getRandomString()
        common.env_setup()


    def finalize(self):
        rmtree(self.git_repo)
        #"10.Move ssh key back",
        #common.command_get_status("test -f %s/id_rsa -a -f %s/id_rsa.pub && rm -f ~/.ssh/id_rsa* && mv %s/id_rsa* ~/.ssh/"%(self.sshkey_backup_dir,self.sshkey_backup_dir,self.sshkey_backup_dir))
        #rmtree(self.sshkey_backup_dir)
        common.alter_domain(self.domain_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        #common.update_sshkey()
        if self.test_variant in ( "jbosseap", "jbossas", "jbossews","jbossews2"):
            if self.get_run_mode() == "DEV":
                pass
                #common.change_node_profile("small")


class JenkinsAfterAlterNamespace(OpenShiftTest):
    
    def deploy_changes(self, source, destination):
        try:
            index_file = self.git_repo + "/" + self.deployment_configuration[self.test_variant]["index"]
            self.info("Editing: " + index_file)
            for line in fileinput.input(index_file, inplace = True):
                print re.sub(source, destination, line),
        except:
            fileinput.close()
            self.info("IO error")
            return False
        fileinput.close()
        
        deployment_steps = [
            "cd %s" % self.app_name,
            "git commit -a -m testing",
        ]
        return common.command_getstatusoutput(" && ".join(deployment_steps))
    
    def test_method(self):
        self.info("=============================")
        self.info("1. Create an jenkins app")
        self.info("=============================")
        ret_code = common.create_app(
                self.jenkins_name, common.app_types["jenkins"], 
                self.config.OPENSHIFT_user_email, 
                self.config.OPENSHIFT_user_passwd,
                clone_repo = False
        )
        self.assert_equal(ret_code, 0, "Failed to create jenkins app")

        self.info("=============================")
        self.info("2. Create an app")
        self.info("=============================")
        ret_code = common.create_app(
                self.app_name, 
                self.app_type, 
                self.config.OPENSHIFT_user_email, 
                self.config.OPENSHIFT_user_passwd,
        )
        self.assert_equal(ret_code, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))
        
        if self.test_variant in ( "jbosseap", "jbossas","jbossews", "jbossews2"):
            if self.get_run_mode() == "DEV":
                pass
                #self.info("Changing node profile to 'medium'")
                #common.change_node_profile("medium")
        
        self.info("=============================")
        self.info("3. Embed jenkins client to the app")
        self.info("=============================")
        ret_code = common.embed(
                self.app_name, 
                "add-" + common.cartridge_types["jenkins"], 
                self.config.OPENSHIFT_user_email, 
                self.config.OPENSHIFT_user_passwd,
        )
        self.assert_equal(ret_code, 0, "Failed to embed jenkins client to the app")
       
        # No need to update SSH key pair now, since it is associated with a user 
        # rather than a domain

        ''' 
        self.info("=============================")
        self.info("4. Backup the libra ssh key and create new key pair")
        self.info("=============================")
        ret_code = common.command_get_status("mv ~/.ssh/id_rsa* %s/ && ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa" % ( self.sshkey_backup_dir )),
        '''

        self.info("=============================")
        self.info("5. Alter domain")
        self.info("=============================")
        ret_code = common.alter_domain(
                self.new_domain_name, 
                self.config.OPENSHIFT_user_email, 
                self.config.OPENSHIFT_user_passwd,
        )
        self.assert_equal(ret_code, 0, "Failed to alter domain name")

        '''
        self.info("=============================")
        self.info("6. Update ssh key")
        self.info("=============================")
        ret_code = common.update_sshkey()
        self.assert_equal(ret_code, 0, "Failed to update ssh key")
        '''

        self.info("=============================")
        self.info("7.Change git config file in git repo")
        self.info("=============================")
        ret_code = common.command_get_status("sed -i -e 's/%s/%s/g' %s/.git/config" % ( self.domain_name, self.new_domain_name, self.git_repo ))
        self.assert_equal(ret_code, 0, "Failed to change git config file in git repo")
        
        self.info("=============================")
        self.info("8. Make some change in the git repo and git push to trigger jenkins build job")
        self.info("=============================")
        (ret_code, output) = self.deploy_changes("Welcome to OpenShift", self.random_string)
        self.debug(output)
        ret = common.trigger_jenkins_build(self.app_name)
        self.assert_equal(ret, True, "Failed to git push the changes to trigger jenkins build job")
        
        
        self.info("=============================")
        self.info("9. Check the jenkins build url")
        self.info("=============================")
        ret_code = common.grep_web_page(
                str(OSConf.default.conf["apps"][self.app_name]["embed"][common.cartridge_types["jenkins"]]["url"]).replace(self.domain_name, self.new_domain_name), 
                "Last Successful Artifacts", 
                "-L -k -H 'Pragma: no-cache' -u %s:%s" % (OSConf.default.conf["apps"][self.jenkins_name]["username"], OSConf.default.conf["apps"][self.jenkins_name]["password"]),
                60, 10
        )
        self.assert_equal(ret_code, 0, "Job URL must be accessed successfully")

        self.info("=============================")
        self.info("10. Check if the changes take effect")
        self.info("=============================")
        ret_code = common.grep_web_page(
                str(OSConf.get_app_url(self.app_name)).replace(self.domain_name, self.new_domain_name), 
                self.random_string, 
                "-L -k -H 'Pragma: no-cache'", 
                15, 6
        )
        self.assert_equal(ret_code, 0, "Changes must be deployed")
 
        return self.passed("[US1178 & US1034] [rhc-cartridge] jenkins build after alter domain namespace")


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsAfterAlterNamespace)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
