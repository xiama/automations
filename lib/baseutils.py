from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
import unittest, time, re
import logging
import config
import ConfigParser




logging.basicConfig(filename='seleniumtest.log',format='%(levelname)s:%(message)s',level=logging.DEBUG)
#url="https://stg.openshift.redhat.com/"
#logging.info('So should this')
#logging.warning('And this, too')

def initiate(classself):
	tmp_browser=config.browser.strip().lower()
	if tmp_browser == 'firefox':
		if config.proxy == False:
			classself.driver = webdriver.Firefox()
			if config.browserpath != '0':
				    classself.binary = FirefoxBinary(config.browserpath)
				    classself.driver = webdriver.Firefox(classself.binary)
		elif config.proxy == True:
			classself.profile=webdriver.FirefoxProfile()
			classself.profile.set_preference("network.proxy.type", 1)
			classself.profile.set_preference("network.proxy.http", "file.sjc.redhat.com")
			classself.profile.set_preference("network.proxy.http_port", 3128)
			classself.profile.set_preference("network.proxy.ssl", "file.sjc.redhat.com")
			classself.profile.set_preference("network.proxy.ssl_port", 3128)
			classself.driver = webdriver.Firefox(classself.profile)
			if config.browserpath !='0':
				    classself.binary = FirefoxBinary(config.browserpath)
				    classself.driver = webdriver.Firefox(classself.profile,classself.binary)
	elif tmp_browser == 'ie':
		classself.driver = webdriver.Ie()
	elif tmp_browser == 'chrome':
		classself.driver = webdriver.Chrome()
	else :
	  logging.warning(tmp_browser+'is not supported')
	   
	if config.browserpath != '0' and tmp_browser == 'chrome':
		classself.driver = webdriver.Chrome(executable_path=config.browserpath)
	classself.driver.implicitly_wait(20)
	classself.base_url =config.url
	classself.verificationErrors = []
#	basedriver=classself.driver


def is_element_present(classself, how, what):
    try: classself.driver.find_element(by=how, value=what)
    except NoSuchElementException, e: return False
    return True

def assert_contain_text_by_id(classself,text,id_name):
    _retry=120
    while(_retry>0):
         _retry=_retry-1
         time.sleep(1)
         try:
 #           if classself.driver.find_element_by_id(id_name).text.find(text) != -1 : break
            if text in classself.driver.find_element_by_id(id_name).text : break
         except: pass
         time.sleep(1)
    else:classself.fail("the text is not displayed yet")

def assert_contain_text_by_css(classself,text,css_name):
    _retry=120
    while(_retry>0):
         _retry=_retry-1
         time.sleep(1)
         try:
#            if classself.driver.find_element_by_css(css_name).text.find(text) != -1 : break
            if text in classself.driver.find_element_by_css(css_name).text : break
         except: pass
         time.sleep(1)
    else:classself.fail("the text is not displayed yet")

def assert_contain_text_by_xpath(classself,text,xpath):
    _retry=60
    while(_retry>0):
         _retry=_retry-1
         time.sleep(1)
         try:
 #           if classself.driver.find_element_by_xpath(xpath).text.find(text) != -1 : break
            if text in classself.driver.find_element_by_xpath(xpath).text : break
         except: pass
         time.sleep(1)
    else:classself.fail("the text is not displayed yet")


def is_element_displayed(classself,how,what):
    try:classself.assert_true(classself.driver.find_element(by=how,value=what).is_displayed(),what+" is not displayed")
    except AssertionError as e: classself.verificationErrors.append(str(e))

def is_element_hidden(classself,how,what):
    try:classself.assert_false(classself.driver.find_element(by=how,value=what).is_displayed())
    except AssertionError as e: classself.verificationErrors.append(str(e))

def wait_element_not_displayed_by_id(classself,id_name):
    try:
       WebDriverWait(classself.driver,120).until(classself.driver.find_element_by_id(id_name))
       classself.assert_true(classself.driver.find_element_by_id(id_name).is_displayed())
    except AssertionError as e: classself.verificationErrors.append(str(e))

