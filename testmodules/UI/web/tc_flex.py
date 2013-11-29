from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class Flex(unittest.TestCase):
    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    def test_check_flex_about(self):
       # baseutils.go_to_home(self)
        baseutils.go_to_flex(self)
        baseutils.click_element_by_xpath(self,"//a[contains(@href, '#about')]")
        baseutils.assert_text_equal_by_css(self,"WHAT\'S FLEX?","#about > header > h1")
        baseutils.assert_text_equal_by_id(self,'OpenShift Flex is a browser-based platform-as-a-service for Java and PHP applications with auto-scaling, performance monitoring and application management capabilities built-in. There\'s two ways to get started:\nProvide your Amazon EC2 credentials in order to authorize OpenShift Flex to deploy cloud servers on your behalf.\nOR\nTake advantage of Red Hat\'s free trial offer. The free trial includes 30 days or 30 hours (whichever comes first) of free cloud resources from Amazon EC2.\nThe free trial is governed by the terms and conditions agreed to during the registration process for OpenShift.\nPlease Remember:\nOpenShift is in developer preview with no service level agreements.\nOpenShift should not be used for production purposes.\nAt Red Hat\'s discretion, it may decommission the resources it granted as part of the free trial without notification, explanation, or backup.\nUsers of OpenShift Flex are responsible for making backups of all their data\nAfter the expiration of the free trial, the resources and data on them will be deleted\nTo maximize the time of your free trial we recommend that you stop your cluster when not utilizing it',"flex-ways")
        baseutils.assert_text_equal_by_xpath(self,"Provide your Amazon EC2 credentials in order to authorize OpenShift Flex to deploy cloud servers on your behalf.","//div[@id='flex-ways']/ol/li/p")
        baseutils.assert_text_equal_by_id(self,"Take advantage of Red Hat's free trial offer. The free trial includes 30 days or 30 hours (whichever comes first) of free cloud resources from Amazon EC2.","offer")
        baseutils.assert_text_equal_by_css(self,"The free trial is governed by the terms and conditions agreed to during the registration process for OpenShift.","p.terms")
        baseutils.assert_text_equal_by_css(self,"OpenShift is in developer preview with no service level agreements.","ul.terms > li")
        baseutils.assert_text_equal_by_xpath(self,"OpenShift should not be used for production purposes.","//li[@id='free-flex']/ul/li[2]")
        baseutils.assert_text_equal_by_xpath(self,"At Red Hat's discretion, it may decommission the resources it granted as part of the free trial without notification, explanation, or backup.","//li[@id='free-flex']/ul/li[3]")
        baseutils.assert_text_equal_by_xpath(self,"To maximize the time of your free trial we recommend that you stop your cluster when not utilizing it","//li[@id='free-flex']/ul/li[6]")
        baseutils.assert_text_equal_by_css(self,"Build your Server Cluster and Application Stack","#about > h2")
        baseutils.assert_text_equal_by_css(self,"OpenShift Flex's wizard driven interface makes it easy to provision resources and build integrated application stacks.","#about > p")
        baseutils.assert_text_equal_by_xpath(self,"Deploy, Modify, Rollback and Restart Applications","//section[@id='about']/h2[2]")
        baseutils.assert_text_equal_by_xpath(self,"OpenShift Flex makes it easy to deploy your application, make modifications to code and components, version your changes and redeploy.","//section[@id='about']/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Monitoring and Auto-Scaling Built-in","//section[@id='about']/h2[3]")
        baseutils.assert_text_equal_by_xpath(self,"Without the use of agents or scripts, OpenShift Flex gives you end-to-end monitoring straight-out-of-box with configurable auto-scaling that lets you decide when and how to scale your application.","//section[@id='about']/p[3]")


    
    def test_check_flex_videos(self):
       # baseutils.go_to_home(self)
        baseutils.go_to_flex(self)
        baseutils.click_element_by_link_text(self,"Videos")
        baseutils.assert_text_equal_by_css(self,"OpenShift Flex Product Tour","div.product-video > h2")
        baseutils.assert_text_equal_by_css(self,"Issac Roth, PaaS Master - Red Hat","p.video-author.author")
        baseutils.assert_element_present_by_css(self,"img[alt=\"OpenShift Flex Product Tour\"]")
        baseutils.assert_text_equal_by_css(self,"This video walks you through the high level functionality of OpenShift Flex, covering provisioning, deploying, monitoring and scaling applications in the cloud.","p.video-description")
        baseutils.assert_text_equal_by_xpath(self,"What are people saying about OpenShift?","//section[@id='videos']/div[2]/h2")
        baseutils.assert_text_equal_by_xpath(self,"Developers, ISVs, customers and partners","//section[@id='videos']/div[2]/p")
        baseutils.assert_element_present_by_xpath(self,"//img[@alt='Developers, ISVs, customers and partners']")
        baseutils.assert_text_equal_by_xpath(self,"This video shows you what developers, ISVs, customers and partners are saying about Red Hat's exciting new OpenShift PaaS.","//section[@id='videos']/div[2]/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Deploying a Mongo Driven Application on OpenShift Flex","//section[@id='videos']/div[3]/h3")
        baseutils.assert_text_equal_by_xpath(self,"David Blado","//section[@id='videos']/div[3]/p")
        baseutils.assert_element_present_by_xpath(self,"//section[@id='videos']/div[3]/div/iframe")
        baseutils.assert_text_equal_by_xpath(self,"This video walks a user through deploying an application on OpenShift Flex that uses MongoDB as its database backend. Complete with performance and log management demo!","//section[@id='videos']/div[3]/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Deploying a Seam Application on OpenShift Flex","//section[@id='videos']/div[4]/h3")
        baseutils.assert_element_present_by_xpath(self,"//section[@id='videos']/div[4]/div/iframe")
        baseutils.assert_text_equal_by_xpath(self,"This video walks a user through deploying a Seam application on OpenShift Flex. Complete with a performance and log management demo!","//section[@id='videos']/div[4]/p[2]")
        baseutils.click_element_by_xpath(self,"//a[contains(text(),'Watch more videos')]")
        baseutils.check_title(self,"Videos | Red Hat OpenShift Community")

    def test_check_flex_navi_a_Sign(self):
        #baseutils.go_to_home(self)
        baseutils.go_to_flex(self)
        baseutils.click_element_by_link_text(self,"Sign up to try Flex!")
        baseutils.assert_text_equal_by_css(self,"Sign up for OpenShift - it's Easy!","#signup > header > h1")
    
    def test_z_check_flex_navi_b_Documentation(self):
        baseutils.go_to_flex(self)
#       baseutils.click_element_by_css_no_wait(self,"#signup > a.close_button > img")
        baseutils.click_element_by_link_text(self,"Documentation")
        baseutils.check_title(self,"User Guide")
#        baseutils.assert_text_equal_by_css(self,"OpenShift Flex","div.product.expanded > span.product")

    def test_check_flex_navi_c_Forum(self):
        baseutils.go_to_flex(self)
        baseutils.click_element_by_link_text(self,"Forum")
        baseutils.check_title(self,"Flex | Red Hat OpenShift Community")

    def test_check_flex_quickstart(self):
       # baseutils.go_to_home(self)
        baseutils.go_to_flex(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Flex")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_css(self,"QUICKSTART","#quickstart > header > h1")
        baseutils.assert_text_equal_by_css(self,"Clicking on the link below will take you to the Flex application where you can start migrating your applications to the cloud.","#quickstart > p")
        baseutils.assert_element_present_by_xpath(self,"//a[contains(@href, '/app/flex_redirect')]")
        baseutils.assert_element_present_by_xpath(self,"//a[contains(text(),'Flex Console')]")

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()
