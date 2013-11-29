import rhtest
import database
import time
import autoweb


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = "UI"

    def initialize(self):
        #tb = self.config.testbed
        self.ip = self.config.instance_info['ip']
        self.info("IP: %s" % self.ip)
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        self.web = self.config.web
        

    def finalize(self):
        self.info("Closing webdriver")
        print self.driver
        self.web.driver.close()

class LoginPage(OpenShiftTest):
    def test_check_login_form(self):
        self.web.go_to_home()
        self.web.go_to_signin()
        self.web.assert_element_present_by_link_text("Forgot your password?")
        self.web.assert_element_present_by_link_text("create an account")
        self.web.assert_element_present_by_css("input.btn")
        
    def test_login_invalid_user(self):
        """ test invalid user """
        self.web.go_to_home()
        self.web.go_to_signin()
        self.web.login("baduser", "vostok08")
        self.web.assert_text_equal_by_css("Invalid username or password","div.alert.alert-error")

    def test_method(self):
        errorCount = 0
        self.test_check_login_form()
        self.test_login_invalid_user()
        #web = self.config.web
        # test_check_login_form
        #web.go_to_home()
        #web.go_to_signin()

        self.info("Test: Check login form")

        if errorCount:
            return self.failed("LoginPage test failed.")
        else:
            return self.passed("LoginPage test passed.")
   
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(LoginPage)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
