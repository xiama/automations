#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
import clog
import sys
import time
import unittest
import rhtest

"""
class and support functions for web automation

"""

log = clog.get_logger()

class AutoWeb(rhtest.Test, unittest.TestCase):
    log = log
    driver = None #webdriver.Firefox()  #default
    browser = 'firefox'
    base_url = None
    proxy = False
    browserpath = 0
    platform = 'dev'
    domain = 'yujzhang2259'

    username_simple_account = 'mgao+stg33@redhat.com'
    password_simple_account = 'redhat'
    username_both_registered_openshift_account = 'mgao+stg69@redhat.com'
    password_both_registered_openshift_account = 'redhat'
    username_both_registered_RHN_account = 'mgaostg69'
    password_both_registered_RHN_account = '111111'
    username_RHN_account = 'mgaostg59'
    username_email_of_RHN_account = 'mgao+stg59@redhat.com'
    password_email_of_RHN_account = 'redhat'
    username_not_accept_terms_account = 'mgao+NotAccept@redhat.com'
    password_not_accept_terms_account = 'redhat'

    
    def __init__(self, **kwargs):
        if kwargs.has_key('logger'):
            # use local global logger if none is given (with framework, then 
            # the framework logger should be used.
            self.log = kwargs['logger']

        if kwargs.has_key('browser'):
            self.browser = kwargs['browser'].strip().lower()
        if kwargs.has_key('ip'):
            self.base_url = "https://" + kwargs['ip']
        if kwargs.has_key('browser_path'):
            self.browserpath = kwargs['browserpath']

        if kwargs.has_key('config'):
            self.config = kwargs['config']

        if kwargs.has_key('proxy'):
            self.proxy=kwargs['proxy']
        
        if self.proxy:
            print "### setting proxy"
            self.profile=webdriver.FirefoxProfile()
            self.profile.set_preference("network.proxy.type", 1)
            self.profile.set_preference("network.proxy.http", "file.sjc.redhat.com")
            self.profile.set_preference("network.proxy.http_port", 3128)
            self.profile.set_preference("network.proxy.ssl", "file.sjc.redhat.com")
            self.profile.set_preference("network.proxy.ssl_port", 3128)
            self.driver = webdriver.Firefox(self.profile)
        else:
            self.driver = webdriver.Firefox()
            pass # self.info("xxx", 1)
        self.verificationErrors = []


    def wait_element_present_by_link_text(self,name):
        self.do_wait(By.LINK_TEXT, name)
            
    def check_title(self, title):
        time.sleep(5)
        title_match = False
        for i in range(60):
            try:
                if title == self.driver.title:
                    title_match = True
                    break
            except:
                pass
            time.sleep(1)
        if not title_match:
            log.error("timed out, '%s' is not equal to '%s'" % title, self.driver.title)

    def assert_element_not_present_by_css(self, css):
        try: self.assert_false(is_element_present(self, By.CSS_SELECTOR,css))
        except AssertionError as e: self.verificationErrors.append(str(e))
    
    def assert_element_present_by_css(self, css, msg=''):
        try: self.assert_true(self.is_element_present(By.CSS_SELECTOR,css))
        except AssertionError as e: self.verificationErrors.append(msg+","+str(e))

    def assert_element_present_by_id(self, idname, msg=''):
        try: self.assert_true(self.is_element_present(By.ID,idname))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_not_present_by_id(self, idname):
        try: self.assert_false(self.is_element_present(self, By.ID,idname))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_present_by_xpath(self, xpath):
        try: self.assert_true(self.is_element_present(self, By.XPATH,xpath))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_present_by_link_text(self, link_text):
        self.assert_true(self.is_element_present(By.LINK_TEXT,link_text))

    def assert_element_present_by_partial_link_text(self, partial_link_text):
        try: self.assert_true(is_element_present(self, By.PARTIAL_LINK_TEXT ,partial_link_text))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_present_by_name(self, name):
        try: self.assert_true(is_element_present(self, By.NAME ,name))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_present_by_class_name(self, class_name):
        try: self.assert_true(is_element_present(self, By.CLASS_NAME ,class_name))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_element_present_by_tag_name(self, tag_name):
        try: self.assert_true(is_element_present(self, By.TAG_NAME ,tag_name))
        except AssertionError as e: self.verificationErrors.append(str(e))


    def assert_element_present(self, how,what):
        try: self.assert_true(is_element_present(self, how ,what))
        except AssertionError as e: self.verificationErrors.append(str(e))

    def assert_text_equal_by_css(self, text,css, msg=''):
        try: self.assert_equal(text,self.driver.find_element_by_css_selector(css).text)
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def assert_text_equal_by_xpath(self, text, xpath, msg=''):
        try: self.assert_equal(text,self.driver.find_element_by_xpath(xpath).text)
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def assert_text_equal_by_partial_link_text(self, text, partial_link_text, msg=''):
        try: self.assertEqual(text,self.driver.find_element_by_partial_link_text(partial_link_text).text)
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def assert_text_equal_by_id(self, text,id_name, msg=''):
        try: self.assertEqual(text,self.driver.find_element_by_id(id_name).text)
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def assert_text_regexp_match_by_css(self, text, css, msg=''):
        try: self.assertRegexpMatches(self.driver.find_element_by_css_selector(css).text,text)
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def assert_value_equal_by_id(self, value,id_name, msg=''):
        try: self.assertEqual(value,self.driver.find_element_by_id(id_name).get_attribute("value"))
        except (AssertionError, NoSuchElementException) as e: self.verificationErrors.append("%s >> %s"%(msg,str(e)))

    def is_text_equal_by_css(self, text,css):
        for i in range(60):
            try:
                if text == self.driver.find_element_by_css_selector(css).text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out,%s is not equal to %s" %(text,self.driver.find_element_by_css_selector(css).text))

    def is_text_equal_by_xpath(self, text,xpath):
        for i in range(60):
            try:
                if text == self.driver.find_element_by_xpath(xpath).text: break
            except: pass
            time.sleep(1)
        else:self.fail("time out,%s is not equal to %s" %(text,self.driver.find_element_by_xpath(xpath).text))

    # support functions 
    def click_element_by_link_text(self, link_text):
        self.wait_element_present_by_link_text(link_text)
        self.driver.find_element_by_link_text(link_text).click()

    def click_element_by_css(self, css):
        self.wait_element_present_by_css(self,css)
        self.driver.find_element_by_css_selector(css).click()

    def click_element_by_id(self, id_name):
        self.wait_element_present_by_id(id_name)
        self.driver.find_element_by_id(id_name).click()

    def click_element_by_xpath(self, xpath):
        self.wait_element_present_by_xpath(xpath)
        self.driver.find_element_by_xpath(xpath).click()

    def click_element_by_name(self, name):
        self.wait_element_present_by_name(name)
        self.driver.find_element_by_name(name).click()

    def click_element_by_xpath_wait(self,xpath):
        self.wait_element_present_by_xpath(xpath)
        self.driver.find_element_by_xpath(xpath).click()
        time.sleep(8)     

    def click_element_by_class(self,class_name):
        self.wait_element_present_by_class(self,class_name)
        self.driver.find_element_by_class_name(class_name).click()

    def click_element_by_css_no_wait(self,css):
        self.driver.find_element_by_css_selector(css).click()

    def click_element_by_id_no_wait(self,id_name):
        self.driver.find_element_by_id(id_name).click()

    def click_element_by_xpath_no_wait(self,xpath):
        self.driver.find_element_by_xpath(xpath).click()

    def click_element_by_partial_link_text_no_wait(self,partial_link_text):
        self.driver.find_element_by_partial_link_text(partial_link_text).click()

    def do_wait(self, element_type, element_name):
        try:
            element = WebDriverWait(self.driver, 60).until(lambda driver : driver.find_element(element_type, element_name))
        except:
            self.log.error("Timed out waiting for element '%s'" % element_name)

    def wait_element_present_by_xpath(self,xpath):
        self.do_wait(By.XPATH, xpath)
        
    def wait_element_not_present_by_xpath(self,xpath):
        for i in range(60):
            try:
                if not is_element_present(self,By.XPATH, xpath): break
            except: pass
            time.sleep(1)
        else: self.fail("time out,%s is present"%(xpath))

    def wait_element_present_by_css(self, css):
        self.do_wait(By.CSS_SELECTOR, css)

    def wait_element_present_by_id(self, idname):
        self.do_wait(By.ID, idname)

    def wait_element_present_by_class(self, class_name):
        self.do_wait(By.CLASS_NAME, class_name)


    def wait_element_present_by_name(self,name):
        self.do_wait(By.NAME, name)

    def go_to_home(self):
        self.driver.get(self.base_url+"/app")
        self.check_title("OpenShift by Red Hat")

    def go_to_community(self):
        self.driver.get(self.base_url+"/community")
        self.check_title("Welcome to OpenShift | OpenShift by Red Hat")  

    def go_to_developer(self):
        self.driver.get(self.base_url+"/community/developers")
        self.check_title("Developer Center | OpenShift by Red Hat")      

    def go_to_pricing(self):
        self.driver.get(self.base_url+"/pricing")

    def go_to_signin(self, link_text="Sign In to Manage Your Apps".upper()):
        self.click_element_by_link_text(link_text)
        self.is_element_displayed(By.ID,"web_user_rhlogin")

    def go_to_signup(self):
        self.go_to_home()
        self.scroll_to_bottom()
        self.click_element_by_xpath(".//*[@id='bottom_signup']/div/a")
        time.sleep(2)
        if not is_element_displayed(self,By.ID,"signup"):
           self.click_element_by_xpath(".//*[@id='bottom_signup']/div/a")
        self.is_element_displayed(By.ID,"signup")

    def go_to_partners(self):
        partner_page=self.base_url+"/app/partners"
        self.driver.get(partner_page)
        self.check_title("OpenShift by Red Hat | Meet Our Partners")

    def go_to_legal(self):
        legal_page=self.base_url+"/app/legal"
        self.driver.get(legal_page)
        self.check_title("OpenShift by Red Hat | Terms and Conditions")
        self.driver.execute_script("window.scrollTo(0, 0);")


    def go_to_platformoverview(self):
        go_to_home(self)
        self.click_element_by_link_text("Platform Overview")
        self.check_title("OpenShift by Red Hat | Cloud Platform")

    def go_to_account(self):
        self.driver.get(self.base_url+"/app/account")
        
    
    def go_back(self):      
        self.driver.back()
        time.sleep(5)
 
    def go_to_register(self):
        register_page=self.base_url+"/app/account/new"
        self.driver.get(register_page)

    def go_to_platform(self):
        platform_page=self.base_url+"/app/platform"
        self.driver.get(platform_page)

    def go_to_login(self):
        login_page=self.base_url+"/app/login"
        self.driver.get(login_page)

    def go_to_domain_edit(self):
        domain_edit_page=self.base_url+"/app/domain/edit"
        self.driver.get(domain_edit_page)
 
    def go_to_create_drupal(self):
        create_drupal_page=self.base_url+"/app/console/application_types/drupal"
        self.driver.get(create_drupal_page)

    def go_to_create_app(self, app_type):
        create_app_page=self.base_url+"/app/console/application_types/"+app_type
        self.driver.get(create_app_page)
        time.sleep(3)
        self.driver.refresh()
        time.sleep(2)

    def create_app(self, app_type, app_name):
        self.go_to_create_app(app_type)
        time.sleep(5)
        self.input_by_id("application_name", app_name)
        self.click_element_by_name("submit")
        time.sleep(5)
        self.driver.refresh()
        time.sleep(2)
         

    def go_to_app_detail(self, app_name):
        app_detail_page=self.base_url+"/app/console/applications/"+app_name
        self.driver.get(app_detail_page)
        time.sleep(3)
        self.driver.refresh()
        time.sleep(2)

    def go_to_account_page(self):
        account_page=self.base_url+"/app/account"
        self.driver.get(account_page)
        self.driver.refresh()
        time.sleep(2)

    def go_to_password_edit(self):
        password_edit_page=self.base_url+"/app/account/password/edit"
        self.driver.get(password_edit_page)
        self.driver.refresh()
        time.sleep(2)

    def delete_last_app(self, app_name):
        self.go_to_app_detail(app_name)
        time.sleep(2)
        self.click_element_by_link_text("Delete this application")
        time.sleep(1)
        self.click_element_by_name("submit")
        time.sleep(60)
        self.go_to_app_detail(app_name)
        self.assert_text_equal_by_xpath("Sorry, but the page you were trying to view does not exist.", '''//article/div/p''')
        

    def delete_app(self, app_name):
        self.go_to_app_detail(app_name)
        time.sleep(2)
        self.click_element_by_link_text("Delete this application")
        time.sleep(1)
        self.click_element_by_name("submit")
        time.sleep(60)
        self.go_to_app_detail(app_name)
        self.assert_text_equal_by_xpath("Sorry, but the page you were trying to view does not exist.", '''//article/div/p''')
       

    def add_cartridge(self, app_name, cartridge_name):
        self.go_to_app_detail(app_name)
        self.click_element_by_xpath('''//section[@id='app-cartridges']/div[2]/a''')
        self.click_element_by_xpath("//a[contains(@href, '/cartridge_types/"+cartridge_name+"')]")
        self.click_element_by_id("cartridge_submit")
        time.sleep(8)
        self.driver.refresh()
        time.sleep(2)

    def change_password(self, old_password, new_password):

        self.go_to_password_edit()
        self.input_by_id("web_user_old_password", old_password)
        self.input_by_id("web_user_password", new_password) 
        self.input_by_id("web_user_password_confirmation", new_password) 
        self.click_element_by_name('commit')
        time.sleep(10)
        self.driver.refresh()
        time.sleep(2)
        

    def input_by_id(self, id_name, input_content):
        self.driver.find_element_by_id(id_name).clear()
        self.driver.find_element_by_id(id_name).send_keys(input_content)
  
    def clear_element_value(self, id_name):
        self.driver.find_element_by_id(id_name).clear()
        

    #############################################################
    # check & assertions
    #############################################################
    def is_element_displayed(self, how, what):
        #res  = self.assert_true(self.driver.find_element(by=how,value=what).is_displayed())
        #self.info("xxx", 1)
        #try:#self.assert_true(self.driver.find_element(by=how,value=what).is_displayed(),what+" is not displayed")
        time.sleep(4)
        self.assert_true(self.driver.find_element(by=how,value=what).is_displayed())
        #except AssertionError as e: self.verificationErrors.append(str(e))

    def is_element_hidden(self,how,what):
        try:self.assertFalse(self.driver.find_element(by=how,value=what).is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))

    def wait_element_not_displayed_by_id(self,id_name):
        try:
           WebDriverWait(self.driver,120).until(self.driver.find_element_by_id(id_name))
           self.assertTrue(self.driver.find_element_by_id(id_name).is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))

    def is_text_displayed(self,text,css):
        try:
           WebDriverWait(self.driver, 100).until(self.driver.find_element_by_css_selector(css))
           self.assertTrue( text == self.driver.find_element_by_css_selector(css).text)
        except AssertionError as e: self.verificationErrors.append(str(e))

    def is_text_displayed_by_id(self,text,id_name):
        try:
           WebDriverWait(self.driver, 100).until(self.driver.find_element_by_id(id_name))
           self.assertTrue( text == self.driver.find_element_by_id(id_name).text)
        except AssertionError as e: self.verificationErrors.append(str(e))


    ## helper functions 
    def login(self):
        username = self.config.OPENSHIFT_user_email
        password = self.config.OPENSHIFT_user_passwd

        self.go_to_login()
        self.wait_element_present_by_id("web_user_rhlogin")
        self.input_by_id("web_user_rhlogin", username)
        self.input_by_id("web_user_password", password)
        self.click_element_by_name('''commit''')
        time.sleep(5)
        self.driver.refresh()
        time.sleep(2)

    def login_new(self,username,password):
     
        self.go_to_login()
        self.wait_element_present_by_id("web_user_rhlogin")
        self.input_by_id("web_user_rhlogin", username)
        self.input_by_id("web_user_password", password)
        self.click_element_by_name('''commit''')
        time.sleep(5)
        self.driver.refresh()
        time.sleep(2)


    def logout(self):
        self.assert_element_present_by_link_text("Sign Out")
        self.click_element_by_link_text("Sign Out")
        sign_in_text="Sign In to Manage Your Apps".upper()
        self.assert_element_present_by_link_text(sign_in_text)

    def __del__(self):
        self.driver.close()

