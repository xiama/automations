from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class LoginPage(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)

    def test_check_login_form(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.assert_element_present_by_css(self,"a.password_reset.more")
 #       baseutils.is_element_hidden(self,By.ID,"login-form")
        baseutils.click_element_by_css_no_wait(self,"a.sign_up.more")
        time.sleep(5)
        baseutils.is_element_displayed(self,By.ID,"signup")
        baseutils.click_element_by_css_no_wait(self,"#signup > a.close_button > img")
        time.sleep(5)
        baseutils.is_element_hidden(self,By.ID,"signup")
        #baseutils.check_title(self,"OpenShift by Red Hat | Sign up for OpenShift")
#        baseutils.assert_text_equal_by_css(self,"Need to Register instead?","#register > h2")

    def test_login_invalid_user(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,"xtian",config.password)
        baseutils.assert_text_equal_by_css(self,"Invalid username or password","div.message.error")


    def test_login_without_user(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,"",config.password)
        baseutils.assert_text_equal_by_css(self,"This field is required.","label.error")

    def test_login_without_pwd(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],"")
        baseutils.assert_text_equal_by_css(self,"This field is required.","label.error")


    def test_login_granted_user(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        time.sleep(5)
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
        baseutils.assert_element_present_by_link_text(self,"Sign out") 
        _greetings=baseutils.generate_greetings(config.granted_user[0])
        baseutils.assert_element_present_by_link_text(self,_greetings)


    def test_login_sql_bypass(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,"xtian+0@redhat.com or 1=1",config.password)
        baseutils.assert_text_equal_by_css(self,"Invalid username or password","div.message.error")



    def test_login_session_existing(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        time.sleep(5)
 #       baseutils.wait_for_ajax(self)
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
  #      baseutils.assert_element_present_by_link_text(self,"Get started!")
        baseutils.assert_element_present_by_link_text(self,"Sign out") 
        _greetings=baseutils.generate_greetings(config.granted_user[0])
        baseutils.assert_element_present_by_link_text(self,_greetings)
        baseutils.go_to_express(self)
        baseutils.assert_element_present_by_link_text(self,"Sign out")
    '''
    def test_login_from_express_regisra_link(self):
        self.driver.get(config.confirm_url_express_yujzhang)
#        print config.confirm_url_express_yujzhang
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
#        baseutils.assert_text_equal_by_css(self,"Click here to reset your password","p")
        baseutils.assert_value_equal_by_id(self,config.email(config.confirm_url_express_yujzhang),"login_input")
        baseutils.input_by_id(self,"pwd_input",config.granted_user2[1])
        print config.granted_user2[1]
        baseutils.scroll_by(self)
        baseutils.click_element_by_css_no_wait(self,"input.button")
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.assert_text_equal_by_css(self,"WHAT\'S EXPRESS?","#about > header > h1")
   
    
    def test_login_from_flex_regisra_link(self):
        self.driver.get(config.confirm_url_flex)
        baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
#        baseutils.assert_text_equal_by_css(self,"Click here to reset your password","p")
        baseutils.assert_value_equal_by_id(self,config.email(config.confirm_url_flex),"login_input")
        baseutils.input_by_id(self,"pwd_input",config.password)
        baseutils.scroll_by(self)
        baseutils.click_element_by_css_no_wait(self,"input.button")
        baseutils.check_title(self,"OpenShift by Red Hat | Flex")
        baseutils.assert_text_equal_by_css(self,"WHAT\'S FLEX?","#about > header > h1")
    '''
    def test_login_logout_back(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
      #  baseutils.assert_element_present_by_link_text(self,"Get started!")
        _greetings=baseutils.generate_greetings(config.granted_user[0])
        baseutils.assert_element_present_by_link_text(self,_greetings)
        baseutils.assert_element_present_by_link_text(self,"Sign out")
        baseutils.logout(self)
        baseutils.go_back(self)
        self.driver.refresh()
        baseutils.assert_element_present_by_link_text(self,"Sign in")

    def test_login_cookie_deleted(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        time.sleep(5)
 #       baseutils.wait_for_ajax(self)
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
     #   baseutils.assert_element_present_by_link_text(self,"Get started!")
        _greetings=baseutils.generate_greetings(config.granted_user[0])
        baseutils.assert_element_present_by_link_text(self,_greetings)
        baseutils.assert_element_present_by_link_text(self,"Sign out")
        self.driver.delete_cookie("_rhc_session")
        self.driver.delete_cookie("rh_sso")
        self.driver.refresh()
        baseutils.assert_element_present_by_link_text(self,"Sign in")
        

        
    def tearDown(self):
        self.driver.quit()
        if len(self.verificationErrors)==1:
           self.assertEqual([''], self.verificationErrors)
        else:self.assertEqual([], self.verificationErrors)
           
        '''
        if self.verificationErrors != [] or self.verificationErrors != [''] :
            for error in self.verificationErrors:
                if error.strip()!=[''] or error.strip()!=[]:
                   self.fail(error.strip())
        '''
      
#        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
    #HTMLTestRunner.main()
