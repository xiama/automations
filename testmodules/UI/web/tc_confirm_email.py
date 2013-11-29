from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import *
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class EmailConfirm(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
        self.confirm_link=config.confirm_url_express
#        baseutils.update_config_file('environment','confirm_url_express',self,confirm_link)
    
    def test_aa_alogin_without_confirm(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.new_user,config.password)
        baseutils.assert_text_equal_by_css(self,"Invalid username or password","div.message.error")
    
    def test_a_confirm_invalid_key(self):
        self.driver.get(config.confirm_url_express_yujzhang_invalidkey)
        baseutils.is_text_equal_by_css(self,"Email confirmation failed","div.message.error")

    def test_b_confirm_without_key(self):
        self.driver.get(config.nokey_confirm_url(self.confirm_link))
        baseutils.is_text_equal_by_css(self,"The confirmation link used is missing the key parameter. Please check your link or try registering again.","div.message.error")    
   
    def test_f_confirm_normal_not_accept_terms(self):
        self.driver.get(config.confirm_url_express_yujzhang)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
        baseutils.assert_text_equal_by_css(self,"Click here to reset your password","p")
        baseutils.assert_value_equal_by_id(self,config.granted_user2[0],"login_input")
#        selenium.focus(selenium,"pwd_input")
        baseutils.input_by_id(self,"pwd_input",config.granted_user2[1])
        baseutils.click_element_by_css_no_wait(self,"input.button")
        baseutils.check_title(self,"OpenShift by Red Hat | Legal terms")
        baseutils.assert_element_present_by_link_text(self,"OpenShift Legal Terms and Conditions")
        baseutils.assert_text_equal_by_css(self,"Sign in","a.sign_in")
        self.driver.get(self.base_url+"/app/")
        baseutils.check_title(self,"OpenShift by Red Hat | Legal terms")

    '''
    def test_g_confirm_normal_login_grant_default(self):
        self.driver.get(config.validemail_confirm_url(self.confirm_link))
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
        baseutils.assert_text_equal_by_css(self,"Click here to reset your password","p")
        baseutils.assert_value_equal_by_id(self,config.email(self.confirm_link),"login_input")
        baseutils.input_by_id(self,"pwd_input",config.password)
        baseutils.click_element_by_css_no_wait(self,"input.button")
        baseutils.check_title(self,"OpenShift by Red Hat | Legal terms")
        baseutils.assert_element_present_by_link_text(self,"OpenShift Legal Terms and Conditions")
        baseutils.assert_text_equal_by_css(self,"Sign in","a.sign_in")
        baseutils.click_element_by_id_no_wait(self,"term_submit")
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.assert_text_equal_by_css(self,"WHAT\'S EXPRESS?","#about > header > h1")
        baseutils.is_element_displayed(self,By.LINK_TEXT,"Quickstart")
        baseutils.is_element_displayed(self,By.LINK_TEXT,"Express Console")
        baseutils.go_to_flex(self)
        baseutils.is_element_displayed(self,By.LINK_TEXT,"Quickstart")
        baseutils.is_element_displayed(self,By.LINK_TEXT,"Flex Console")
    '''    
    def test_c_confirm_invalid_email(self):
        self.driver.get(config.invalidemail_confirm_url(self.confirm_link))
        baseutils.is_text_equal_by_css(self,"Email confirmation failed","div.message.error")

    def test_d_confirm_without_email(self):
        self.driver.get(config.noemail_confirm_url(self.confirm_link))
        baseutils.is_text_equal_by_css(self,"The confirmation link used is missing the emailAddress parameter. Please check your link or try registering again.","div.message.error")
          
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
    #HTMLTestRunner.main()
