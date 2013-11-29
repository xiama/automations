'''
[US1797][UI][Account Management]Create domain from link in "My Account" page
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import HTMLTestRunner

class US17971357222(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
        self.confirm_link=self.cfg.confirm_url_express

    
    def test_u_s17971357222(self):
        driver = self.driver
        baseutils.login(self,self.cfg.new_user,self.cfg.password)
#domain shouldn't exist
        if (baseutils.has_domain(self)):
            time.sleep(10)
            raise Exception("The domain already exist")

        baseutils.go_to_account_page(self)
        invalid = [("longerlongerlongerlonger", u"Namespace 'longerlongerlongerlonger' is too long. Maximum length is 16 characters.") ]
        for t in invalid:
            driver.find_element_by_id("domain_name").clear()
            driver.find_element_by_id("domain_name").send_keys(t[0])
            driver.find_element_by_id("domain_submit").click()
            baseutils.wait_element_present_by_id(self, "domain_submit")
            baseutils.assert_text_regexp_match_by_xpath(self, t[1],"id('domain_name_group')/div/div[1]/p")
            time.sleep(2)
        #zero string
        driver.find_element_by_id("domain_name").clear()
        driver.find_element_by_id("domain_submit").click()
        baseutils.wait_element_present_by_id(self, "domain_submit")
        baseutils.assert_text_regexp_match_by_xpath(self, u"This field is required.", "id('app-errors')/p")

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
        baseutils.assert_text_regexp_match_by_xpath(self, u"Namespace '%s' is already in use. Please choose another."%used_domain, "id('domain_name_group')/div/div[1]/p")
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
