"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012

Refactored by
Attila Nagy
anagy@redhat.com
Jun 11, 2012

[US1178 & US1034][RT] Create Jenkins cartridge application for CI testing
https://tcms.engineering.redhat.com/case/122369/
"""

import rhtest
import common
from shutil import rmtree
import fileinput
import re
import OSConf
import proc
import os


class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.info("[US1178 & US1034] [rhc-cartridge] Create Jenkins cartridge application for CI testing")
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing variant, using `zend` as default")
            self.test_variant = 'zend'

        self.info("VARIANT: %s"%self.test_variant)
        self.app_name = self.test_variant.split('-')[0] + "ci" + common.getRandomString(3)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        common.env_setup()
        self.random_string = common.getRandomString()
        self.deployment_configuration = {
           "php": {"index": "php/index.php"},
           "zend": {"index": "php/index.php"},
           "jbossas": {"index": "src/main/webapp/index.html"},
           "jbosseap": {"index": "src/main/webapp/index.html"},
           "python": {"index": "wsgi/application"},
           "ruby": {"index": "config.ru"},
           "ruby-1.9": {"index": "config.ru"},
           "nodejs" : {"index": "index.html"},
           "perl": {"index": "perl/index.pl"}}

    def finalize(self):
        #rmtree(self.app_name, ignore_errors = True)
        if self.test_variant == "jbossas" or self.test_variant == "jbosseap":
            if self.get_run_mode() == "DEV":
                pass
                # back to small profile
                #common.change_node_profile("small")
                #common.remove_gearsize_capability('medium')

class JenkinsCITesting(OpenShiftTest):
        
    def test_method(self):
        self.info("=================================")
        self.info("1.Create an jenkins app")
        self.info("=================================")
        ret_code = common.create_app("server", common.app_types["jenkins"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False)
        self.assert_equal(ret_code, 0, "Jenkins server must be created successfully")
        
        self.info("=================================")
        self.info("2. Create an application")
        self.info("=================================")
        ret_code = common.create_app(self.app_name, 
                        self.app_type, 
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret_code, 0, "Failed to create %s app: %s" % (self.app_type, self.app_name))
        
        if self.test_variant in ("jbossas", "jbosseap"):
            # JBoss needs larger node profile to build
            if self.get_run_mode() == "DEV":
                #20120615: we don't need to change node profile any more
                pass
                #common.add_gearsize_capability('medium')
                #ret = common.change_node_profile("medium")
                #self.assert_equal(ret, 0, "The change of node profile to medium should pass.")
                #time.sleep(30)
        
        self.info("=================================")
        self.info("3. Embed jenkins client to the app")
        self.info("=================================")
        ret_code = common.embed(self.app_name, 
                        "add-" + common.cartridge_types["jenkins"], 
                        self.config.OPENSHIFT_user_email, 
                        self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret_code, 0, "Jenkins client must be embedded successfully")
        
        self.info("=================================")
        self.info("4.Make some change in the git repo")
        self.info("=================================")
        try:
            index_file = self.git_repo + "/" + self.deployment_configuration[self.test_variant]["index"]
            self.info("Editing: " + index_file)
            for line in fileinput.input(index_file, inplace = True):
                print re.sub("Welcome to OpenShift", self.random_string, line),
        except:
            fileinput.close()
            self.info("IO error")
            return False
        fileinput.close()
        
        try:
            start_hook_file = "/.openshift/action_hooks/build"
            #start_hoot_file = "./.openshift/action_hooks/build"
            self.info("Editing: " + start_hook_file)
            start_hook = open(self.git_repo + start_hook_file, "w+")
            start_hook.write("#! /bin/bash\nset -x\nsleep 120\n")
            start_hook.close()
            os.chmod(self.git_repo + start_hook_file, 0755)
        except:
            self.info("IO Error ")
            return False
        
        self.info("=================================")
        self.info("5. Git push all the changes in a subprocess")
        self.info("=================================")
        deployment_steps = [
            "cd %s" % self.app_name,
            "git add .",
            "git commit -a -m testing",
            "git push"                    
        ]
        deployment_process = proc.Proc(" && ".join(deployment_steps))

        self.info("=================================")
        self.info("6. Jenkins build job should start in given time")
        self.info("=================================")
        ret_code = deployment_process.grep_output("Waiting for job to complete", 5, 60)
        self.assert_equal(ret_code, 0, "Job must be waiting for start")
        
        self.info("=================================")
        self.info("7. Check if jenkins build job is running")
        self.info("=================================")
        job_url = OSConf.default.conf['apps'][self.app_name]['embed']['jenkins-client-1']['url']
        option = "-k -H 'Pragma: no-cache' -u %s:%s" % (OSConf.default.conf["apps"]["server"]["username"], OSConf.default.conf["apps"]["server"]["password"])
        ret_code = common.grep_web_page(job_url + "1/consoleText", "sleep 120", option, 7, 15)
        self.assert_equal(ret_code, 0)
        
        self.info("=================================")
        self.info("8. Check if the normal app is still available")
        self.info("=================================")
        ret_code = common.grep_web_page(OSConf.get_app_url(self.app_name), 
                        "Welcome to OpenShift", 
                        "-H 'Pragma: no-cache'", 5, 30 )
        self.assert_equal(ret_code, 0)
        
        self.info("=================================")
        self.info("9. Wait for git push to finish")
        self.info("=================================")
        deployment_process.wait(5, 10)
        
        self.info("=================================")
        self.info("10. Check if jenkins build is finished successfully")
        self.info("=================================")
        ret_code = common.grep_web_page(job_url + "1/api/xml", 
                        '<result>SUCCESS</result>', option, 60, 30)
        self.assert_equal(ret_code, 0)
        
        self.info("=================================")
        self.info("11. Check if the normal app is still available")
        self.info("=================================")
        ret_code = common.grep_web_page(OSConf.get_app_url(self.app_name), 
                        self.random_string, "-H 'Pragma: no-cache'", 5, 20)
        self.assert_equal(ret_code, 0)
                
        return self.passed("[US1178 & US1034] [rhc-cartridge] Create Jenkins cartridge application for CI testing")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsCITesting)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
