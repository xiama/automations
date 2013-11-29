from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
#import unittest, time, re
#import baseutils
#import HTMLTestRunner

class US17971357232(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
        self.confirm_link=self.cfg.confirm_url_express

    
    def test_u_s17971357232(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user,self.cfg.password)
        if (not baseutils.has_domain(self)):
            baseutils.setup_domain(self)
        if (not baseutils.has_sshkey(self)):
            baseutils.setup_default_sshkey(self)

        baseutils.go_to_account_page(self)
        driver.find_element_by_link_text("Change your namespace...").click()
##
        for t in baseutils.Invalid_input:
            driver.find_element_by_id("domain_name").clear()
            driver.find_element_by_id("domain_name").send_keys(t)
            driver.find_element_by_id("domain_submit").click()
            baseutils.assert_text_equal_by_xpath(self, "Only letters and numbers are allowed","id('app-errors')/p")
            time.sleep(2)
##
        used_domain=self.cfg.exist_domain
        driver.find_element_by_id("domain_name").clear()
        driver.find_element_by_id("domain_name").send_keys(used_domain)
        driver.find_element_by_id("domain_submit").click()
        baseutils.assert_text_equal_by_xpath(self, "Namespace '%s' already in use. Please choose another."%used_domain,
                        "id('domain_name_group')/div/div[1]/p")
        new_domain=baseutils.get_random_str(10)
        print "DEBUG:", new_domain
        driver.find_element_by_id("domain_name").clear()
        driver.find_element_by_id("domain_name").send_keys(new_domain)
        driver.find_element_by_id("domain_submit").click()
        baseutils.wait_element_present_by_link_text(self, "Change your namespace...")
        baseutils.assert_text_equal_by_xpath(self, "http://applicationname"+u"\u2013"+"%s.rhcloud.com"%new_domain, "id('content')/div[2]/div[1]/section[2]/div[1]")
        
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
