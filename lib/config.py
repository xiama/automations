#!/usr/bin/python

##Gloabal varible configuration
#set gloable varible values
import string
import ConfigParser

configparse = ConfigParser.RawConfigParser()
configparse.read('/home/pruan/work/rhtest/etc/config.cfg')
timeoutsec=configparse.get('environment', 'timeoutsec')
password=configparse.get('environment', 'password')
browser=configparse.get('environment', 'browser')
browserpath=configparse.get('environment', 'browserpath')
proxy=configparse.getboolean('environment', 'proxy')
url=configparse.get('environment', 'url')
resultfile=configparse.get('output', 'resultfile')
description=configparse.get('output', 'description')
title=configparse.get('output', 'title')
confirm_url_express=configparse.get('environment', 'confirm_url_express')
confirm_url_express_yujzhang=configparse.get('environment', 'confirm_url_express_yujzhang')
confirm_url_express_yujzhang_invalidkey=configparse.get('environment', 'confirm_url_express_yujzhang_invalidkey')
confirm_url_flex=configparse.get('environment', 'confirm_url_flex')
restricted_user=configparse.get('environment', 'restricted_user')
invalid_user=configparse.get('environment', 'invalid_user')
toregister_user=configparse.get('environment', 'toregister_user')
new_user=configparse.get('environment', 'new_user')
granted_user = ["xtian+1@redhat.com","123456"]
granted_user2 = ["yujzhang+confirmlink@redhat.com","111111"]
rhn_user = ["libra-qe@redhat.com","redhat"]
exist_domain=configparse.get('environment', 'exist_domain')
ssh_key_file=configparse.get('environment', 'ssh_key_file')
tochangepwduser = ["yujzhang+pwd@redhat.com","111111","111111"]
domainuser = ["yujzhang+domain@redhat.com","111111"]
libra_server=configparse.get('environment', 'libra_server')
dashboard_path=url+"/app/dashboard"
control_panel=url+"/app/control_panel"
registration_page=url+"/app/user/new"
express_registration_page=url+"/app/user/new/express"
flex_registration_page=url+"/app/user/new/flex"
flex_console=url+"/flex/flex/index.html"




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


