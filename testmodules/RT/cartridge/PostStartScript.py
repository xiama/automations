#
#  File name: PostStartScript.py
#  Date:      2012/07/26 11:03
#  Author:    mzimen@redhat.com
#

import common
import rhtest


class OpenShiftTest(rhtest.Test):
    ITEST = ["DEV"]

    def initialize(self):
        self.info("[US2008][RT] Check running post-start script")
        self.timeout = 95

        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'

        try:
            self.cart_variant = self.config.tcms_arguments['cartridge']
        except:
            self.cart_variant = 'mysql'
        self.info("VARIANT: %s"%self.test_variant)
        self.info("DB VARIANT: %s"%self.cart_variant)

        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        self.custom_app_commands= "#!/bin/sh\n\nid; echo TESTING_STRING_%s; "%(
                self.test_variant)
        self.custom_cart_commands= "#!/bin/sh\n\nid; echo TESTING_STRING_%s; "%(
                self.cart_variant)
        self.hook_app_file = "%s/.openshift/action_hooks/post_start_%s"%(
                self.app_name, common.app_types[self.test_variant])
        self.hook_cart_file = "%s/.openshift/action_hooks/post_start_%s"%(
                self.app_name, common.cartridge_types[self.cart_variant])

        common.env_setup()


    def finalize(self):
        #just for the case if something interrupts restarting...
        common.run_remote_cmd_as_root("/sbin/service libra start")


class PostStartScript(OpenShiftTest):
    def test_method(self):

        self.add_step("Create an app", 
                common.create_app,
                function_parameters=[self.app_name,
                        common.app_types[self.test_variant],
                        self.user_email, 
                        self.user_passwd, 
                        True],
                        expect_return = 0)
        self.add_step("Embed a cartridge", 
                common.embed,
                function_parameters=[self.app_name,
                        "add-%s"%common.cartridge_types[self.cart_variant], 
                        self.user_email, 
                        self.user_passwd],
                expect_return = 0)

        self.add_step("Add post-start script for %s"%self.test_variant,
                "echo '%s' > %s"%
                        (self.custom_app_commands, self.hook_app_file),
                expect_return = 0)

        self.add_step("Chmod +x for our scripts",
                "chmod +x %s/.openshift/action_hooks/post_start_*"%
                        (self.app_name),
                expect_return = 0)

        #for app only
        self.add_step("Git add/commit/push [App+Cartridge]",
                "cd %s && git add . && git commit -m new_files -a && git push"%
                        (self.app_name),
                expect_description = "Only app hook should be executed",
                expect_str = ["remote: uid=", 
                        "remote: TESTING_STRING_%s"%self.test_variant, 
                        "remote: Done"],
                unexpect_str = [
                        "remote: uid=0"], #must not be root
                expect_return = 0)

        #add cartridge hook
        self.add_step("Add post-start script for %s"%self.cart_variant,
                "echo '%s'> %s"%
                        (self.custom_cart_commands, self.hook_cart_file),
                expect_return = 0)

        self.add_step("Chmod +x for our scripts",
                "chmod +x %s/.openshift/action_hooks/post_start_*"%
                        (self.app_name),
                expect_return = 0)

        #for both of them...
        self.add_step("Git add/commit/push [BOTH]",
                "cd %s && git add . && git commit -m update_hooks -a && git push"%
                        (self.app_name),
                expect_description = "Both hooks should be executed",
                expect_str = ["remote: uid=", 
                        "remote: TESTING_STRING_%s"%self.test_variant, 
                        "remote: TESTING_STRING_%s"%self.cart_variant, 
                        "remote: Done"],
                unexpect_str = [
                        "remote: uid=0"], #must not be root
                expect_return = 0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            try_count=3,
            expect_return = 0)

        #only for CART, no PHP
        self.add_step("Remove PHP post-start script",
                "cd %s && git rm -f %s "%(self.app_name, self.hook_app_file.replace(self.app_name,".")),
                expect_return = 0)

        self.add_step("Git add/commit/push",
                "cd %s && git add . && git commit -m update_hooks -a && git push"%
                        (self.app_name),
                expect_description = "Only cartridge hook should be executed",
                expect_str = ["remote: uid=", 
                        "remote: TESTING_STRING_%s"%self.cart_variant, 
                        "remote: Done"],
                unexpect_str = [
                        "remote: uid=0", #must not be root
                        "remote: TESTING_STRING_%s"%self.test_variant], 
                expect_return = 0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            try_count=3,
            expect_return = 0)
        #
        #check the timeout
        #
        self.custom_app_commands += "sleep %s"%(self.timeout)
        self.custom_cart_commands += "sleep %s"%(self.timeout)
        self.add_step("Add post-start script for %s"%self.test_variant,
                "echo '%s' > %s"%
                        (self.custom_app_commands, self.hook_app_file),
                expect_return = 0)

        self.add_step("Add post-start script for %s"%self.cart_variant,
                "echo '%s'> %s"%
                        (self.custom_cart_commands, self.hook_cart_file),
                expect_return = 0)

        self.add_step("Chmod +x for our scripts",
                "chmod +x %s/.openshift/action_hooks/post_start_*"%
                        (self.app_name),
                expect_return = 0)

        self.add_step("Git add/commit/push [TIMEOUT+BOTH]",
                "cd %s && git add . && git commit -m update_hooks -a && git push"%
                        (self.app_name),
                expect_description = "Both hooks should be executed",
                expect_str = ["remote: uid=", 
                        "remote: TESTING_STRING_%s"%self.test_variant, 
                        "remote: TESTING_STRING_%s"%self.cart_variant, 
                        "remote: Done"],
                unexpect_str = ["remote: uid=0"], #must not be root
                expect_return = 0)


        self.add_step("Check the output remotely",
            common.run_remote_cmd_as_root,
            expect_description = "`Timeout' warning message should be present in the output of libra start",
            function_parameters = ["/sbin/service libra restart | grep Timeout"],
            expect_return = 0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            expect_return = 0)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PostStartScript)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of PostStartScript.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
