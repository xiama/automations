"""
"""

import common
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        test_variant = "php"
        self.app_type = common.app_types[test_variant]
        self.app_name = 'my%s%s' % ( test_variant, common.getRandomString(5) )

        common.env_setup()
        self.info("[US1848][runtime][rhc-cartridge] Access embeded mysql server from shell without typing password")

    def finalize(self):
        pass


class MysqlWithoutPassword(OpenShiftTest):
    def test_method(self):

        self.add_step("Creating an application",
            common.create_app,
            function_parameters = [ self.app_name, 
                                    self.app_type, 
                                    self.user_email, 
                                    self.user_passwd, 
                                    False],
            expect_description = "The application must be created successfully",
            expect_return = 0)

        self.add_step("Embedding MySQL cartridge",
            common.embed,
            function_parameters = [ self.app_name, 
                                    "add-" + common.cartridge_types["mysql"] ],
            expect_description = "MySQL cartridge must be embedded successfully",
            expect_return = 0)

        self.add_step("Accessing remote MySQL console",
            common.rhcsh,
            function_parameters = [ self.app_name, 
                                    [ ( 'sendline', 'mysql'), ( 'expect', 'mysql> ') ] ],
            expect_description = "The console must be accessible without password",
            expect_return = 0)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MysqlWithoutPassword)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
