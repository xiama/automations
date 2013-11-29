#!/usr/bin/python

##Gloabal varible configuration
#set gloable varible values
import string
import ConfigParser

class Config():
    def __init__(self):
        configparse = ConfigParser.RawConfigParser()
        configparse.read('config.cfg')
        self.timeoutsec=configparse.get('environment', 'timeoutsec')
        self.password=configparse.get('environment', 'password')
        self.browser=configparse.get('environment', 'browser')
        self.browserpath=configparse.get('environment', 'browserpath')
        self.proxy=configparse.get('environment', 'proxy')
        self.url=configparse.get('environment', 'url')
        self.resultfile=configparse.get('output', 'resultfile')
        self.description=configparse.get('output', 'description')
        self.title=configparse.get('output', 'title')
        self.confirm_url_express=configparse.get('environment', 'confirm_url_express')
        self.confirm_url_express_yujzhang=configparse.get('environment', 'confirm_url_express_yujzhang')
        self.confirm_url_express_yujzhang_invalidkey=configparse.get('environment', 'confirm_url_express_yujzhang_invalidkey')
        self.confirm_url_flex=configparse.get('environment', 'confirm_url_flex')
        self.restricted_user=configparse.get('environment', 'restricted_user')
        self.invalid_user=configparse.get('environment', 'invalid_user')
        self.toregister_user=configparse.get('environment', 'toregister_user')
        self.new_user=configparse.get('environment', 'new_user')
        self.granted_user = ["xtian+1@redhat.com","123456"]
        self.granted_user2 = ["yujzhang+confirmlink@redhat.com","111111"]
        self.rhn_user = ["libra-qe@redhat.com","redhat"]
        self.exist_domain=configparse.get('environment', 'exist_domain')
        self.ssh_key_file=configparse.get('environment', 'ssh_key_file')
        self.tochangepwduser = ["yujzhang+pwd@redhat.com","111111","111111"]
        self.domainuser = ["yujzhang+domain@redhat.com","111111"]
        self.libra_server=configparse.get('environment', 'libra_server')
        self.dashboard_path=self.url+"/app/dashboard"
        self.control_panel=self.url+"/app/control_panel"
        self.registration_page=self.url+"/app/user/new"
        self.express_registration_page=self.url+"/app/user/new/express"
        self.flex_registration_page=self.url+"/app/user/new/flex"
        self.flex_console=self.url+"/flex/flex/index.html"

if __name__ == "__main__":
    self = Config()


def baseconfirm_url(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return confirmation_link[:pathstart]

def email(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return str.replace(str.replace(temp_email,"%2B","+"),"%40","@")

def invalidemail_confirm_url(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return url+ str.replace(path,temp_email,"ere")

def invalidkey_confirm_url(confirmation_link):
#    process_email_confirm_link(confirmation_link)
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return url+str.replace(path,key,"rere")

def noemail_confirm_url(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return url+path[:j-1]

def nokey_confirm_url(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return url+path[:m+1]+path[j+1:]

def validemail_confirm_url(confirmation_link):
    pathstart=str.index(confirmation_link,"app")
    path=confirmation_link[pathstart-1:]
    i=str.index(path,"=")
    j=str.index(path,"&") 
    k=str.rindex(path,"=")
    m=str.index(path,"?")
    key=path[i+1:j]
    temp_email=path[k+1:]
    return url+path