def is_text_displayed(classself,text,css):
    try:
       WebDriverWait(classself.driver, 100).until(classself.driver.find_element_by_css_selector(css))
       classself.assert_true( text == classself.driver.find_element_by_css_selector(css).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))

def is_text_displayed_by_id(classself,text,id_name):
    try:
       WebDriverWait(classself.driver, 100).until(classself.driver.find_element_by_id(id_name))
       classself.assert_true( text == classself.driver.find_element_by_id(id_name).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))



def check_title(classself,title):
    time.sleep(5)
    for i in range(60):
        try:
            if title == classself.driver.title: break
        except: pass
        time.sleep(1)
    else:classself.fail("time out,%s is not equal %s" %(title,classself.driver.title));


def assert_element_present_by_css(classself,css):
	try: classself.assert_true(is_element_present(classself,By.CSS_SELECTOR,css))
	except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_not_present_by_css(classself,css):
        try: classself.assert_false(is_element_present(classself,By.CSS_SELECTOR,css))
        except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_id(classself,idname):
	try: classself.assert_true(is_element_present(classself,By.ID,idname))
	except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_not_present_by_id(classself,idname):
        try: classself.assert_false(is_element_present(classself,By.ID,idname))
        except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_xpath(classself,xpath):
	try: classself.assert_true(is_element_present(classself,By.XPATH,xpath))
	except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_link_text(classself,link_text):
    try: classself.assert_true(is_element_present(classself,By.LINK_TEXT,link_text))
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_partial_link_text(classself,partial_link_text):
    try: classself.assert_true(is_element_present(classself,By.PARTIAL_LINK_TEXT ,partial_link_text))
    except AssertionError as e: classself.verificationErrors.append(str(e))


def assert_element_present_by_name(classself,name):
    try: classself.assert_true(is_element_present(classself,By.NAME ,name))
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_class_name(classself,class_name):
    try: classself.assert_true(is_element_present(classself,By.CLASS_NAME ,class_name))
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_element_present_by_tag_name(classself,tag_name):
    try: classself.assert_true(is_element_present(classself,By.TAG_NAME ,tag_name))
    except AssertionError as e: classself.verificationErrors.append(str(e))


def assert_element_present(classself,how,what):
    try: classself.assert_true(is_element_present(classself,how ,what))
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_text_equal_by_css(classself,text,css,msg=None):
    try: classself.assertEqual(text,classself.driver.find_element_by_css_selector(css).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))


def assert_text_equal_by_xpath(classself,text,xpath):
    try: classself.assertEqual(text,classself.driver.find_element_by_xpath(xpath).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_text_equal_by_partial_link_text(classself,text,partial_link_text):
    try: classself.assertEqual(text,classself.driver.find_element_by_partial_link_text(partial_link_text).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))


def assert_text_equal_by_id(classself,text,id_name):
    try: classself.assertEqual(text,classself.driver.find_element_by_id(id_name).text)
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_text_regexp_match_by_css(classself,text,css):
    try: classself.assertRegexpMatches(classself.driver.find_element_by_css_selector(css).text,text)
    except AssertionError as e: classself.verificationErrors.append(str(e))

def assert_value_equal_by_id(classself,value,id_name):
    try: classself.assertEqual(value,classself.driver.find_element_by_id(id_name).get_attribute("value"))
    except AssertionError as e: classself.verificationErrors.append(str(e))

def is_text_equal_by_css(classself,text,css):
    for i in range(60):
        try:
            if text == classself.driver.find_element_by_css_selector(css).text: break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not equal to %s" %(text,classself.driver.find_element_by_css_selector(css).text))

def is_text_equal_by_xpath(classself,text,xpath):
    for i in range(60):
        try:
            if text == classself.driver.find_element_by_xpath(xpath).text: break
        except: pass
        time.sleep(1)
    else:classself.fail("time out,%s is not equal to %s" %(text,classself.driver.find_element_by_xpath(xpath).text))



    