def _test(ip):
    web = AutoWeb(ip=ip)
    #web = AutoWeb(ip=ip, proxy=True)
    web.go_to_home()
    sign_in_text="Sign In to Manage Your Apps".upper()
    web.go_to_signin(sign_in_text)
    web.assert_element_present_by_link_text("Forgot your password?")
    web.assert_element_present_by_link_text("create an account")
    web.assert_element_present_by_css("input.btn")

def test_login_invalid_user(ip):
    """ test invalid user """
    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login("baduser", "vostok08")
    print "#############"
    #web.assert_text_equal_by_css("Invalid username or password","div.message.error")
    web.assert_text_equal_by_css("Invalid username or password","div.alert.alert-error")

def test_login_without_user(ip):
    """ test_login_without_user """
    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login("", "vostok08")
    web.assert_text_equal_by_css("This field is required.","p.help-inline")

def test_login_without_pwd(ip):
    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login("pruan@redhat.com", "")
    web.assert_text_equal_by_css("This field is required.","p.help-inline")

def test_login_granted_user(ip, username='pruan@redhat.com', password="vostok08"):
    log.info("Testing login with valid user")
    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login(username, password)
    web.check_title("OpenShift by Red Hat")
    web.assert_element_present_by_link_text("Sign Out")

def test_login_sql_bypass(ip):
    log.info("Testing login with sql bypass")
    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login("xtian+0@redhat.com or 1=1", "vostok08")
    web.assert_text_equal_by_css("Invalid username or password","div.alert")

