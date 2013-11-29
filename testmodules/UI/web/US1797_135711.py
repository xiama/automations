from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US1797135711(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)

    
    def test_u_s1797135711(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user,self.cfg.password)
        baseutils.go_to_account_page(self)

        driver.find_element_by_link_text("Change password...").click()
        baseutils.wait_element_present_by_id(self,"web_user_submit")
        self.assertEqual("OpenShift by Red Hat | OpenShift Change Password", driver.title)

        driver.find_element_by_id("web_user_old_password").clear()
        driver.find_element_by_id("web_user_old_password").send_keys(self.cfg.password)
        driver.find_element_by_id("web_user_password").clear()
        new_password="abcabc"
        driver.find_element_by_id("web_user_password").send_keys(new_password)
        driver.find_element_by_id("web_user_password_confirmation").clear()
        driver.find_element_by_id("web_user_password_confirmation").send_keys("%s\t"%new_password)

        driver.find_element_by_id("web_user_submit").click()
        baseutils.wait_element_present_by_link_text(self,"Change password...")
        self.assertEqual("OpenShift by Red Hat | My Account", driver.title)

        baseutils.logout(self)
        baseutils.login(self,self.cfg.new_user, new_password)

        #and put it back
        baseutils.go_to_account_page(self)
        baseutils.wait_element_present_by_link_text(self,"Change password...")
        driver.find_element_by_link_text("Change password...").click()

        baseutils.wait_element_present_by_id(self,"web_user_submit")
        self.assertEqual("OpenShift by Red Hat | OpenShift Change Password", driver.title)
        driver.find_element_by_id("web_user_old_password").clear()
        driver.find_element_by_id("web_user_old_password").send_keys(new_password)
        driver.find_element_by_id("web_user_password").clear()
        driver.find_element_by_id("web_user_password").send_keys(self.cfg.password)
        driver.find_element_by_id("web_user_password_confirmation").clear()
        driver.find_element_by_id("web_user_password_confirmation").send_keys("%s\t"%self.cfg.password)
        driver.find_element_by_id("web_user_submit").click()
        baseutils.wait_element_present_by_link_text(self,"Change password...")
        #and we should be back at my_account page
        self.assertEqual("OpenShift by Red Hat | My Account", driver.title)

    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