#    for i in range(240):
#        try:
#            if not classself.driver.find_element_by_id(id_name).is_displayed(): break
#        except: pass
#        time.sleep(1)
#    else: classself.fail("time out")

#def wait_element_not_displayed_by_id(classself,id_name):
 #   wait_element_not_present(classself,By.ID,id_name)
 

def wait_element_present_by_xpath(classself,xpath):
    for i in range(60):
        try:
            if is_element_present(classself,By.XPATH, xpath): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(xpath))

def wait_element_not_present_by_xpath(classself,xpath):
    for i in range(60):
        try:
            if not is_element_present(classself,By.XPATH, xpath): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is present"%(xpath))

def wait_element_present_by_css(classself,css):
    for i in range(60):
        try:
            if is_element_present(classself,By.CSS_SELECTOR, css): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(css))

def wait_element_present_by_id(classself,idname):
    for i in range(60):
        try:
            if is_element_present(classself,By.ID, idname): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(idname))

def wait_element_present_by_class(classself,class_name):
    for i in range(60):
        try:
            if is_element_present(classself,By.CLASS_NAME,class_name): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(class_name))

def wait_element_present_by_name(classself,name):
    for i in range(60):
        try:
            if is_element_present(classself,By.NAME,name): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(name))

def wait_element_present_by_link_text(classself,name):
    for i in range(60):
        try:
            if is_element_present(classself,By.LINK_TEXT,name): break
        except: pass
        time.sleep(1)
    else: classself.fail("time out,%s is not present"%(name))


def click_element_by_css(classself,css):
    wait_element_present_by_css(classself,css)
    classself.driver.find_element_by_css_selector(css).click()

def click_element_by_id(classself,id_name):
    wait_element_present_by_id(classself,id_name)
    classself.driver.find_element_by_id(id_name).click()

def click_element_by_xpath(classself,xpath):
    wait_element_present_by_xpath(classself,xpath)
    classself.driver.find_element_by_xpath(xpath).click()

def click_element_by_xpath_wait(classself,xpath):
    wait_element_present_by_xpath(classself,xpath)
    classself.driver.find_element_by_xpath(xpath).click()
    time.sleep(8)

def click_element_by_link_text(classself,link_text):
    wait_element_present_by_link_text(classself,link_text)
    classself.driver.find_element_by_link_text(link_text).click()
    

def click_element_by_class(classself,class_name):
    wait_element_present_by_class(classself,class_name)
    classself.driver.find_element_by_class_name(class_name).click()


def click_element_by_css_no_wait(classself,css):
    classself.driver.find_element_by_css_selector(css).click()

def click_element_by_id_no_wait(classself,id_name):
    classself.driver.find_element_by_id(id_name).click()

def click_element_by_xpath_no_wait(classself,xpath):
    classself.driver.find_element_by_xpath(xpath).click()

def click_element_by_partial_link_text_no_wait(classself,partial_link_text):
    classself.driver.find_element_by_partial_link_text(partial_link_text).click()

def go_to_home(classself):
#    basedriver=classself.driver
    classself.driver.get(classself.base_url+"/app/")
#    time.sleep(10)
    check_title(classself,"OpenShift by Red Hat")
    

def go_to_express(classself):
    express_page=classself.base_url+"/app/express"
    classself.driver.get(express_page)
    '''
#    go_to_home(classself)
    click_element_by_xpath(classself,"//a[contains(text(),'Cloud Services')]")
    '''
    check_title(classself,"OpenShift by Red Hat | Express")

def go_to_express_quick_start(classself):
    quick_start=classself.base_url+"/app/express#quickstart"
    classself.driver.get(quick_start)