def test_login_session_exists(ip):

    web = AutoWeb(ip=ip)
    web.go_to_home()
    web.go_to_signin()
    web.login()
    web.check_title("OpenShift by Red Hat")
    web.assert_element_present_by_link_text("Sign Out") 


def test_login_logout_back(ip):
    web = AutoWeb(ip=ip)

    web.go_to_home()
    web.go_to_signin()
    web.login()
    web.check_title("OpenShift by Red Hat")
    web.assert_element_present_by_link_text("Sign Out")
    web.logout()
    web.go_back()
    web.driver.refresh()
    web.assert_element_present_by_id("login_input")

def test_login_cookie_deleted(self):
    web.go_to_home(self)
    web.go_to_signin(self)
    web.login(self,config.granted_user[0],config.granted_user[1])
    time.sleep(5)
#       web.wait_for_ajax(self)
    web.check_title(self,"OpenShift by Red Hat | Cloud Platform")
 #   web.assert_element_present_by_link_text(self,"Get started!")
    _greetings=web.generate_greetings(config.granted_user[0])
    web.assert_element_present_by_link_text(self,_greetings)
    web.assert_element_present_by_link_text(self,"Sign out")
    self.driver.delete_cookie("_rhc_session")
    self.driver.delete_cookie("rh_sso")
    self.driver.refresh()
    web.assert_element_present_by_link_text(self,"Sign in")
    


    
    
    
if __name__ == '__main__':
    ip = sys.argv[1]

    test_login_logout_back(ip)
    #test_login_sql_bypass(ip)

    #web = AutoWeb(ip=ip)
    #web = AutoWeb(ip=ip, proxy=True)
    #web.go_to_home()
    #log.info("#################")
    #sign_in_text="Sign In to Manage Your Apps".upper()
    #web.go_to_signin(sign_in_text)
    #web.assert_element_present_by_link_text("Forgot your password?")
    #web.assert_element_present_by_link_text("create an account")
    #web.assert_element_present_by_css("input.btn")
    

    #web.assert_element_present_by_css("a.password_reset.more")
