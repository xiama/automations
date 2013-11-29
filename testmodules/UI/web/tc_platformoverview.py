from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner


class PlatformOverview(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.binary= ""
        self.verificationErrors = []
        baseutils.initiate(self)

    def test_check_platform_a_overview_never_signin(self):
        baseutils.go_to_platformoverview(self)
        self.driver.delete_cookie("_rhc_session")
        self.driver.delete_cookie("rh_sso")
        self.driver.delete_cookie("prev_login")
        self.driver.refresh()
#        baseutils.click_element_by_link_text(self,"EXPRESS")
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,"//*[@id='express']/h2/a")
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath_no_wait(self,"//*[@id='flex']/header/h2/a")
        baseutils.check_title(self,"OpenShift by Red Hat | Flex")
        baseutils.go_back(self)
#        baseutils.click_element_by_xpath_no_wait(self,"//*[@id='power']/header/h2/a")
#        baseutils.check_title(self,"OpenShift by Red Hat | Power")
#        baseutils.go_back(self)
#        baseutils.scroll_bar(self)
#        baseutils.click_element_by_xpath(self,"//li[@id='express']/div/a")
#        baseutils.check_title(self,"OpenShift by Red Hat | Platform Features")
#        baseutils.go_back(self)
#        baseutils.scroll_bar(self)
#        baseutils.click_element_by_xpath(self,"//li[@id='flex']/div/a")
#        baseutils.check_title(self,"OpenShift by Red Hat | Platform Features")
#        baseutils.go_back(self)
#        baseutils.scroll_to_upper(self)
#        baseutils.assert_contain_text_by_xpath(self,"//div[@id='user_box']/div/h2","Don't have an OpenShift account")
        baseutils.click_element_by_link_text(self,"Create account")
        baseutils.assert_element_present_by_id(self,"web_user_email_address")
        baseutils.click_element_by_css(self,"#signup > a.close_button > img")
        baseutils.click_element_by_link_text(self,"...or sign in")
        baseutils.assert_element_present_by_id(self,"login_input")
        baseutils.click_element_by_css(self,"a.close_button > img")
        baseutils.assert_text_equal_by_css(self,"POPULAR OPENSHIFT VIDEOS","#videos > header > h1")
        baseutils.click_element_by_link_text(self,"Watch more videos")
        baseutils.check_title(self,"Videos | Red Hat OpenShift Community")
        baseutils.go_back(self)
        baseutils.assert_element_present_by_xpath(self,"//*[@id='retweets']/ul/li[*]/a/img")
        baseutils.assert_element_present_by_xpath(self,"//*[@id='retweets']/ul/li[*]/p")
        baseutils.assert_element_present_by_xpath(self,"//*[@id='buzz']/a")
        if config.proxy:
           baseutils.click_element_by_xpath(self,"//*[@id='buzz']/a")
           time.sleep(5)
           baseutils.check_title(self,"Red Hat OpenShift (openshift) on Twitter")

    def test_check_platform_b_overview_videos_links(self):
        baseutils.go_to_platformoverview(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_css(self,"img[alt=\"OpenShift Appcelerator Demo\"]")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch Deploying Mobile Apps on OpenShift with Appcelerator")
        baseutils.go_back(self)
        baseutils.scroll_to_upper(self)
        baseutils.click_element_by_link_text(self,"Mobile App Deployment to Express w/ Appcelerator")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch Deploying Mobile Apps on OpenShift with Appcelerator")
        baseutils.go_back(self)
        baseutils.scroll_to_upper(self)
        baseutils.click_element_by_css(self,"img[alt=\"OpenShift Flex Product Tour\"]")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch OpenShift Flex Product Tour")
        baseutils.go_back(self)
        baseutils.scroll_to_upper(self)
        baseutils.click_element_by_link_text(self,"OpenShift Flex Product Tour")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch OpenShift Flex Product Tour")
        baseutils.go_back(self)
        baseutils.scroll_to_upper(self)
        baseutils.click_element_by_css(self,"img[alt=\"Deploying to OpenShift PaaS with the eXo Cloud IDE\"]")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch Deploying to OpenShift PaaS with the eXo cloud IDE")
        baseutils.go_back(self)
        baseutils.scroll_to_upper(self)
        baseutils.click_element_by_link_text(self,"Deploying to OpenShift PaaS with the eXo Cloud IDE")
        baseutils.check_title(self,"OpenShift by Red Hat | Watch Deploying to OpenShift PaaS with the eXo cloud IDE")

    def test_check_platform_c_overview_signed_in_out(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        time.sleep(20)
        baseutils.go_to_platformoverview(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,"//li[@id='express']/div/a")
        baseutils.assert_text_equal_by_css(self,"Control Panel","section.main > header > h1","Control Panel is not equal here")
        baseutils.go_back(self)
#        baseutils.scroll_bar(self)
#        baseutils.assert_contain_text_by_css(self,"Open","#flex > div.content > a.more")
        baseutils.logout(self)
        baseutils.click_element_by_link_text(self,"Platform Overview")
        baseutils.scroll_to_upper(self)
#        baseutils.assert_contain_text_by_css(self,"Compare features","a.more")
#        baseutils.assert_contain_text_by_xpath(self,"Compare features","//li[@id='flex']/div/a")
        baseutils.assert_text_equal_by_xpath(self,"Sign in to OpenShift",".//*[@id='user_box']/div/h2")
        baseutils.click_element_by_link_text(self,"Click here to reset your password")
#        while (not baseutils.assert_element_present_by_css(self,"#reset_password > header > h1")):
#            baseutils.click_element_by_link_text(self,"Click here to reset your password")
#        baseutils.assert_text_equal_by_css(self,"Reset your password","#reset_password > header > h1","Reset your password is not equal to the text here")
#        baseutils.click_element_by_xpath(self,"//div[@id='reset_password']/a/img")
        baseutils.click_element_by_link_text(self,"Click here to register")
        time.sleep(4)
        baseutils.assert_element_present_by_id(self,"web_user_email_address")
#        baseutils.click_element_by_css(self,"#signup > a.close_button > img")
        

    def tearDown(self):
        self.driver.quit()
        if len(self.verificationErrors)==1:
           self.assertEqual([''], self.verificationErrors)
        else:self.assertEqual([], self.verificationErrors)
        

if __name__ == "__main__":
    unittest.main()
