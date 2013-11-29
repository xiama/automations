#
#  File name: PreStartScript.py
#  Date:      2012/07/26 15:03
#  Author:    mzimen@redhat.com
#

import common
import rhtest
import OSConf
import re


class OpenShiftTest(rhtest.Test):
    ITEST = ["DEV"]

    def initialize(self):
        self.info("[US2008][RT] Check running pre-start script")
        self.timeout=5

        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        self.info("VARIANT: %s"%self.test_variant)

        try:
            self.cart_variant = self.config.tcms_arguments['cartridge']
        except:
            self.cart_variant = 'mysql'
        self.info("DB VARIANT: %s"%self.cart_variant)

        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        self.custom_app_vars={
            "QE_ID_APP": "$(id)",
            "TESTING_STRING_%s"%self.test_variant: 1,
            "QE_APP": 1
        }

        self.custom_cart_vars={
            "QE_ID_CART": "$(id)",
            "MYSQL_PS1": "qashift ",
            "TESTING_STRING_%s"%self.cart_variant: 1,
            "sleep": "$(sleep %s)"%self.timeout,
            "QE_CART": 1
        }
        dict2list = lambda dic: [(k, v) for (k, v) in dic.iteritems()]

        self.custom_app_commands= "\n".join(
                map(lambda item: ("export %s=%s"%(item[0],item[1])), dict2list(self.custom_app_vars)))
        self.custom_cart_commands= "\n".join(
                map(lambda item: ("export %s=%s"%(item[0],item[1])), dict2list(self.custom_cart_vars)))
        #self.custom_cart_commands += "\nblabla"

        self.hook_app_file = "%s/.openshift/action_hooks/pre_start_%s"%(
                self.app_name, common.app_types[self.test_variant])
        self.hook_cart_file = "%s/.openshift/action_hooks/pre_start_%s"%(
                self.app_name, common.cartridge_types[self.cart_variant])

        common.env_setup()


    def finalize(self):
        pass


class PreStartScript(OpenShiftTest):
    def test_method(self):

        self.add_step("Create an app", 
                common.create_app,
                function_parameters=[self.app_name,
                        common.app_types[self.test_variant],
                        self.user_email, 
                        self.user_passwd, 
                        True],
                        expect_return=0)

        self.add_step("Embed a cartridge", 
                common.embed,
                function_parameters=[self.app_name,
                        "add-%s"%common.cartridge_types[self.cart_variant], 
                        self.user_email, 
                        self.user_passwd],
                expect_return=0)

        self.add_step("Add pre-start script for %s"%self.test_variant,
                "echo '%s' > %s"%
                        (self.custom_app_commands, self.hook_app_file),
                expect_return=0)

        self.add_step("Put the testing script online",
            self.upload_checker_file,
            expect_return = True)

        #for app only
        self.add_step("Git add/commit/push [App+Cartridge]",
                "cd %s && git add . && git commit -m new_files -a && git push"%
                        (self.app_name),
                expect_description = "Only app hook should be executed",
                expect_str = [ 
#                        "blabla: command not found", 
                        "remote: Done"],
                expect_return=0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            try_count=3,
            expect_return=0)

        self.add_step("Check the variables remotely [APP]",
            self.check_variables,
            function_parameters=[self.custom_app_vars.keys()],
            expect_description = "All of the variables must be in rhcsh shell.",
            expect_return=True)

        #add cartridge hook
        self.add_step("Add pre-start script for %s"%self.cart_variant,
                "echo '%s'> %s"%
                        (self.custom_cart_commands, self.hook_cart_file),
                expect_return=0)

        #for both of them...
        self.add_step("Git add/commit/push [BOTH]",
                "cd %s && git add . && git commit -m update_hooks -a && git push"%
                        (self.app_name),
                expect_description = "Both hooks should be executed",
                expect_str = [
                        "remote: Done"],
                expect_return=0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            try_count=3,
            expect_return=0)

        self.add_step("Check the variables remotely [APP]",
            self.check_variables,
            function_parameters=[self.custom_app_vars.keys()],
            expect_description = "All of the app+cart variables must be in rhcsh shell.",
            expect_return=True)

        #only for CART, no PHP
        self.add_step("Remove APP pre-start script",
            "cd %s && git rm -f %s "%(self.app_name, self.hook_app_file.replace(self.app_name,".")),
            expect_return=0)

        self.add_step("Git add/commit/push [CART]",
            "cd %s && git add . && git commit -m update_hooks -a && git push"%
                    (self.app_name),
            expect_description = "Only cartridge hook should be loaded",
            expect_str = ["remote: Done"],
            expect_return=0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[self.app_name],
            try_count=3,
            expect_return=0)

        self.add_step("Check the output remotely",
            common.run_remote_cmd_as_root,
            expect_description = "`Timeout' warning message should be present in the output of libra start",
            function_parameters=["/sbin/service libra restart | grep Timeout"],
            expect_return=0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            function_parameters=[],
            expect_return=0)

        self.add_step("Check the variables remotely [APP]",
            self.check_variables,
            function_parameters=[self.custom_app_vars.keys()],
            expect_description = "All of the app+cart variables must be in rhcsh shell.",
            expect_return=True)

        self.custom_app_commands += "\nblabla"

        self.add_step("Add pre-start script for %s"%self.test_variant,
            "echo '%s' > %s"%
                    (self.custom_app_commands, self.hook_app_file),
            expect_return=0)

        self.add_step("Git add/commit/push [APP+ERROR]",
            "cd %s && git add . && git commit -m update_hooks -a && git push"%
                    (self.app_name),
            expect_description = "Only cartridge hook should be loaded",
            expect_str = [
                    "blabla: command not found", 
                    "remote: Done"],
            expect_return=0)

        self.add_step("Check the app url",
            common.check_web_page_output,
            expect_description = "App shouldn't be accessible because of error",
            function_parameters=[self.app_name],
            expect_return=1)

        self.add_step("Check the variables remotely [APP]",
            self.check_variables,
            function_parameters=[self.custom_app_vars.keys()],
            expect_description = "Shouldn't be accessible.",
            expect_return=False)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)

    def check_variables(self, *vars_to_check):
        app_url = OSConf.get_app_url(self.app_name)
        output = common.fetch_page(app_url+"/checker.php")
        for arr in vars_to_check:
            for var in arr:
                obj = re.search(r"%s="%var, output)
                if not obj:
                    self.error("Unable to find %s in environemnt"%var)
                    return False
        return True

    def upload_checker_file(self):
        fname = "%s/php/checker.php"%self.app_name
        checker = """
<?php
echo "List of all \$_ENV variables\n";

foreach ($_ENV as $key => $val) {
    echo "$key=$val";
}
?>
        """
        try:
            f = open(fname, "wb")
            f.write(checker)
            f.close()
        except:
            return False
        return True

class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PreStartScript)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of PreStartScript.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
