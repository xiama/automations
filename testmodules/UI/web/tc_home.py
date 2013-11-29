from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class HomePage(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.binary= ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    def test__a_check_home_navigation_bar(self):
        baseutils.go_to_home(self)
        baseutils.click_element_by_xpath(self,".//*[@id='main_nav']/div/ul/li[1]/a")
        baseutils.check_title(self,"OpenShift by Red Hat | Cloud Platform")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Express')]")
        baseutils.check_title(self,"OpenShift by Red Hat | Express")

    def test_aa_check_flex_nav_bar(self):
        baseutils.go_to_home(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Flex')]")
        time.sleep(5)
        baseutils.check_title(self,"OpenShift by Red Hat | Flex")
        
      #  baseutils.click_element_by_link_text(self,"POWER")
      #  baseutils.check_title(self,"OpenShift by Red Hat | Power")

    def test_ab_check_community_nav_bar(self):
        baseutils.go_to_home(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Community')]")
        time.sleep(5)     
        baseutils.check_title(self,"Red Hat OpenShift Community")
        baseutils.go_back(self)
        time.sleep(5)
        baseutils.click_element_by_link_text(self,"Sign in")
        baseutils.is_element_displayed(self,By.ID,"login-form")
       # baseutils.check_title(self,"OpenShift by Red Hat | Sign in to OpenShift")
    

    def test__b_check_home_links(self):
        baseutils.go_to_home(self)
        baseutils.go_to_signin(self)
        baseutils.click_element_by_xpath(self,"//img[@alt='OpenShift Logo']")
        time.sleep(5)
        baseutils.check_title(self,"OpenShift by Red Hat")
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,"//section[@id='opener']/div/a")
        time.sleep(5)
        if not baseutils.is_element_displayed(self,By.ID,"signup"):
            baseutils.click_element_by_xpath(self,"//section[@id='opener']/div/a")
#        baseutils.check_title(self,"OpenShift by Red Hat | Sign up for OpenShift")
        baseutils.click_element_by_css_no_wait(self,"#signup > a.close_button > img")
        baseutils.click_element_by_xpath(self,"//section[@id='bottom_signup']/div/a")
#        baseutils.check_title(self,"OpenShift by Red Hat | Sign up for OpenShift")
        time.sleep(5)
        baseutils.is_element_displayed(self,By.ID,"signup")
        

    def test_c_check_home_contents(self):
        baseutils.go_to_home(self)
        baseutils.assert_element_present_by_xpath(self,"//img[@alt='OpenShift Logo']")
        baseutils.assert_text_equal_by_css(self,"GO BEYOND THE CLOUDS","div.content > header > hgroup > h1")
        baseutils.assert_text_equal_by_css(self,"JAVA PHP RUBY PYTHON PERL","div.content > header > hgroup > h2")
#        baseutils.assert_element_present_by_xpath(self,"//img[@alt='Panda pilot, soaring through the clouds!']")
        baseutils.assert_text_equal_by_css(self,"WHAT IS OPENSHIFT?","#exposition > header > h1")
        baseutils.assert_text_equal_by_css(self,"OpenShift is a free, auto-scaling platform-as-a-service for Java, Ruby, PHP, Perl and Python applications.","#intro")
        baseutils.assert_element_present_by_css(self,"img.icon")
        baseutils.assert_text_equal_by_xpath(self,"WHY USE OPENSHIFT?","//section[@id='exposition']/header[2]/h1")
        baseutils.assert_text_equal_by_css(self,"Time of the essence? Just upload code and go!","header > h2")
        baseutils.assert_text_equal_by_xpath(self,"Whether you prefer the command line or a browser-based interface, OpenShift provides the fastest and easiest on-ramp to the cloud for free.",".//*[@id='fast']/p")
        baseutils.assert_text_equal_by_css(self,"Experiencing growing pains? OpenShift is tailored to meet your needs.","#free > header > h2") 
        baseutils.assert_text_equal_by_xpath(self,"OpenShift adapts to the varying needs of your app with auto-scaling built-in. No need for complicated scripts or additional coding.",".//*[@id='free']/p")
        baseutils.assert_element_present_by_css(self,"#free > img.icon")
        baseutils.assert_element_present_by_css(self,"#open > img.icon")
        baseutils.assert_text_equal_by_css(self,"Don't get locked in! Choose your languages, frameworks, middleware and clouds.","#open > header > h2")
        baseutils.assert_text_equal_by_css(self,"Keep your options open. OpenShift is based on Open Source with support for Java, PHP, Ruby, Python, and Perl and more.","#open > p")

    def test_da_check_home_twitter(self):
        baseutils.go_to_home(self)
        baseutils.assert_element_present_by_xpath(self,".//*[@id='latest']/a/img")
        baseutils.assert_element_present_by_xpath(self,".//*[@id='latest']/p")
    #    baseutils.assert_element_present_by_css(self,"li > img.avatar")
   #     baseutils.assert_element_present_by_css(self,"li > p.tweet")
        baseutils.assert_element_present_by_xpath(self,".//*[@id='retweets']/ul/li[*]/a/img")
        baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[*]/p")
      #  baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[2]/img")
      #  baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[2]/p")
      #  baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[3]/img")
      #  baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[4]/img")
      #  baseutils.assert_element_present_by_xpath(self,"//div[@id='retweets']/ul/li[4]/p")
      
        baseutils.scroll_by(self)
        if config.proxy:
               baseutils.click_element_by_xpath(self,"//*[@id='social_links']/a[1]")
               time.sleep(5)
               baseutils.check_title(self,"Twitter / Search - openshift")
               baseutils.go_back(self)
        else:  
               baseutils.assert_element_present_by_link_text(self,"More #openshift buzz")
               baseutils.assert_element_present_by_xpath(self,"//a[contains(text(),'Follow @OpenShift')]")
   
    def test_e_check_header_announcements(self):
        baseutils.go_to_home(self)
        baseutils.assert_element_present_by_xpath(self,".//*[@id='announcements']/ul/li[*]/a")
       # baseutils.is_element_displayed(self,By.XPATH,".//*[@id='announcements']/ul/li[1]/a")
        baseutils.click_element_by_xpath_wait(self,".//*[@id='announcements']/ul/li[*]/a")
        if self.driver.title == "OpenShift Newsletter Signup": pass
        elif self.driver.title == "Red Hat OpenShift (openshift) on Twitter":pass
        else: baseutils.assert_text_equal_by_xpath(self,"Got a cool app? Tell us about it!",".//*[@id='announcements']/ul/li[3]/a/div[1]")
        baseutils.check_title(self,"OpenShift Newsletter Signup")
        baseutils.go_back(self)
        baseutils.is_element_displayed(self,By.XPATH,".//*[@id='announcements']/ul/li[2]/a")
        baseutils.click_element_by_xpath_no_wait(self,".//*[@id='announcements']/ul/li[2]/a")
        time.sleep(5)
        baseutils.check_title(self,"Red Hat OpenShift (openshift) on Twitter")
        baseutils.go_back(self)
        baseutils.is_element_displayed(self,By.XPATH,"//aside[@id='announcements']/ul/li[3]/a")
        baseutils.assert_text_equal_by_xpath(self,"Got a cool app? Tell us about it!",".//*[@id='announcements']/ul/li[3]/a/div[1]")
       
    def test_f_check_home_footer(self):
        baseutils.go_to_home(self)
        baseutils.assert_text_equal_by_css(self,"News","li > header > h2")
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Announcements')]")
        baseutils.check_title(self,"News and Announcements | Red Hat OpenShift Community")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Blog')]")
        baseutils.check_title(self,"OpenShift Blog | Red Hat OpenShift Community")
        baseutils.go_back(self)
        if config.proxy:
               baseutils.click_element_by_xpath(self,"//a[@href='http://www.twitter.com/#!/openshift']")
               baseutils.check_title(self,"Red Hat OpenShift (openshift) on Twitter")
               baseutils.go_back(self)
        else: baseutils.assert_element_present_by_xpath(self,"//a[@href='http://www.twitter.com/#!/openshift']")
        baseutils.assert_text_equal_by_xpath(self,"Community","//li[2]/header/h2")
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Forum')]")
        baseutils.check_title(self,"Forums | Red Hat OpenShift Community")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Partner Program')]")
        baseutils.check_title(self,"OpenShift by Red Hat | Meet Our Partners")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[@href='http://webchat.freenode.net/?randomnick=1&channels=openshift&uio=d4']")
        baseutils.check_title(self,"Connection details - freenode Web IRC")
        baseutils.go_back(self)
        baseutils.assert_element_present_by_link_text(self,"Feedback")
        baseutils.assert_text_equal_by_xpath(self,"Legal","//li[3]/header/h2")
        baseutils.click_element_by_xpath(self,"//a[contains(@href, '/app/legal')]")
        baseutils.check_title(self,"OpenShift by Red Hat | Terms and Conditions")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(@href, '/app/legal/openshift_privacy')]")
        baseutils.check_title(self,"OpenShift by Red Hat | OpenShift Privacy Statement")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(@href, 'https://access.redhat.com/security/team/contact/')]")
        baseutils.check_title(self,"access.redhat.com | Security contacts and procedures")
        baseutils.go_back(self)
        baseutils.assert_text_equal_by_xpath(self,"Help","//li[4]/header/h2")
        baseutils.click_element_by_xpath(self,"//a[@href='http://www.redhat.com/openshift/faq']")
        baseutils.check_title(self,"Frequently Asked Questions | Red Hat OpenShift Community")
        baseutils.go_back(self)
        baseutils.assert_element_present_by_xpath(self,"//a[contains(text(),'Contact')]")


    def test_g_check_legal_links(self):
        baseutils.go_to_legal(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'OpenShift Preview Services Agreement')]")
        baseutils.check_title(self,"OpenShift by Red Hat | OpenShift Preview Services Agreement")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Acceptable Use Policy')]")
        baseutils.check_title(self,"OpenShift by Red Hat | Acceptable Use Policy")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Privacy Policy')]")
        baseutils.check_title(self,"OpenShift by Red Hat | OpenShift Privacy Statement")
        baseutils.go_back(self)
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Terms of Use')]")
        baseutils.check_title(self,"OpenShift by Red Hat | Terms of Use")
        baseutils.go_back(self)
        
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        

if __name__ == "__main__":
    unittest.main()
