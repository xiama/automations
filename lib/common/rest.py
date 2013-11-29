from consts import *
from misc import *
import time, os, re
import OSConf
import openshift  #rest api
import shutil

#
# All of the rest helpers as alternatives to rhc-client functionalities
#

def create_app2(app_name, app_type, user_email=None, user_passwd=None, 
               clone_repo=True, git_repo="./", scalable=False, 
               gear_size = "small", disable_autoscaling=True):
    """Similar as craate_app but with using REST API"""
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    if scalable:
        scalable = 'true'
    else:
        scalable = 'false'

    (status, response) = rest.app_create_scale(app_name, app_type, scalable)
    if status in ('Created', 'OK'):
        OSConf.setup_by_rest()
        if clone_repo:
            git_clone_app(app_name)
        return 0
    else:
        return 1


def destroy_app2(app_name, user_email=None, user_passwd=None, clean_repo=False, git_repo="./"):
    """REST variant of destro_app"""
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    rest.app_delete(app_name)

    if clean_repo == True and os.path.exists(git_repo):
        shutil.rmtree(git_repo)

    OSConf.remove_app(app_name)


def create_scalable_app2(app_name, app_type, user_email=None, user_passwd=None, 
                        clone_repo=True, git_repo="./", gear_size="small", 
                        disable_autoscaling=True):
    """Create app with REST API"""
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()

    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, response) = rest.app_create_scale(app_name, app_type)
    if status in ('OK', 'Created'):
        OSConf.setup_by_rest()
        if clone_repo:
            git_clone_app(app_name)
        if disable_autoscaling:
            if clone_repo:
                touch(os.path.join(app_name,".openshift/markers/disable_auto_scaling"))
                cmd = "cd %s && git add . && git commit -amt && git push" % (app_name)
                log.debug("Disabling autoscaling...")
                (retcode, output) = command_getstatusoutput(cmd, quiet = True)
                if retcode != 0:
                    log.error("Unable to disable autoscaling: %s"%output)
            else:
                log.warning("Unable to disable autoscaling->disabled clone_repo")
    else:
        log.error(response)
    if status in ('OK', 'Created'):
        return 0
    else:
        return 1


def scale_up(app_name, domain_name=None, user_email=None, user_passwd=None):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, resp) = rest.app_scale_up(app_name)
    import json
    jresp = json.loads(resp)
    if status == 'OK':
        return 0
    elif jresp['status'] == "unprocessable_entity":
        return 2
    else:
        log.error(resp)
        return 1
    '''
    if domain_name is None:
        domain_name = get_domain_name()
    cmd = 'curl -d nolinks=1 -s -3 -k -H "Accept: application/json" --user "%s:%s" https://%s/broker/rest/domains/%s/applications/%s/events -X POST -d event=scale-up'%(user_email, user_passwd, get_instance_ip(), domain_name, app_name),
    (status, output) = command_getstatusoutput(cmd, quiet=True)
    try:
        jjson = json.loads(output)
    except:
        print "ERROR!", output
        return 1
    if status == 0 and jjson['status'] in ('ok'):#$"Application event 'scale-up' successful" in output:
        print "Application has successfull scaled up"
        return 0
    else:
        print output
        print "Failed to scale up the app"
        return 1
    '''


def scale_down(app_name, domain_name=None, user_email=None, user_passwd=None):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, resp) = rest.app_scale_down(app_name)
    import json
    jresp = json.loads(resp)
    if status == 'OK':
        return 0
    elif jresp['status'] == "unprocessable_entity":
        return 2
    else:
        log.error(resp)
        return 1
    '''
    if domain_name is None:
        domain_name = get_domain_name()
    cmd = 'curl -d nolinks=1 -s -3 -k -H "Accept: application/json" --user "%s:%s"  https://%s/broker/rest/domains/%s/applications/%s/events -X POST -d event=scale-down'%(user_email, user_passwd, get_instance_ip(), domain_name, app_name),
    (status, output) = command_getstatusoutput(cmd, quiet=True)
    try:
        jjson = json.loads(output)
    except:
        print "ERROR!",output
        return 1

    if status == 0 and jjson['status'] in ('ok'):#and "Application event 'scale-down' successful" in output:
        print "Application has successfull scaled down"
        return 0
    else:
        print output
        print "Failed to scale down the app"
        return 1
    '''


def get_application_template_uuid(name):
    """
    Return application template's UUID
    """
    (user, passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), user=user, passwd=passwd)
    (status, resp) = rest.app_templates()
    if status == 'OK':
        for t in rest.rest.response.json['data']:
            if t["display_name"] == name:
                return t["uuid"]
    else:
        log.error("%s,%s"%(status, raw))
        return None
    log.error("Unable to find given template")
    return None


def create_app_using_template(app_name, template_tag):
    template_uuid = get_application_template_uuid(template_tag)
    log.debug(template_uuid)
    (user, passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), user=user, passwd=passwd)
    (status, resp) = rest.app_create(app_name, 'template', template_uuid=template_uuid )
    if status == 'OK':
        return 0
    else:
        return 1

