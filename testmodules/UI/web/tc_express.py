from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import unittest, time, re
import baseutils
import config
import HTMLTestRunner

class Express(unittest.TestCase):

    def setUp(self):
        self.driver = ""
        self.base_url = ""
        self.profile = ""
        self.verificationErrors = []
        baseutils.initiate(self)
    
    def test_check_express_about(self):
       # baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.assert_text_equal_by_css(self,"WHAT\'S EXPRESS?","#about > header > h1")
        baseutils.assert_text_equal_by_xpath(self,"Looking for a fast on-ramp to the Cloud? Get Java, Ruby, PHP, Perl and Python apps in the cloud with the command-line and Git in just a few mintes.","//*[@id='about']/p[1]")
        baseutils.assert_text_equal_by_xpath(self,"Install","//*[@id='about']/h2[1]")
        baseutils.assert_text_equal_by_xpath(self,"Download and install the OpenShift Express client tools so you can deploy and manage your application in the cloud.","//section[@id='about']/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Create","//*[@id='about']/h2[2]")
        baseutils.assert_text_equal_by_xpath(self,"Create a subdomain for your application and clone the Git master repository from the cloud.","//section[@id='about']/p[3]") 
        baseutils.assert_text_equal_by_xpath(self,"Deploy","//*[@id='about']/h2[3]")
        baseutils.assert_text_equal_by_xpath(self,"Add your application code to the Git repository and push to the cloud. Congratulations, your application is live!","//section[@id='about']/p[4]")

    def test_check_express_videos(self):
      #  baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.click_element_by_link_text(self,"Videos")
        baseutils.assert_text_equal_by_css(self,"EXPRESS VIDEOS","#videos > header > h1")
        baseutils.assert_text_equal_by_xpath(self,"OpenShift Express Product Tour","//*[@id='videos']/div[1]/header/h2")
        baseutils.assert_text_equal_by_css(self,"Mike McGrath, Cloud Architect - Red Hat","p.video-author.author")
        baseutils.assert_element_present_by_xpath(self,"//section[@id='videos']/div/div/a/img")
        baseutils.assert_text_equal_by_css(self,"This video walks you through the high level functionality of OpenShift Express, from installing the client tools, creating a subdomain to deploying your app onto the cloud.","p.video-description")
        baseutils.assert_text_equal_by_xpath(self,"Mobile App Deployment to Express w/ Appcelerator","//section[@id='videos']/div[2]/header/h2")
        baseutils.assert_text_equal_by_xpath(self,"Nolan Wright, CTO and Co-Founder - Appcelerator","//section[@id='videos']/div[2]/p")
        baseutils.assert_element_present_by_xpath(self,"//section[@id='videos']/div[2]/div/a/img")
        baseutils.assert_text_equal_by_xpath(self,"This video shows you just how easy it is to develop and deploy a mobile app onto OpenShift Express with Appcelerator's Mobile Cloud Platform","//section[@id='videos']/div[2]/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Deploying to OpenShift PaaS with the eXo Cloud IDE","//section[@id='videos']/div[3]/header/h2")
        baseutils.assert_text_equal_by_xpath(self,"Mark Downey, Developer Advocate","//section[@id='videos']/div[3]/p")
        baseutils.assert_element_present_by_xpath(self,"//section[@id='videos']/div[3]/div/a/img")
        baseutils.assert_text_equal_by_xpath(self,"This video demonstrates how easy it is to use the eXo cloud IDE to develop and deploy applications on OpenShift.","//section[@id='videos']/div[3]/p[2]")
        baseutils.click_element_by_link_text(self,"Watch more videos")
        baseutils.check_title(self,"Videos | Red Hat OpenShift Community")


    
    def test_check_express_navi(self):
     #   baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.click_element_by_xpath(self,"//*[@id='account']/ul/li/a")
        baseutils.assert_text_equal_by_css(self,"Sign up for OpenShift - it's Easy!","#signup > header > h1")
        baseutils.click_element_by_css_no_wait(self,"#signup > a.close_button > img")
        baseutils.click_element_by_link_text(self,"Documentation")
        baseutils.assert_text_equal_by_css(self,"OpenShift Express","span.productname")
        baseutils.check_title(self,"User Guide")
        baseutils.go_back(self)
        baseutils.click_element_by_link_text(self,"Forum")
        baseutils.check_title(self,"Express | Red Hat OpenShift Community")
   

    def test_a_check_express_quick_start_links(self):
        #baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_xpath(self,"QUICKSTART",".//*[@id='quickstart']/header/h1")
        #baseutils.click_element_by_css(self,"#toc > li > a")
        #baseutils.assert_text_equal_by_xpath(self,"Install the client tools","//h3")
        time.sleep(3)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,".//*[@id='toc']/li[3]/a")
        baseutils.scroll_by(self)
        baseutils.assert_text_equal_by_xpath(self,"Create your first application","//li[@id='create_application']/h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Make a change, publish")
        baseutils.scroll_by(self)
        baseutils.assert_text_equal_by_xpath(self,"Make a change, publish","//li[@id='publish']/h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Next steps")
        baseutils.assert_text_equal_by_css(self,"Next steps","#next_steps > h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Red Hat Enterprise Linux or Fedora")
        baseutils.assert_text_equal_by_xpath(self,"Red Hat Enterprise Linux or Fedora","//li[@id='rhel']/h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Other Linux Systems")
        baseutils.assert_text_equal_by_css(self,"Other Linuxes","#other_nix > h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Mac OS X")
        baseutils.assert_text_equal_by_css(self,"Mac","#mac > h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Windows")
        baseutils.assert_text_equal_by_css(self,"Windows","#win > h4")
        time.sleep(5)
        baseutils.scroll_bar(self)
        if config.proxy :
              baseutils.click_element_by_link_text(self,"openshift.repo")
              baseutils.go_back(self)
              #baseutils.go_to_express_quick_start(self)
              time.sleep(5)
        else :
              baseutils.assert_element_present_by_link_text(self,"openshift.repo")
        
        baseutils.scroll_bar(self)
        baseutils.click_element_by_xpath(self,".//*[@id='rhel']/aside/p[1]/a")
        baseutils.check_title(self,"Sudo Main Page")
        baseutils.go_back(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Installing OpenShift client tools video walkthrough")
        baseutils.check_title(self,"OpenShift Express -- Install the OpenShift Express Client Tools - YouTube")
        baseutils.go_back(self)
        baseutils.scroll_bar(self)
        baseutils.click_element_by_link_text(self,"Full Xcode Suite -- or --")
        baseutils.check_title(self,"Download Xcode 4 - Apple Developer")
        baseutils.go_back(self)
        self.driver.execute_script("window.scrollTo(0,0);")
        baseutils.click_element_by_link_text(self,"git for OS X")
        baseutils.check_title(self,"git-osx-installer - OSX Installer for Git - Google Project Hosting")
        baseutils.go_back(self)
        self.driver.execute_script("window.scrollTo(0,0);")
        baseutils.click_element_by_link_text(self,"Cygwin")
        baseutils.check_title(self,"Cygwin")
        baseutils.go_back(self)
        self.driver.execute_script("window.scrollTo(0,0);")
        time.sleep(5)
        self.driver.execute_script("window.scrollTo(0,0);")
        baseutils.click_element_by_xpath(self,"//div[@id='domain_link']/a")
        baseutils.assert_text_equal_by_css(self,"Control Panel","section.main > header > h1")
        baseutils.go_back(self)
        self.driver.execute_script("window.scrollTo(0, 0);")
        if config.proxy :
              baseutils.click_element_by_link_text(self,"Creating a application video walkthrough")
              baseutils.check_title(self,"OpenShift Express -- Create and Define your Application - YouTube")
              baseutils.go_back(self)
              self.driver.execute_script("window.scrollTo(0,0);")
              baseutils.click_element_by_link_text(self,"Deploying an application video walkthrough")
              baseutils.check_title(self,"OpenShift Express -- Deploy to the Cloud - YouTube")
              baseutils.go_back(self)
              self.driver.execute_script("window.scrollTo(0,0);")
        else :
              baseutils.assert_element_present_by_link_text(self,"Creating a application video walkthrough")
              baseutils.assert_element_present_by_link_text(self,"Deploying an application video walkthrough")
        
    
    def test_aa_check_express_quick_start_links_a(self):
        baseutils.go_to_express(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_xpath(self,"QUICKSTART",".//*[@id='quickstart']/header/h1")
        baseutils.click_element_by_link_text(self,"TurboGears2 Python framework")
        baseutils.assert_text_equal_by_xpath(self,"Deploying TurboGears2 Python web framework using Express","//section/div[2]/h2")
#        baseutils.check_title(self,"Deploying TurboGears2 Python web framework using Express | Red Hat Openshift Community")
#        baseutils.go_back(self)
#        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        baseutils.go_to_express(self)
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_xpath(self,"QUICKSTART",".//*[@id='quickstart']/header/h1")
        baseutils.click_element_by_link_text(self,"Pyramid Python framework")
        baseutils.assert_element_present_by_link_text(self,"http://pylonsproject.org/projects/pyramid/about")
#        baseutils.assert_text_equal_by_xpath(self,"OpenShift > Community > Blogs > Deploying a Pyramid application in a virtual Python WSGI environment on Red Hat OpenShift Express","//section[@id='about']/div")
        baseutils.go_back(self)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        baseutils.assert_element_present_by_xpath(self,"//a[contains(@href, 'https://www.redhat.com/openshift/sites/default/files/documents/RHOS_Express_Getting_Started_w_Drupal.pdf')]")
        baseutils.assert_element_present_by_xpath(self,"//a[contains(@href, 'https://www.redhat.com/openshift/sites/default/files/documents/RHOS_Express_Getting_Started_w_MediaWiki.pdf')]")
        baseutils.click_element_by_xpath(self,"//li[@id='next_steps']/ul/li/a")
        baseutils.assert_text_equal_by_xpath(self,"Videos","//section[@id='about']/div[2]/div[2]/h2")
#        baseutils.check_title(self,"Videos | Red Hat Openshift Community")
        baseutils.go_to_express(self)
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_xpath(self,"QUICKSTART",".//*[@id='quickstart']/header/h1")
#        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        baseutils.click_element_by_link_text(self,"Technical Documentation")
        baseutils.assert_text_equal_by_xpath(self,"User Guide","//div[@id='id3774062']/div/div/div[2]/h1")
#        baseutils.check_title(self,"User Guide")
        baseutils.go_back(self)
        baseutils.click_element_by_link_text(self,"Support Forums")
        baseutils.assert_text_equal_by_xpath(self,"FORUM","//section[@id='about']/div[2]/div/table/thead/tr/th")
#        baseutils.check_title(self,"Forums | Red Hat Openshift Community")
        baseutils.go_back(self)


    
    def test_check_express_quick_start_contents(self):
        #baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_xpath(self,"Install the client tools","//*[@id='install_client_tools']/h3")
        baseutils.assert_text_equal_by_xpath(self,"Red Hat Enterprise Linux or Fedora","//li[@id='rhel']/h4")
        baseutils.assert_text_equal_by_css(self,"Prerequisites","h5")
        baseutils.assert_text_equal_by_xpath(self,"RHEL 6 and up or Fedora 14 and up.","//li[@id='rhel']/ol/li/ul/li")
        baseutils.assert_text_equal_by_xpath(self,"Root or sudoer access","//li[@id='rhel']/ol/li/ul/li[2]")
        baseutils.assert_text_equal_by_xpath(self,"Download the express repo file openshift.repo","//li[@id='rhel']/ol/li[2]")
        baseutils.assert_text_equal_by_xpath(self,'Move the openshift.repo file to your /etc/yum.repos.d/ directory.\n$ sudo mv ~/Downloads/openshift.repo /etc/yum.repos.d/\nReplace \'~/Downloads/openshift.repo\' with the location to which you saved the repo file.',"//li[@id='rhel']/ol/li[3]")
        baseutils.assert_text_equal_by_xpath(self,"$ sudo mv ~/Downloads/openshift.repo /etc/yum.repos.d/","//li[@id='rhel']/ol/li[3]/pre")
        baseutils.assert_text_equal_by_xpath(self,'Install the client tools:\n$ sudo yum install rhc',"//li[@id='rhel']/ol/li[4]")
        baseutils.assert_text_equal_by_css(self,"The sudo command will only work if your user is listed in the sudoers file. For more information on setting up sudo, see http://www.gratisoft.us/sudo/sudo.html.","aside > p")
        baseutils.assert_text_equal_by_xpath(self,"As an alternative to sudo, you can activate a root terminal with the su command and the root password. In that case, omit sudo from the given commands. Don't forget to close your root terminal when you're done!","//li[@id='rhel']/aside/p[2]")
        baseutils.assert_text_equal_by_css(self,"Other Linuxes","#other_nix > h4")
        baseutils.assert_text_equal_by_css(self,"Prerequisites","#other_nix > ol > li.prereqs > h5")
        baseutils.assert_text_equal_by_css(self,"Root access","#other_nix > ol > li.prereqs > ul > li")
        baseutils.assert_text_equal_by_xpath(self,"Ruby 1.8 or higher installed or available to be installed","//li[@id='other_nix']/ol/li/ul/li[2]")
        baseutils.assert_text_equal_by_xpath(self,"Install the required packages: git, ruby, rubygems, and the ruby 1.8 development package.","//li[@id='other_nix']/ol/li[2]")
        baseutils.assert_text_equal_by_xpath(self,"Install the gem:\n$ su -c \'gem install rhc\'","//li[@id='other_nix']/ol/li[3]")
        baseutils.assert_text_equal_by_css(self,"Mac","#mac > h4")
        baseutils.assert_text_equal_by_css(self,"Prerequisites","#mac > ol > li.prereqs > h5")
        baseutils.assert_text_equal_by_xpath(self,"Full Xcode Suite -- or --","//li[3]/ol/li/ul/li/ol/li/a")
        baseutils.assert_text_equal_by_xpath(self,"git for OS X","//li[3]/ol/li/ul/li/ol/li[2]/a")
        baseutils.assert_text_equal_by_css(self,"Windows","#win > h4")
        baseutils.assert_text_equal_by_css(self,"Prerequisites","#win > ol > li.prereqs > h5")
        baseutils.assert_text_equal_by_xpath(self,'The following optional cygwin components\nopenssh\nruby\nmake\ngcc\ngit',"//li[@id='win']/ol/li/ul/li[2]")
        baseutils.assert_text_equal_by_xpath(self,"Download and extract rubygems from http://rubyforge.org/projects/rubygems","//li[@id='win']/ol/li[2]")
        baseutils.assert_text_equal_by_xpath(self,'From within cygwin run:\n$ ruby <path_to_extracted_rubygems>/setup.rb install',"//li[@id='win']/ol/li[3]")
        baseutils.assert_text_equal_by_xpath(self,'Install the gem:\n$ gem install rhc',"//li[@id='win']/ol/li[4]")
        baseutils.assert_text_equal_by_css(self,"Create a domain name","#create_domain_name > h4")
        baseutils.assert_text_equal_by_css(self,"Using your OpenShift login and password, call rhc-create-domain to create a unique domain name for your applications.","div.main > p")
    
    def test_check_express_quick_start_contents_b(self):
        #baseutils.go_to_home(self)
        baseutils.go_to_express(self)
        baseutils.go_to_signin(self)
        baseutils.login(self,config.granted_user[0],config.granted_user[1])
        baseutils.check_title(self,"OpenShift by Red Hat | Express")
        baseutils.click_element_by_link_text(self,"Quickstart")
        baseutils.assert_text_equal_by_css(self,'$ rhc-create-domain -n mydomain -l rhlogin\nPassword: (type... type... type...)',"div.main > pre")
        baseutils.assert_text_equal_by_css(self,"OpenShift domain names make up part of your app's url. They are also unique across all OpenShift users, so choose wisely, and be creative!","div.main > aside > p")
        baseutils.assert_text_equal_by_xpath(self,"The rhc-create-domain command will create a configuration file - <your home directory>/.openshift/express.conf - which sets up a default login.","//li[@id='create_domain_name']/div/aside[2]/p")
        baseutils.assert_text_equal_by_css(self,"Why wait?","#domain_link > h4")
        baseutils.assert_text_equal_by_css(self, "Reserve your amazing domain name right now!","#domain_link > h5")
        baseutils.assert_text_equal_by_css(self,"All you need is an ssh keypair and a unique name.","#domain_link > p")
        baseutils.assert_text_equal_by_css(self,"Create your first application","#create_application > h4")
        baseutils.assert_text_equal_by_css(self,"Now you can create an application.","#create_application > p")
        baseutils.assert_text_equal_by_css(self,'$ rhc-create-app -a myapp -t php-5.3\nPassword: (type... type... type...)',"#create_application > pre")
     #   baseutils.assert_text_equal_by_xpath(self,"This will create a remote git repository for your application, and clone it locally in your current directory.","//li[@id='create_application']/p[2]")
        baseutils.assert_text_equal_by_css(self,"OpenShift offers many application stacks. Run rhc-create-app -h to see all of your options.","#create_application > aside > p")
        baseutils.assert_text_equal_by_xpath(self,"Your application's domain name will be <your app name>-<your domain name>.rhcloud.com. So, the application created by the example commands would be located at myapp-mydomain.rhcloud.com","//li[@id='create_application']/aside[2]/p")
        baseutils.assert_text_equal_by_css(self,"Make a change, publish","#publish > h4")
        baseutils.assert_text_equal_by_css(self,"As we all know, getting an application running is only the first step. Now you are on the road to making it your own. Here's an example for the php framework.","#publish > p")
      #  baseutils.assert_text_equal_by_xpath(self,"Now, check your URL - your change will be live.","//li[@id='publish']/p[2]")
        baseutils.assert_text_equal_by_xpath(self,"Use whichever ide or editor works best for you. Chances are, it'll have git support. Even if it doesn't, you're just two simple commands away from glory!","//li[@id='publish']/aside[2]/p")
        baseutils.assert_text_equal_by_xpath(self,"Checkout these great guides for deploying popular frameworks on OpenShift:","//li[@id='publish']/aside[3]/p")
        baseutils.assert_text_equal_by_css(self,"Next steps","#next_steps > h4")
        baseutils.assert_text_equal_by_css(self,"While this has gotten you started, there is a lot more information out there to really get you going. Check out the following pages for videos, blogs, and tutorials:","#next_steps > p")
        baseutils.assert_text_equal_by_css(self,'$ cd myapp\n$ vim php/index.php\n(Make a change...  :wq)\n$ git commit -a -m \"My first change\"\n$ git push',"#publish > pre")
    
        
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
    #HTMLTestRunner.main()
