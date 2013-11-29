#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-07-23

[US619][Runtime][rhc-cartridge]git submodule support
https://tcms.engineering.redhat.com/case/138336/
"""
import os
import common
import OSConf
import rhtest
import random


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework

    def initialize(self):
        valid_variants = ["jbosseap", "php", "ruby", "ruby-1.9", "python", "wsgi", "perl", "diy", "nodejs"]
        random.seed()
        rand = int(random.random() * len(valid_variants))
        self.summary = "[US619][Runtime][rhc-cartridge]git submodule support"
        self.app_name = "submodule" + common.getRandomString(4)
        self.app_type = common.app_types[valid_variants[rand]]
        self.git_repo = "./%s" % (self.app_name)
        self.submodule_name = "wolfcms-example"
        self.submodule_repo = "https://github.com/openshift/%s.git" % (self.submodule_name)
        common.env_setup()

    def finalize(self):
        pass


class GitSubmoduleTest(OpenShiftTest):
    CODE = """#!/usr/bin/env python
import os
import re
import sys

git_repo = os.path.abspath(os.environ['OPENSHIFT_REPO_DIR'])
# Read from .gitmodules
try:
    f = file('%s/.gitmodules' % (git_repo), 'r')
    s = f.read()
    f.close()
except:
    print('Failed to read %s/.gitmodules' % (git_repo))
    sys.exit(1)
# Search for submodule's relative path
try:
    submodule_path = re.search(r'(?<=path = ).+$', s, re.M).group(0)
except:
    print('Failed to find submodule dir path in .gitmodules')
    sys.exit(2)
# Check if submodule's dir is empty
path = '/'.join([git_repo, submodule_path])
print('The path of the submodule is:' + path)
try:
    lst = os.listdir(path)
except:
    print('submodule dir %s does not exist' % path)
    sys.exit(3)
if len(lst) == 0:
    print('Test Result: FAIL. git submodule update is not executed successfully on server')
    sys.exit(3)
else:
    print('Test Result: PASS. git submodule update is executed successfully on server')
    sys.exit(0)"""

    def test_method(self):
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App creation failed")
        # Add an public git repo as a submodule of the app
        cmd = "cd %s && git submodule add %s" % (self.git_repo, self.submodule_repo)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.debug(output)
        self.assert_equal(ret, 0, "Failed to add submodule")
        # Modify .openshift/action_hooks/pre_build
        try:
            f = file("%s/.openshift/action_hooks/pre_build" % (self.git_repo), "w")
            f.write(GitSubmoduleTest.CODE)
            f.close()
        except IOError:
            return self.failed("Failed to write code to %s/.openshift/action_hooks/pre_build" % (self.git_repo))
        except:
            self.error("Unknown error")
            import traceback
            traceback.print_exc()
            return self.failed("%s failed" % self.__class__.__name__)
        # Git push all the changes
        cmd = "cd %s && git add . && git commit -amt && git push" % (self.git_repo)
        ###expected_output = "Test Result: PASS. git submodule update is executed successfully on server"
        (ret, output) = common.command_getstatusoutput(cmd)
        self.debug(output)
        self.assert_equal(ret, 0, "Git push failed")
        ###if output.find(expected_output) == -1:
        ###    return self.failed("%s failed" % self.__class__.__name__)
        # Git clone the app's repo and pull down the submodule
        cmd = "git clone %s %s-clone && cd %s-clone && git submodule init && git submodule update" % (OSConf.get_git_url(self.app_name), self.app_name, self.app_name)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.debug(output)
        self.assert_equal(ret, 0, "Failed to git clone the repo and pull down submodule")
        # Check if the submodule is pulled down
        self.info("Checking dir: %s-clone/%s" % (self.app_name, self.submodule_name))
        try:
            lst = os.listdir("%s-clone/%s" % (self.app_name, self.submodule_name))
        except OSError:
            return self.failed("Failed to list files under %s-clone/%s. The dir may not exist" % (self.git_repo, self.submodule_name))
        except:
            self.error("Unknown error")
            import traceback
            traceback.print_exc()
            return self.failed("%s failed" % self.__class__.__name__)
        if len(lst) == 0:
            return self.failed("The git submodule isn't pulled down")
        else:
            self.info("The git submodule is successfully pulled down")
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(GitSubmoduleTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
