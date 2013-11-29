"""
Attila Nagy
anagy@redhat.com
May 5, 2012

[US2001][Runtime][rhc-node] jenkins show correct builder size in config page
"""

import rhtest
import common
import OSConf
import pycurl
from StringIO import StringIO
from time import sleep
from shutil import rmtree

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US2001][Runtime][rhc-node] jenkins show correct builder size in config page"
        self.app_name_small = "myphpsmall"
        self.app_name_medium = "myjbossmedium"

        common.env_setup(cleanup=True)

    def finalize(self):
        for repo in [ self.app_name_small, self.app_name_medium ]:
            rmtree(repo, ignore_errors = True)
        if self.get_run_mode() == "DEV":
            common.change_node_profile("small")
            common.remove_gearsize_capability('medium') #default is small only
    
class JenkinsBuilderSize(OpenShiftTest):
        
    def test_method(self):
        # This step is needed to create builder machines
        if self.get_run_mode() == "DEV":
            common.add_gearsize_capability('medium')
        #
        # Step 1
        #
        self.info("1. create jenkins server app")
        ret_code = common.create_app("jenkins", 
                                     common.app_types["jenkins"], 
                                     clone_repo = False)
        
        self.assert_equal(ret_code, 0, "Jenkis app must be created successfully")
        #
        # Step 2  
        #
        self.info("2. go to jenkins config page check the builder size")
        app_cache = OSConf.get_apps()
        self.jenkins_url = app_cache['jenkins']['url']
        self.jenkins_username = app_cache['jenkins']['username']
        self.jenkins_password = app_cache['jenkins']['password']
        sleep(120)
        jenkins_config_output = self.get_jenkins_page("configure")
        
        # Waiting for Jenkins to stand up
 
        str2find='<select name="defaultBuilderSize"><option selected="true" value="small">Small</option><option value="medium">Medium</option></select>'
        self.assert_true(
            jenkins_config_output.find(str2find) != -1,
                "Drop-down list 'Default Builder Size' must contain options 'Small' and 'Medium' (small as default)")

        #
        # Step 3
        #
        self.info("3. create a small gear size app with jenkins enabled")

        ret_code = common.create_app(self.app_name_small, common.app_types["php"])
        self.assert_equal(ret_code, 0, "App must be created successfully")

        ret_code = common.embed(self.app_name_small, 
                                "add-" + common.cartridge_types["jenkins"])
        self.assert_equal(ret_code, 0, "Jenkins client must be embed successfully")

        #
        # Step 4
        #
        self.info('4.go to jenkins console and check the application builder size in configure job page')
        jenkins_config_output = self.get_jenkins_page("job/%s-build/configure" % self.app_name_small)
        str2find='<select name="builderSize"><option selected="true" value="small">Small</option>'
        self.assert_true(
            jenkins_config_output.find(str2find) != -1,
            "Drop-down list 'Default Builder Size' must contain options 'Small' and 'Medium'"
        )
        #'<select name="builderSize"><option selected="true" value="small">Small </option><option value="medium">Medium</option></select>'

        #
        # Step 5
        #
        self.info("5.do some change and push the changes")
        self.assert_true(
            self.deploy_new_file("./" + self.app_name_small).find("SUCCESS") != -1,
            "Deployment must be successful"
        )

        #
        # Step 6
        #
        if self.get_run_mode() == "DEV":
            self.info("6.create a medium gear size app with jenkins enabled")
            common.change_node_profile("medium")
        ret_code = common.create_app(self.app_name_medium, 
                                     common.app_types["jbossas"], 
                                     gear_size = "medium")
        self.assert_equal(ret_code, 0, "App must be created successfully")

        ret_code = common.embed(self.app_name_medium, 
                                "add-" + common.cartridge_types["jenkins"])
        self.assert_equal(ret_code, 0, "Jenkins client must be embed successfully")

        #
        # Step 7
        #
        self.info("7. go to jenkins console and check the application builder size in configure job page ")
        jenkins_config_output = self.get_jenkins_page("job/%s-build/configure" % self.app_name_medium)
        str2find='<option selected="true" value="medium">Medium</option>'
        self.assert_true(
            jenkins_config_output.find(str2find) != -1,
            "Drop-down list 'Default Builder Size' doesn't contain 'Medium' as default")

        #
        # Step 8
        #
        self.info("8.do some change and push the changes")
        self.assert_true(
            self.deploy_new_file("./" + self.app_name_medium).find("SUCCESS") != -1,
            "Deployment must be successful")

        return self.passed(self.summary)

    def get_jenkins_page(self, path):
        output = StringIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.VERBOSE, 1)
        curl.setopt(pycurl.URL, "https://" + self.jenkins_url + "/" + path)
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
        curl.setopt(pycurl.WRITEFUNCTION, output.write)
        curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
        curl.setopt(pycurl.USERPWD, "%s:%s" % (self.jenkins_username, self.jenkins_password))
        curl.perform()
        return output.getvalue()

    def deploy_new_file(self, git_repo):
        file = open(git_repo + "/" + common.getRandomString(), "w")
        file.write(common.getRandomString())
        file.close()

        deployment_steps = [
            "cd %s" % git_repo,
            "git add .",
            "git commit -a -m testing",
            "git push"
        ]

        return common.command_getstatusoutput(" && ".join(deployment_steps))[1]
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(JenkinsBuilderSize)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
