from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US1797135717(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
        self.confirm_link=self.cfg.confirm_url_express
    
    def test_u_s1797135717(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user, self.cfg.password)
        #check if domain and default ssh key already exist
        if (not baseutils.has_domain(self)):
            baseutils.setup_domain(self)
        if (not baseutils.has_sshkey(self)):
            baseutils.setup_default_sshkey(self)

        baseutils.go_to_account_page(self)
        keyname='test'

        driver.find_element_by_link_text("Add a new key...").click()
        driver.find_element_by_id("key_name").clear()
        driver.find_element_by_id("key_name").send_keys(keyname)
        driver.find_element_by_id("key_raw_content").clear()
        driver.find_element_by_id("key_raw_content").send_keys(baseutils.gen_sshkey()[1])
        driver.find_element_by_id("key_submit").click()
        baseutils.wait_element_present_by_id(self, "%s_sshkey"%keyname)
        baseutils.assert_contain_text_by_xpath(self, keyname,"id('%s_sshkey')/td[1]"%keyname)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
