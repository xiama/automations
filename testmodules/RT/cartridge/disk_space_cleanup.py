"""
Attila Nagy
anagy@redhat.com
Feb 23, 2012

[US1107][rhc-cartridge] Disk space cleanup using rhc app tidy
https://tcms.engineering.redhat.com/case/122527/
"""

import os
import common
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.summary = "[US1107][rhc-cartridge] Disk space cleanup using rhc app tidy"
        try:
            self.test_variant = self.config.test_variant
        except:
            self.info("Missing OPENSHIFT_test_name, used `jbossea` as default")
            self.test_variant = 'jbosseap'

        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.cart = common.type_to_cart(self.app_type)

        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))


class DiskSpaceCleanup(OpenShiftTest):

    def test_method(self):
        self.info(self.summary)

        self.add_step(
                'Creating an application',
                common.create_app,
                function_parameters = [ self.app_name, 
                                        self.app_type, 
                                        self.config.OPENSHIFT_user_email, 
                                        self.config.OPENSHIFT_user_passwd, 
                                        False ],
                expect_description = 'The app should be created successfully',
                expect_return = 0)

        self.add_step(
                "Visiting the application's URL (to generate access.log file)",
                common.check_web_page_output,
                function_parameters = [ self.app_name, 'health', '1' ],
                expect_description = 'The application must be alive',
                expect_return = 0)

        self.add_step(
                "Running command 'tidy' and checking the result",
                self.tidy_and_comparation,
                function_parameters = [ self.app_name],
                expect_description = "Temporary files must be successfully created and disappeared after running 'tidy'",
                expect_return = 1) # It's a Python function

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)

    def tidy_and_comparation(self, app_name):
        """
        This functions returns 1 if the comperation was successfull ( new_size < original_size)
        Returns 0 otherwise
        """
        # Step 1: Getting the original repo size
        original_size = common.get_git_repo_size(app_name)

        # Step 2: Creating temporary files, the name is a random string
        files = list()
        random_name = common.getRandomString()

        files.append(r"/tmp/%s.txt" % ( random_name ))
        files.append(r"${OPENSHIFT_GEAR_DIR}/tmp/%s.txt" % ( random_name ))

        if self.test_variant == 'jbosseap':
            files.append(r"${OPENSHIFT_%s_LOG_DIR}/%s.txt" % ( self.cart, random_name ))

        elif self.test_variant in ("ruby","rack"):
            files.append(r"${OPENSHIFT_REPO_DIR}/tmp/%s.txt" % ( random_name ))

        ( ret_code, ret_output ) = common.run_remote_cmd(app_name, 
                                   "set -x && " + ' && '.join(map(( lambda x: "touch " + x), files)))
        if ret_code != 0:
            print "Failed to create temporary file"
            return 0

        # Step 3: Running command 'tidy'
        ( ret_code, ret_output ) = common.command_getstatusoutput("rhc app tidy %s -l %s -p '%s' %s " % (app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS))
        if ret_code != 0:
            print "Failed to run command 'tidy'"
            return 0
        
        # Step 4: Checking Git repo size
        new_size = common.get_git_repo_size(app_name)

        if int(new_size) < int(original_size):
            print "OK. Git repo size is smaller"
        else:
            print "Git repo size must be smaller"
            return 0

        # Step 5: Checking the existence of the temporary files
        ( ret_code, ret_output ) = common.run_remote_cmd(
                                        app_name,
                                        "set -x && " + ' && '.join(map(( lambda x: 'test ! -f %s'  + x ), files))
        )
        if ret_code != 0:
            print "Existing temporary files after running the command 'tidy'..."
            return 0

        # Step 6: Checking access log files
        (ret_code, ret_output) = common.run_remote_cmd(app_name, r"test \! -f ${OPENSHIFT_%s_LOG_DIR}access.log*" % (self.cart))
        if ret_code != 0:
            print "Existing access.log file in OPENSHIFT_%s_LOG_DIR" % (self.cart)
            return 0

        # Otherwise everything is OK
        return 1


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DiskSpaceCleanup)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
