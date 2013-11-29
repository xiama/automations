from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import random
import HTMLTestRunner


class CreateApplication(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        self.exist_app="mypythonapp1"
        baseutils.initiate(self)



    def get_domain_name(self):
        return self.driver.find_element_by_css_selector("div.current.domain").text

    def generate_app_name(self):
        i=random.uniform(1,10)
        app_name="app"+str(i)[5:10]
        return app_name

    def get_cartridge_list(self,id_name="express_app_cartridge"):
        select=self.driver.find_element_by_id(id_name)
        options = select.find_elements_by_tag_name("option")
        return options

    def assert_app_url(self,appname):
        _domain_name=self.get_domain_name()
        _app_url="http://"+appname+"-"+_domain_name+"."+config.libra_server
        print "========================="
        print _app_url
        baseutils.assert_element_present_by_link_text(self,_app_url)
        #baseutils.assert_text_equal_by_partial_link_text(self,_app_url,"http://"+appname+"-")

    def assert_app_url_after_change(self,appname,_new_domain):
        _app_url="http://"+appname+"-"+_new_domain+"."+config.libra_server
        print "========================="
        print _app_url
        baseutils.assert_element_present_by_link_text(self,_app_url)


    def create_application(self,app_name,cartridge_type):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.domainuser[0],config.domainuser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        #VerifyDomainExist
        time.sleep(10)
       # baseutils.assert_element_present_by_id(self,"show_namespace")
       # self.driver.refresh()
       # self.driver.refresh()
        baseutils.wait_element_present_by_id(self,"express_app_app_name")
        self.driver.find_element_by_id("express_app_app_name").clear()
        self.driver.find_element_by_id("express_app_app_name").send_keys(app_name)
        cartridges=self.get_cartridge_list()
        self.assertTrue(len(cartridges) >= 5)
        for car in cartridges:
            if car.text == cartridge_type or car.text.find(cartridge_type) != -1:
               car.click()
               break
        #baseutils.click_element_by_xpath(self,"//body/section/div/div[2]/div[2]/div[1]/div[1]/form[1]/fieldset[1]/ol[1]/li[1]/input[@id='express_app_submit']")
        #self.driver.find_element_by_id("express_app_submit").click()
        time.sleep(2)
        baseutils.scroll_bar(self)
        time.sleep(1)
        baseutils.click_element_by_id(self,"express_app_submit")

    def delete_application(self):
#        baseutils.go_to_home(self)
        time.sleep(4)
#        baseutils.go_to_signin(self)
#        baseutils.login(self,config.domainuser[0],config.domainuser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        appname=self.driver.find_element_by_xpath("//div[@id='app_list_container']/ul/li/header/h1").text
        print appname
        baseutils.click_element_by_link_text(self,"Delete...")   
#        baseutils.assert_element_present_by_xpath(self,"//div[@id='app_list_container']/ul/li/div/div/a")
#        self.driver.find_element_by_xpath("//div[@id='app_list_container']/ul/li/div/div/a").click()       
        time.sleep(3)
        baseutils.wait_element_present_by_xpath(self,"//form[@id='"+appname+"_delete_form']/input[3]")
        baseutils.click_element_by_xpath(self,"//form[@id='"+appname+"_delete_form']/input[3]")
        time.sleep(15)
        baseutils.wait_element_not_present_by_xpath(self,"//div[@id='app_list_container']/ul/li[5]/header/h1")
      
    def test_a_create_app_with_blank_appname(self):
        self.create_application("","jbossas")
        time.sleep(2)
        baseutils.assert_contain_text_by_xpath(self,"THIS FIELD IS REQUIRED.","//li[@id='express_app_app_name_input']/label[2]")

        #baseutils.assert_text_equal_by_css(self,"App name is invalid; App name can't be blank","div.message.error")
        
    def test_b_create_app_with_nonalphnum_appname(self):
        self.create_application("app_1","jbossas-7.0")
        time.sleep(2)
        baseutils.assert_text_equal_by_xpath(self,"ONLY LETTERS AND NUMBERS ARE ALLOWED",".//li[@id='express_app_app_name_input']/label[2]")
    
    
    def test_c_create_app_with_blank_cart(self):
        self.create_application("myapp","")
        time.sleep(2)
        baseutils.assert_contain_text_by_xpath(self,"THIS FIELD IS REQUIRED.","//li[@id='express_app_cartridge_input']/label[2]")
   
    
    def test_d_create_app_with_blacklist_appname(self):
        self.create_application("openshift","perl-5.10")
        time.sleep(2)
        baseutils.assert_text_equal_by_css(self,"App name openshift is not a permitted app name","div.error.message")
    
    def test_e_create_app_with_blankapp_blankcart(self):
        self.create_application("","")
        time.sleep(2)
        baseutils.assert_contain_text_by_xpath(self,"THIS FIELD IS REQUIRED.","//li[@id='express_app_app_name_input']/label[2]")
        baseutils.assert_contain_text_by_xpath(self,"THIS FIELD IS REQUIRED.","//li[@id='express_app_cartridge_input']/label[2]")

        #baseutils.assert_text_equal_by_css(self,"App name is invalid; App name can't be blank; Cartridge can't be blank; Cartridge is not a valid cartridge.","div.message.error")        
    
    def test_f_create_jboss_app(self):
        _appname=self.generate_app_name()
        self.create_application(_appname,"jbossas")
        time.sleep(20)
       # baseutils.is_element_displayed(self,By.ID,"spinner")
       # baseutils.assert_text_equal_by_id(self,"Creating your app...","spinner-text")
        self.assert_app_url(_appname)
       # if baseutils.is_text_displayed (self,"We're sorry, this operation has timed out. It is possible that it was succfully completed, but we are unable to verify it.","div.error.message"):
        #    pass
       # else:
       # baseutils.assert_contain_text_by_id(self,"using Java with JBossAS 7 on OpenShift:","spinner-text")
       # baseutils.click_element_by_css_no_wait(self,"a.close > img")
       # baseutils.wait_element_not_displayed_by_id(self,"spinner")
        self.assert_app_url(_appname)
        self.delete_application()
    
    def test_g_create_perl_app(self):
        _appname=self.generate_app_name()
        self.create_application(_appname,"perl")
        time.sleep(20)
        #baseutils.is_element_displayed(self,By.ID,"spinner")
        #baseutils.assert_text_equal_by_id(self,"Creating your app...","spinner-text")
        #time.sleep(5)
        #if baseutils.is_text_displayed (self,"We're sorry, this operation has timed out. It is possible that it was succfully completed, but we are unable to verify it.","div.error.message"):
        #    pass
        #else:
        #baseutils.assert_contain_text_by_id(self,"OpenShift Perl app","spinner-text")
        #baseutils.click_element_by_css_no_wait(self,"a.close > img")
        #baseutils.wait_element_not_displayed_by_id(self,"spinner")
        self.assert_app_url(_appname)
        self.delete_application()
    
    def test_h_create_ruby_app(self):
        _appname=self.generate_app_name()
        self.create_application(_appname,"rack")
        time.sleep(20)
        #baseutils.is_element_displayed(self,By.ID,"spinner")
        #baseutils.assert_text_equal_by_id(self,"Creating your app...","spinner-text")
        #time.sleep(5)
        #if self.driver.find_element_by_css_selector("div.error.message").is_displayed():
         #   self.driver.refresh()
        #else:
           #baseutils.assert_contain_text_by_id(self,"popular Ruby frameworks on OpenShift","spinner-text")
            #baseutils.click_element_by_css_no_wait(self,"a.close > img") 
        #if baseutils.is_text_displayed (self,"We're sorry, this operation has timed out. It is possible that it was succfully completed, but we are unable to verify it.","div.message.error"):
        #    pass
        #else:
        #baseutils.assert_contain_text_by_id(self,"popular Ruby frameworks on OpenShift","spinner-text")
        #baseutils.click_element_by_css_no_wait(self,"a.close > img")
        #baseutils.wait_element_not_displayed_by_id(self,"spinner")
        self.assert_app_url(_appname)
        self.delete_application()
    
    def test_i_create_python_app(self):
        _appname=self.generate_app_name()
       # self.exist_app=_appname
        self.create_application(_appname,"wsgi")
        time.sleep(20)
        #baseutils.is_element_displayed(self,By.ID,"spinner")
        #baseutils.assert_text_equal_by_id(self,"Creating your app...","spinner-text")
        #time.sleep(5)baseutils.click_element_by_xpath(self,"//div[@id='domains']/div[2]/div[2]/div/a")
        #if baseutils.is_text_displayed (self,"We're sorry, this operation has timed out. It is possible that it was succfully completed, but we are unable to verify it.","div.message.error"):
        #    pass
        #else:
        #baseutils.assert_contain_text_by_id(self,"deploy popular python frameworks","spinner-text")
        #baseutils.click_element_by_css_no_wait(self,"a.close > img")
        #baseutils.wait_element_not_displayed_by_id(self,"spinner")
        self.assert_app_url(_appname)
        self.delete_application()

    
    def test_j_create_php_app(self):
        _appname=self.generate_app_name()
        self.create_application(_appname,"php")
        time.sleep(20)
        #baseutils.is_element_displayed(self,By.ID,"spinner")
        #baseutils.assert_text_equal_by_id(self,"Creating your app...","spinner-text")
        #time.sleep(5)
        #if baseutils.is_text_displayed (self,"We're sorry, this operation has timed out. It is possible that it was succfully completed, but we are unable to verify it.","div.message.error"):
        #    pass
        #else:
        #baseutils.assert_contain_text_by_id(self,"OpenShift PHP app","spinner-text")
        #baseutils.click_element_by_css_no_wait(self,"a.close > img")
        #baseutils.wait_element_not_displayed_by_id(self,"spinner")
        self.assert_app_url(_appname)
        self.delete_application()
    '''
    def test_k_check_url_after_changedomain(self):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.domainuser[0],config.domainuser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        #baseutils.click_element_by_xpath(self,"//*[@id='domain_form_replacement']/a")
        #baseutils.click_element_by_link_text(self,"Express Console")
        #time.sleep(5)
        baseutils.wait_element_present_by_id(self,"express_domain_namespace")
        _value=self.driver.find_element_by_id("express_domain_namespace").get_attribute("value")
        _newvalue=_value[:len(_value)-1]
        print "======================"
        print _newvalue
        #baseutils.click_element_by_xpath(self,"//div[@id='domains']/div[2]/div[2]/div/a")
        #time.sleep(2)
        baseutils.wait_element_present_by_id(self,"express_domain_namespace")
        baseutils.input_by_id(self,"express_domain_namespace",_newvalue)
        baseutils.click_element_by_id(self,"express_domain_submit")
        time.sleep(10)
        baseutils.assert_element_present_by_link_text(self,_newvalue)
        time.sleep(20)
#        baseutils.click_element_by_css_no_wait(self,"a.close > img")
        #baseutils.wait_element_not_displayed_by_id(self,"spinner")
        #baseutils.assert_text_equal_by_css(self,"Congratulations! You successfully updated your domain","div.message.success")
        self.assert_app_url_after_change(self.exist_app,_newvalue)
    

    def test_l_create_bsame_appname_w_exist(self):
       # _appname=self.generate_app_name()
        self.create_application(self.exist_app,"php")
        _domain=self.get_domain_name()
        _error="An application named \'"+self.exist_app+"\' in namespace \'"+_domain+"\' already exists"
        baseutils.assert_text_equal_by_css(self,_error,"div.error.message")
    '''
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
    #HTMLTestRunner.main()
