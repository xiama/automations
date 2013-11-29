from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class UserLanding(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    def test_aa_go_to_a_dashboard_nonauth(self):
        self.driver.get(config.dashboard_path)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")

    def test_ab_go_to_b_controlpanel_noauth(self):
        self.driver.get(config.control_panel)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")

    def test_ac_go_to_c_flex_console_noauth(self):
        if config.proxy:
            self.driver.get(config.flex_console)
            baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
        else:pass
        
    def test_d_login_from_registr_page(self):
        self.driver.get(config.registration_page)
        time.sleep(3)
        baseutils.go_to_signin(self)
        baseutils.login_by_window(self,config.granted_user[0],config.granted_user[1])
        time.sleep(3)
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
        
    def test_e_login_from_flex_registr_page(self):
        self.driver.get(config.flex_registration_page)
        time.sleep(3)
        baseutils.go_to_signin(self)
        baseutils.login_by_window(self,config.granted_user[0],config.granted_user[1])
        time.sleep(3)
        baseutils.check_title(self,"OpenShift by Red Hat | Flex")
         
    def test_f_login_from_express_registr_page(self):
        self.driver.get(config.express_registration_page)
        time.sleep(3)
        baseutils.go_to_signin(self)
        baseutils.login_by_window(self,config.granted_user[0],config.granted_user[1])
        time.sleep(3)
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
    '''
    def test_ae_login_from_dashboard(self):
        self.driver.get(config.dashboard_path)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
        baseutils.scroll_bar(self)
        self.driver.refresh()
        baseutils.login_by_form(self,config.granted_user[0],config.granted_user[1])
        time.sleep(2)
        baseutils.assert_text_equal_by_css(self,"Control Panel","section.main > header > h1")
        
    def test_af_login_from_control_panel(self):
        self.driver.get(config.control_panel)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
        baseutils.scroll_bar(self)
        self.driver.refresh()
        baseutils.login_by_form(self,config.granted_user[0],config.granted_user[1])
        time.sleep(2)
        baseutils.assert_text_equal_by_css(self,"Control Panel","section.main > header > h1")
     
    def test_c_login_from_flex_console(self):
        if config.proxy:
            self.driver.get(config.flex_console)
            baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
            baseutils.scroll_bar(self)
            self.driver.refresh()
            baseutils.login_by_form(self,config.granted_user[0],config.granted_user[1])
            self.assertTrue(config.flex_console in self.driver.current_url,"flex console is not right")
        else:pass
    '''    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        

if __name__ == "__main__":
    unittest.main()
    #HTMLTestRunner.main()
