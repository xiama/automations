from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US1797135713(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)

    def test_u_s1797135713(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user,self.cfg.password)
        baseutils.go_to_account_page(self)
        driver.find_element_by_link_text("Change password...").click()
        driver.find_element_by_id("web_user_old_password").clear()
        driver.find_element_by_id("web_user_old_password").send_keys("ewqewqewq")
        driver.find_element_by_id("web_user_password").clear()
        driver.find_element_by_id("web_user_password").send_keys("qweqweqwe")
        driver.find_element_by_id("web_user_password_confirmation").clear()
        driver.find_element_by_id("web_user_password_confirmation").send_keys("asdasdasdasd\t")
        baseutils.assert_text_equal_by_xpath(self, "Please enter the same value again.","//*[@id='web_user_password_confirmation_input']/div/p")
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
