"""
"""
import common, OSConf
import rhtest


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = 'DEV'

    def initialize(self):
        self.info("[US1373][UI][CLI] Pick gear size + [US1908][BusinessIntegration][Marketing]Allotment: Small and medium gears")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = "php"
        self.app_type = common.app_types[self.test_variant]
        self.app_name = "my%s" % ( common.getRandomString() )
        common.env_setup()

    def finalize(self):
        self.gear_and_user_revert()


class GearSize(OpenShiftTest):
    def verify_cgroup_threshold(self, app_name, gear_size):

        thresholds = {
            "small" : { "memory" : 536870912, "swap" : 641728512, "cpu" : 128 },
            "medium" : { "memory" : 1073741824, "swap" : 1178599424, "cpu" : 128 },
            #"large" : { "memory" : 2147483648, "swap" : 2252341248, "cpu" : 128 },  #not supported
        }
        uuid = OSConf.get_app_uuid(app_name)

        if common.get_cgroup_threshold(uuid, "memory", "limit_in_bytes") == thresholds[gear_size]["memory"] and common.get_cgroup_threshold(uuid, "memory", "memsw.limit_in_bytes") == thresholds[gear_size]["swap"] and common.get_cgroup_threshold(uuid, "cpu", "shares") == thresholds[gear_size]["cpu"]:
            return True # Success, it's a Python function
        else:
            return False # Failure

    def gear_and_user_revert(self):
        common.change_node_profile("small")
        common.remove_gearsize_capability('medium') #default

    def test_method(self):

        for gear_size in [ "small", "medium"  ]:
            self.add_step("Changing the node profile to %s" % ( gear_size ),
                common.change_node_profile,
                function_parameters = [ gear_size ],
                expect_description = "Node profile must be changed successfully",
                expect_return = 0)

            self.add_step(
                "Creating application with gear size '%s'" % ( gear_size ),
                common.create_app,
                function_parameters = [ self.app_name + gear_size, 
                                        self.app_type, 
                                        self.user_email, 
                                        self.user_passwd, 
                                        False, 
                                        "./", 
                                        False, 
                                        gear_size ],
                expect_description = "The application must be created successfully",
                expect_return = 0,
                try_count=3,
                try_interval=10)

            self.add_step(
                "Verifying that resource limits are applied for cgroups",
                self.verify_cgroup_threshold,
                function_parameters = [ self.app_name + gear_size, gear_size],
                expect_description = "Cgroup thresholds must match",
                expect_return = True) # This is a Python function

            self.add_step(
                "Destroying the application with gear size '%s'" % ( gear_size ),
                common.destroy_app,
                function_parameters = [ self.app_name + gear_size, self.user_email, self.user_passwd ],
                expect_description = "The application must be destroyed successfully",
                expect_return = 0)

            if gear_size == "small":

                for larger_gear_size in [ "medium" ]:
                    self.add_step(
                        "Creating an application with gear size '%s' without medium_profile capability flag" % ( larger_gear_size ),
                        common.create_app,
                        function_parameters = [ self.app_name + "0" + larger_gear_size, 
                                                self.app_type, 
                                                self.user_email, 
                                                self.user_passwd, 
                                                False, 
                                                "./", 
                                                False, 
                                                larger_gear_size ],
                        expect_description = "The operation must fail",
                        #expect_str = ["Invalid Size"],
                        expect_return = "!0")

                self.add_step(
                    "Setting medium_capability flag",
                    common.add_gearsize_capability,
                    function_parameters = [ 'medium'],
                    expect_description = "gearsize MEDIUM capability must be configured successfully",
                    expect_return = 0)

        self.add_step("Creating an application with an invalid gear size",
            common.create_app,
            function_parameters = [ self.app_name, 
                                    self.app_type, 
                                    self.user_email, 
                                    self.user_passwd, 
                                    False, 
                                    "./", 
                                    False, 
                                    "smallXXXXXX" ],
            expect_description = "The creation of the application must fail",
            expect_return = "!0")

        self.run_steps()
        
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(GearSize)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