def go_to_flex(classself):
#    go_to_home(classself)
    flex_page=classself.base_url+"/app/flex"
    classself.driver.get(flex_page)
    '''
    click_element_by_xpath(classself,"//a[contains(text(),'Cloud Services')]")
    check_title(classself,"OpenShift by Red Hat | Express")
    scroll_bar(classself)
    click_element_by_xpath(classself,"//a[contains(text(),'Flex')]")
    '''
    check_title(classself,"OpenShift by Red Hat | Flex")


def go_to_power(classself):
#   go_to_home(classself)
    power_page=classself.base_url+"/app/power"
    classself.driver.get(power_page)
    '''
    click_element_by_xpath(classself,"//a[contains(text(),'Cloud Services')]")
    check_title(classself,"OpenShift by Red Hat | Express")
    scroll_bar(classself)
    click_element_by_xpath(classself,"//a[contains(text(),'Power')]")
    '''
    check_title(classself,"OpenShift by Red Hat | Power")

def go_to_signin(classself):
    #click_element_by_class(classself,"sign_in")
 #   time.sleep(5)
    click_element_by_link_text(classself,"Sign in")
    #is_element_displayed(classself,By.ID,"login-form")
    is_element_displayed(classself,By.ID,"login_input")


def go_to_signup(classself):
   # scroll_bar(classself)
    #signup_page=classself.base_url+"/app/user/new/express"
    go_to_home(classself)
    scroll_to_bottom(classself)
    click_element_by_xpath(classself,".//*[@id='bottom_signup']/div/a")
    time.sleep(2)
    if not is_element_displayed(classself,By.ID,"signup"):
       click_element_by_xpath(classself,".//*[@id='bottom_signup']/div/a")
    #click_element_by_link_text(classself,"Sign up and try it")
    #click_element_by_xpath(classself,".//*[@id='opener']/div/a")
#    click_element_by_css(classself,"a.button.sign_up")
    is_element_displayed(classself,By.ID,"signup")



def go_to_express_console(classself):
#    basedriver=classself.driver
    classself.driver.get(classself.base_url+"/app/dashboard")
#    time.sleep(10)
    #check_title(classself,"OpenShift by Red Hat")


def go_to_partners(classself):
    partner_page=classself.base_url+"/app/partners"
    classself.driver.get(partner_page)
    check_title(classself,"OpenShift by Red Hat | Meet Our Partners")

def go_to_legal(classself):
    legal_page=classself.base_url+"/app/legal"
    classself.driver.get(legal_page)
    check_title(classself,"OpenShift by Red Hat | Terms and Conditions")
    classself.driver.execute_script("window.scrollTo(0, 0);")


def go_to_platformoverview(classself):
    go_to_home(classself)
    click_element_by_link_text(classself,"Platform Overview")
    check_title(classself,"OpenShift by Red Hat | Cloud Platform")
    
def go_back(classself):
    classself.driver.back()
    time.sleep(5)

def input_by_id(classself,id_name,input_content):
    classself.driver.find_element_by_id(id_name).clear()
    classself.driver.find_element_by_id(id_name).send_keys(input_content)


def input_by_name(classself,name,input_content):
    classself.driver.find_element_by_name(name).clear()
    classself.driver.find_element_by_name(name).send_keys(input_content)

def input_by_xpath(classself,xpath,input_content):
    classself.driver.find_element_by_xpath(xpath).clear()
    classself.driver.find_element_by_xpath(xpath).send_keys(input_content)


def set_captcha(classself):
    classself.driver.execute_script("""
    var input_ele = window.document.createElement('input');
    input_ele.setAttribute('type','hidden');
    input_ele.setAttribute('name','captcha_secret');
    input_ele.setAttribute('value','zvw5LiixMB0I4mjk06aR');
    var dialog = window.document.getElementById('signup');
    dialog.getElementsByTagName('form')[0].appendChild(input_ele);"""
    )



