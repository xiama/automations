from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import unittest, time, re
import baseutils
import config
import HTMLTestRunner


class ManagePassword(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    def test_a_reset_pwd_with_blank_email(self):
        baseutils.reset_password(self,"")
        baseutils.assert_text_equal_by_css(self,"This field is required.","label.error")
     
    def test_b_reset_pwd_with_invalid_email(self):
        baseutils.reset_password(self,"1234567")
        baseutils.assert_text_equal_by_css(self,"Please enter a valid email address.","label.error")

    def test_c_reset_pwd_with_existing_account(self):
        baseutils.reset_password(self,"xtian+test94@redhat.com")
        baseutils.assert_text_equal_by_css(self,"The information you have requested has been emailed to you at xtian+test94@redhat.com.","div.message.success")       
    
    def test_ca_reset_pwd_without_refresh(self):
        baseutils.reset_password(self,"yujzhang+test@redhat.com")
        time.sleep(5)
        baseutils.assert_element_present_by_xpath(self,"//div[@id='password-reset-form']/form/div/input[@type='hidden']")
        
#        self.driver.assertFalse(self.is_element_present(By.CSS_SELECTOR, "#password-reset-form > form > input.button"))
    
    def test_cb_reset_pwd_with_refresh(self):
        baseutils.reset_password(self,"yujzhant+test@redhat.com")
#        self.driver.assertFalse(self.is_element_present(By.ID,"email_input"))
#        baseutils.assert_element_not_present_by_css(self,"#password-reset-form > form > input.button")
        self.driver.refresh()
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.click_element_by_xpath(self,"//*[@id='lost_password']/p/a")
        time.sleep(2)
        baseutils.assert_element_present_by_id(self,"email_input")
        baseutils.assert_element_present_by_css(self,"#password-reset-form > form > input.button")
    
    def test_d_reset_pwd_with_non_existing_account(self):
        baseutils.reset_password(self,"xtian+94test@redhat.com")
        baseutils.assert_text_equal_by_css(self,"The information you have requested has been emailed to you at xtian+94test@redhat.com.","div.message.success")

        
    def test_e_change_pwd_w_incorrect_oldpwd(self):
        baseutils.change_password(self,config.tochangepwduser[0],config.tochangepwduser[1],"654321",config.tochangepwduser[2],config.tochangepwduser[2])
        baseutils.assert_text_equal_by_css(self,"Your old password was incorrect","div.message.error")
    
    def test_f_change_pwd_w_invalid_newpwd(self):
        baseutils.change_password(self,config.tochangepwduser[0],config.tochangepwduser[1],config.tochangepwduser[1],"12345","12345")
        baseutils.assert_text_equal_by_css(self,"PLEASE ENTER AT LEAST 6 CHARACTERS.","fieldset.confirm > label.error")
    
    def test_g_change_pwd_w_mismatch_newpwd(self):
        baseutils.change_password(self,config.tochangepwduser[0],config.tochangepwduser[1],config.tochangepwduser[1],"123456","1234567")
        baseutils.assert_text_equal_by_css(self,"PLEASE ENTER THE SAME VALUE AGAIN.","fieldset.confirm > label.error")
    
    def test_h_change_pwd_w_blank_oldpwd(self):
        baseutils.change_password(self,config.tochangepwduser[0],config.tochangepwduser[1],"","123456","123456")
        baseutils.assert_text_equal_by_css(self,"THIS FIELD IS REQUIRED.","label.error")
    
    def test_i_change_pwd_normally(self):
        baseutils.change_password(self,config.tochangepwduser[0],config.tochangepwduser[1],config.tochangepwduser[1],config.tochangepwduser[2],config.tochangepwduser[2])
        baseutils.assert_text_equal_by_css(self,"Your password has been successfully changed","div.message.success")
      
    def test_z_login_with_changed_pwd(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.tochangepwduser[0],config.tochangepwduser[2])
        time.sleep(5)
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
        baseutils.assert_element_present_by_link_text(self,"Sign out") 
        _greetings=baseutils.generate_greetings(config.tochangepwduser[0])
        baseutils.assert_element_present_by_link_text(self,_greetings)
        
    def tearDown(self):
        self.driver.quit()
        if len(self.verificationErrors)==1:
           self.assertEqual([''], self.verificationErrors)
        else:self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
