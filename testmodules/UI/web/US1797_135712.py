'''
    [US1797][UI][Account Management]Change password from "My Account" page with invalid old password [P1]
    author: mzimen@redhat.com
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US1797135712(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    
    def test_u_s1797135712(self):
        driver = self.driver
        baseutils.login(self, self.cfg.new_user,self.cfg.password)
        if (not baseutils.has_domain(self)):
            baseutils.setup_domain(self)
        if (not baseutils.has_sshkey(self)):
            baseutils.setup_default_sshkey(self)
        baseutils.go_to_account_page(self)


        driver.find_element_by_link_text("Change password...").click()
        baseutils.wait_element_present_by_id(self, "web_user_old_password")
        self.assertEqual("OpenShift by Red Hat | OpenShift Change Password", driver.title)

        driver.find_element_by_id("web_user_old_password").clear()
        driver.find_element_by_id("web_user_old_password").send_keys(self.cfg.password)

        driver.find_element_by_id("web_user_password").clear()
        driver.find_element_by_id("web_user_password").send_keys("abcabc")

        driver.find_element_by_id("web_user_password_confirmation").clear()
        driver.find_element_by_id("web_user_password_confirmation").send_keys("abcabb\t")
        driver.find_element_by_id("web_user_submit").click()
        time.sleep(5)
        baseutils.assert_text_equal_by_xpath(self, "Passwords must match", "id('web_user_password_input')/div/p")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
