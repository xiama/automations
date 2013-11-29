from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import random
import HTMLTestRunner


class CreateDomain(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
        self.domain=self.generate_domain_name()
        self.sshkey=self.ssh_key("id_rsa.pub")
        
    def generate_domain_name(self):
        i=random.uniform(1,10)
        domain_name="test"+str(i)[2:10]
        return domain_name

    def generate_new_sshkey(self,ssh_key_file):
        i=random.uniform(1,10)
        h = open(ssh_key_file, 'rb')
        _oldssh=h.read()
        _newssh=_oldssh[0:366]+str(i)[2:10]
        return _newssh

    def ssh_key(self,ssh_key_file):
        f = open(ssh_key_file, 'rb')
        ssh=f.read()
       # print ssh
        return ssh

  

    def create_domain(self,domain_name):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.domainuser[0],config.domainuser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
 #       baseutils.click_element_by_link_text(self,"Express Console")
        time.sleep(5)
        '''
        if config.proxy == 1:
            baseutils.click_element_by_link_text(self,"Looking for OpenShift Flex?")
            time.sleep(15)
            try: self.assertEqual("https://stg.openshift.redhat.com/flex/flex/index.html", self.driver.current_url())
            except AssertionError as e: self.verificationErrors.append(str(e))
            baseutils.go_back(self)
        else: baseutils.assert_element_present_by_link_text(self,"Looking for OpenShift Flex?")
        '''
        baseutils.assert_text_equal_by_css(self,"Control Panel","section.main > header > h1")
       # baseutils.assert_text_equal_by_xpath(self,"Desired domain name*","//li[@id='express_domain_namespace_input']/label")
        baseutils.click_element_by_link_text(self,"Edit...")
        time.sleep(5)
        baseutils.wait_element_present_by_id(self,"express_domain_namespace")
        baseutils.input_by_id(self,"express_domain_namespace",domain_name)
#       baseutils.input_by_id(self,"express_domain_ssh",ssh)
        self.driver.execute_script("window.scrollTo(0, 0);")
        baseutils.click_element_by_xpath(self,"//div[5]/div/div/form/fieldset/ol/li/input")
    
    def test_a_create_domain_no_domain_name(self):
        self.create_domain("")
        baseutils.assert_text_equal_by_xpath(self,"THIS FIELD IS REQUIRED.",".//*[@id='express_domain_namespace_input']/label[2]")

        
#       def test_b_create_domain_no_ssh_key(self):
#       self.create_domain(self.domain,"")
#       baseutils.assert_text_equal_by_css(self,"This field is required.","#express_domain_ssh_input > label.error")

    def test_c_create_domain_with_blacklist(self):
        self.create_domain("jboss")
        baseutils.assert_text_equal_by_css(self,"Namespace jboss is not permitted","div.error.message")
       
    def test_d_create_domain_with_nonalpha(self):
        self.create_domain("test_55")
        baseutils.assert_text_equal_by_css(self,"ONLY LETTERS AND NUMBERS ARE ALLOWED","label.error")
    
    def test_e_create_domain_with_over16charater(self):
        self.create_domain("abcdefg1234567890")
        baseutils.assert_value_equal_by_id(self,"abcdefg123456789","express_domain_namespace")

    
    def test_f_create_domain_with_existing_name(self):
        self.create_domain(config.exist_domain)
        time.sleep(5)
        baseutils.assert_text_equal_by_xpath(self,"A namespace with name \'"+config.exist_domain+"\' already exists","//div[@id='cp-dialog']/div/div")
    '''
    def test_g_create_domain_normally(self):
        domain_name=self.generate_domain_name()
        domain_name2=domain_name
        self.create_domain(self.domain)
        time.sleep(10)
        baseutils.go_to_home(self)
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        baseutils.assert_text_equal_by_xpath(self,domain_name2,"//div[@id='domains']/div[2]/div")
    '''
    def test_h_change_domain_name(self):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.domainuser[0],config.domainuser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,"//div[@id='domains']/div[2]/div[2]/div/a")
        while self.driver.current_url not in [self.base_url+"/app/dashboard",self.base_url+"/app/control_panel"]:
           baseutils.go_to_express_console(self)             
        try:
           while (not baseutils.assert_element_present_by_id("express_domain_namespace")):
               baseutils.click_element_by_xpath(self,"//div[@id='domains']/div[2]/div[2]/div/a")
        except:pass
        _value=self.driver.find_element_by_id("express_domain_namespace").get_attribute("value")
        _newvalue=_value[:len(_value)-1]
        baseutils.input_by_id(self,"express_domain_namespace",_newvalue)
        baseutils.click_element_by_xpath(self,"//div[5]/div/div/form/fieldset/ol/li/input")
        time.sleep(5)
        baseutils.assert_text_equal_by_css(self,_newvalue,"div.current.domain")
        
    def test_i_create_domain_sshkey(self):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.tochangepwduser[0],config.tochangepwduser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,".//div[@id='ssh_container']/div/div[2]/div/a")
        _newssh=self.ssh_key("id2_rsa.pub")
        baseutils.input_by_id(self,"ssh_form_express_domain_ssh",_newssh)
        baseutils.click_element_by_xpath(self,"//div[5]/div/div/form/fieldset/ol/li/input")
        time.sleep(5)
        baseutils.assert_text_equal_by_css(self,_newssh[0:20]+"...","div.current.ssh")
    
    def test_j_change_domain_sshkey(self):
        baseutils.go_to_home(self)
        time.sleep(4)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.tochangepwduser[0],config.tochangepwduser[1])
        baseutils.go_to_express_console(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,".//div[@id='ssh_container']/div/div[2]/div/a")
        _newssh=self.generate_new_sshkey("id2_rsa.pub")
#        _changessh=_newssh[1:374]+"a"
        baseutils.input_by_id(self,"ssh_form_express_domain_ssh",_newssh)
        baseutils.click_element_by_xpath(self,"//div[5]/div/div/form/fieldset/ol/li/input")
        time.sleep(5)
        baseutils.assert_text_equal_by_css(self,_newssh[0:20]+"...","div.current.ssh")

    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
   # HTMLTestRunner.main() 