def register_a_user(classself,username,password,confirmpassword="0",captcha=False):
    if confirmpassword == "0":
       confirmpassword =password
    #wait_element_present_by_id(classself,"web_user_email_address")
    input_by_id(classself,"web_user_email_address",username)
    input_by_id(classself,"web_user_password",password)
    input_by_id(classself,"web_user_password_confirmation",confirmpassword)
    if captcha:
       set_captcha(classself)
    classself.driver.find_element_by_id("web_user_submit").click()
    

def login(classself,username,password):
    wait_element_present_by_id(classself,"login_input")
    input_by_id(classself,"login_input",username)
    input_by_id(classself,"pwd_input",password)
    classself.driver.find_element_by_css_selector("input.button").click()
    time.sleep(5)

def login_by_form(classself,username,password):
    wait_element_present_by_xpath(classself,"//div[@id='login-form']/form/label/input")
    input_by_xpath(classself,"//div[@id='login-form']/form/label/input",username)
    input_by_xpath(classself,"//div[@id='login-form']/form/label[2]/input",password)
    classself.driver.find_element_by_css_selector("input.button").click()
    time.sleep(5)

def login_by_window(classself,username,password):
    wait_element_present_by_xpath(classself,"//div[@id='login-form']/form/label/input")
    input_by_xpath(classself,"//div[@id='login-form']/form/label/input",username)
    input_by_xpath(classself,"//div[@id='login-form']/form/label[2]/input",password)
    classself.driver.find_element_by_css_selector("form > input.button").click()
    time.sleep(5)

def reset_password(classself,user):
    go_to_home(classself)
    go_to_signin(classself)
    click_element_by_xpath(classself,"//*[@id='lost_password']/p/a")
#    click_element_by_css(classself,"a.password_reset.more")
    time.sleep(2)
    assert_text_equal_by_css(classself,"Reset your password","#reset_password > header > h1")
    input_by_id(classself,"email_input",user)
    click_element_by_css_no_wait(classself,"#password-reset-form > form > input.button")
    
def change_password(classself,user,oldpwd,oldpwd2,newpwd,newpwdcfm):
    go_to_home(classself)
    time.sleep(4)
    go_to_signin(classself)
    login(classself,user,oldpwd)
    go_to_express_console(classself)
    scroll_bar(classself)
    try:click_element_by_link_text(classself,"Click here to change your password")
    except:click_element_by_css(classself,"a.change_password")
    time.sleep(3)
    assert_text_equal_by_css(classself,"Change your password","#change_password > header > h1")
    input_by_name(classself,"old_password",oldpwd2)
    input_by_id(classself,"password",newpwd)
    input_by_name(classself,"password_confirmation",newpwdcfm)
    click_element_by_css(classself,"#change-password-form > form > input.button")
    time.sleep(1)
    if classself.driver.current_url not in [classself.base_url+"/app/dashboard",classself.base_url+"/app/control_panel"]:
       classself.fail("fail,it goes wrong location")
    

def scroll_bar(classself):
    classself.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    classself.driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(10)

def scroll_by(classself):
    classself.driver.execute_script("window.scrollBy(-100,-100);")

def scroll_to_upper(classself):
    classself.driver.execute_script("window.scrollTo(0, 0);")

def scroll_to_middle(classself):
    classself.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")


def scroll_to_bottom(classself):
    classself.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def generate_greetings(username):
    _greetings="Greetings, " + username 
    _greetings+="!"
    return _greetings

def logout(classself):
    assert_element_present_by_link_text(classself,"Sign out")
    click_element_by_link_text(classself,"Sign out")
    assert_element_present_by_link_text(classself,"Sign in")


def wait_for_ajax(classself,timeout = 10):
    time.seep(timeout)
    #WebDriverWait(classself.driver, timeout).until(classself.driver.execute_script(return jQuery.active == 0;))

def update_config_file(section,name,value):
    configparse= ConfigParser.RawConfigParser()
    configparse.read('config.cfg')
    configparse.set(section,name,value)
    with open('config.cfg', 'wb') as configfile:
         configparse.write(configfile)













