from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US1797135719(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)

    
    def test_u_s1797135719(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user,self.cfg.password)
        if (not baseutils.has_domain(self)):
            baseutils.setup_domain(self)
        if (not baseutils.has_sshkey(self)):
            baseutils.setup_default_sshkey(self)

        baseutils.go_to_account_page(self)
        (priv, pub)= baseutils.gen_sshkey()
        key_name = "key"+baseutils.get_random_str(3)
        baseutils.add_sshkey(self, key_name, pub)
        baseutils.delete_sshkey(self, key_name)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
