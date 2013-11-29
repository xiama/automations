"""
Jiangtao Zhao
jizhao@redhat.com
Feb 10, 2012
[US1178 & US1034] [rhc-cartridge] Add/Remove jenkins client for user app 
https://tcms.engineering.redhat.com/case/122367/
"""

import rhtest
import common
from shutil import rmtree
import fileinput
import re
import OSConf
import time

class OpenShiftTest(rhtest.Test):

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("Missing self.config.test_variant, using `zend` as default")
            self.test_variant='zend'

        self.info("VARIANT: %s"%self.test_variant)
        self.app_name = self.test_variant.split('-')[0] + common.getRandomString(7)
        self.jenkins_name = "jenkins" + common.getRandomString(5)
        self.git_repo = "./%s" % (self.app_name)
        self.app_type = common.app_types[self.test_variant]
        common.env_setup()
        self.random_string = common.getRandomString()
        self.random_string2 = common.getRandomString()
        self.deployment_configuration = {
            "php": { "index" : "php/index.php" },
            "zend": { "index" : "php/index.php" },
            "jbossas" : { "index" : "src/main/webapp/index.html" },
            "jbosseap" : { "index" : "src/main/webapp/index.html" },
            "jbossews" : { "index" : "src/main/webapp/index.html" },
            "jbossews-2.0" : { "index" : "src/main/webapp/index.html" },
            "python" : { "index" : "wsgi/application" },
            "ruby" : { "index" : "config.ru" },
            "perl" : { "index" : "perl/index.pl" },
            "nodejs" : { "index" : "index.html" },
        }
        self.deployment_configuration["ruby-1.9"] = self.deployment_configuration["ruby"]
        self.deployment_configuration["python-2.7"] = self.deployment_configuration["python"]
        self.deployment_configuration["python-3.3"] = self.deployment_configuration["python"]

    def finalize(self):
        pass
        #rmtree(self.app_name, ignore_errors = True)

class AddRemoveJenkinsClient(OpenShiftTest):
    
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
        
        return common.trigger_jenkins_build(self.git_repo)

    
    def test_method(self):
        self.info("=================================")
        self.info("1. Check 'jenkins-client-*' in the output")
        self.info("=================================")
        ( ret_code, ret_output ) = common.command_getstatusoutput("rhc cartridge list -l %s -p '%s' %s" % ( self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        self.assert_true(ret_output.find(common.cartridge_types["jenkins"]) != -1, "Cartridge 'jenkins-client' must be shown in cartridge list")
        
        self.info("=================================")
        self.info("2. Create a jenkins app")
        self.info("=================================")
        ret_code = common.create_app(self.jenkins_name, common.app_types["jenkins"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, False)
        self.assert_equal(ret_code, 0, "Jenkins server must be created successfully")
        
        self.info("=================================")
        self.info("3. Create an application")
        self.info("=================================")
        ret_code = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret_code, 0, "The app must be created successfully")
        
        if self.test_variant in ("jbossas", "jbosseap", "jbossews", "jbossews-2.0"):
            if self.config.options.run_mode=="DEV":
                # 20120605: the jenkins jobs now accept small profile
                pass
                # JBoss needs larger node profile to build
                #ret = common.change_node_profile("medium")
                #self.assert_equal(ret, 0, "Changing node profile to medium should pass")
                #time.sleep(30)
        
        self.info("=================================")
        self.info("4. Embed jenkins client to the app")
        self.info("=================================")
        ret_code = common.embed(self.app_name, 
                                "add-" + common.cartridge_types["jenkins"], 
                                self.config.OPENSHIFT_user_email, 
                                self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret_code, 0, "Jenkins client must be embedded successfully")
        
        self.info("=================================")
        self.info("5. Make some change in the git repo and git push")
        self.info("=================================")
        ret_code = self.deploy_changes("Welcome to", self.random_string)
        self.assert_equal(ret_code, True, "Changes must be deployed successfully")
        
        self.info("=================================")
        self.info("6. Check the jenkins build urls")
        self.info("=================================")
        ret_code = common.grep_web_page(
           OSConf.default.conf['apps'][self.app_name]['embed']['jenkins-client-1']['url'],
           "Last Successful Artifacts",
           "-v -L -k -H 'Pragma: no-cache' -u '%s:%s'" % (OSConf.default.conf["apps"][self.jenkins_name]["username"], OSConf.default.conf["apps"][self.jenkins_name]["password"]),
           delay = 5, count = 10
        )
        self.assert_equal(ret_code, 0, "Must be built successfully")
        
        self.info("=================================")
        self.info("7. Check the changes take effect")
        self.info("=================================")
        ret_code = common.grep_web_page(OSConf.get_app_url(self.app_name), self.random_string)
        self.assert_equal(ret_code, 0, "Changes must be found on the web-site")
        
        self.info("=================================")
        self.info("8. Remove jenkins client from the app")
        self.info("=================================")
        ret_code = common.embed(self.app_name, "remove-" + common.cartridge_types["jenkins"])
        self.assert_equal(ret_code, 0, "Jenkins client must be removed successfully")
        
        self.info("=================================")
        self.info("9. Make some change and git push again")
        self.info("=================================")
        ret_code = self.deploy_changes(self.random_string, self.random_string2)
        self.assert_equal(ret_code, True, "Changes must be deployed successfully")
        
        self.info("=================================")
        self.info("10.Check the changes take effect")
        self.info("=================================")
        ret_code = common.grep_web_page(OSConf.get_app_url(self.app_name), self.random_string2, delay=5, count=8)
        self.assert_equal(ret_code, 0, "Changes must be found on the web-site")
        
        return self.passed("[US1178 & US1034] [rhc-cartridge] Add/Remove jenkins client for user app")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AddRemoveJenkinsClient)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
