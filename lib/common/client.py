from consts import *
from misc import *
import time, os, re
import OSConf
import openshift  #rest api
import shutil

#
# All of the rhc-client helpers
#

def create_app(app_name, app_type, user_email=None, user_passwd=None,
               clone_repo=True, git_repo="./", scalable=False,
               gear_size = "small", timeout=None,
               disable_autoscaling=True):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    if clone_repo == True:
        if git_repo == "./":
            options = ""
            cmd = "ls %s" % (app_name)
        else:
            options = "-r %s" %(git_repo)
            cmd = "ls %s" % (git_repo)
    else:
        options = "--no-git"
        cmd = "true"
    try:
        if os.path.exists(app_name):
            shutil.rmtree(app_name)
    except:
        pass

    cmd = ("rhc app create %s %s -l %s -p %s"
           " %s %s")% (app_name, app_type,
                                  user_email, user_passwd, 
                                  options, RHTEST_RHC_CLIENT_OPTIONS)
    if scalable:
        cmd += " -s "

    if gear_size != "small":
        cmd += " -g %s " % ( gear_size )

    (ret, output) = command_getstatusoutput(cmd, quiet=False)

    if ret == 0:
        if not isDNS(output):
            OSConf.add_app(app_name, app_type, output)
        else:
            log.info("DNS issue - try to update cache via REST API")
            OSConf.add_app(app_name, app_type, output)
    else:
        print "ERROR!\n",output
        if is500(output): #or isDNS(output):
            raise MercyException("500")
        return ret

    if scalable and disable_autoscaling:
        if clone_repo:
            touch(os.path.join(app_name,".openshift/markers/disable_auto_scaling"))
            cmd = "cd %s && git add . && git commit -amt && git push" % (app_name)
            log.debug("Disabling autoscaling...")
            (retcode, output) = command_getstatusoutput(cmd, quiet = True)
            if retcode != 0:
                log.error("Unable to disable autoscaling: %s"%output)
        else:
            log.warning("Unable to disable autoscaling->disabled clone_repo")
    if app_type == app_types['jenkins']:
        print 'Waiting for jenkins server to get ready...'
        time.sleep(30)
    return ret


def create_scalable_app(app_name, app_type, user_email=None, user_passwd=None, 
                        clone_repo=True, git_repo="./", gear_size="small", 
                        disable_autoscaling=True):

    return create_app(app_name, app_type, user_email=user_email,
                      user_passwd=user_passwd, clone_repo=clone_repo,
                      git_repo=git_repo, scalable=True, gear_size=gear_size,
                      disable_autoscaling=disable_autoscaling)


def stop_app(app_name, user_email, user_passwd):
    cmd = "rhc app stop %s -l %s -p %s %s"% (app_name, 
                                             user_email, 
                                             user_passwd, 
                                             RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output)  = command_getstatusoutput(cmd)
    return ret


def start_app(app_name, user_email, user_passwd):
    cmd = "rhc app start %s -l %s -p %s %s"% (app_name, 
                                              user_email, 
                                              user_passwd, 
                                              RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output) = command_getstatusoutput(cmd)
    return ret


def force_stop_app(app_name, user_email, user_passwd):
    cmd = "rhc app force-stop %s -l %s -p %s %s"% (app_name, 
                                                   user_email, 
                                                   user_passwd, 
                                                   RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output)  = command_getstatusoutput(cmd)
    return ret


def restart_app(app_name, user_email, user_passwd):
    cmd = "rhc app restart %s -l %s -p %s %s"% (app_name, 
                                                          user_email, 
                                                          user_passwd, 
                                                          RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output) = command_getstatusoutput(cmd)
    return ret


def reload_app(app_name, user_email, user_passwd):
    cmd = "rhc app reload %s -l %s -p %s %s"% (app_name, 
                                               user_email, 
                                               user_passwd, 
                                               RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output) = command_getstatusoutput(cmd)
    return ret


def embed(app_name, embed_cart, user_email=None, user_passwd=None):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    obj = re.search(r"(^[^-]+)-(.*)", embed_cart)
    action = obj.group(1)
    embed_cart = obj.group(2)
    cmd = "rhc cartridge %s %s -a %s -l %s -p '%s' %s" % (action, 
                                                          embed_cart, 
                                                          app_name, 
                                                          user_email, 
                                                          user_passwd, 
                                                          RHTEST_RHC_CLIENT_OPTIONS)
    if action == "remove":
        cmd += " --confirm"
    (ret, output) = command_getstatusoutput(cmd)

    if ret == 0:
        try:
            ret2 = OSConf.update_embed(app_name, action, embed_cart, output)
            if ret2 != 0:
                log.error("Unable to cache embedded info.")
        except Exception, e:
            log.error("Unable to cache embedded info: %s"% e)
    else:
        log.error(output)
        #if is500(output): # or isDNS(output):
            #raise MercyException("500")
    return ret


#@repeat_if_failure
def destroy_app(app_name, user_email=None, user_passwd=None, clean_repo=False, git_repo="./"):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    if git_repo == "./":
        git_repo = app_name

    cmd = "rhc app delete %s -l %s -p '%s' --confirm %s"% (app_name, 
                                                           user_email, 
                                                           user_passwd, 
                                                           RHTEST_RHC_CLIENT_OPTIONS)

    (ret, output) = command_getstatusoutput(cmd, quiet=True)
    if clean_repo == True and os.path.exists(git_repo):
        shutil.rmtree(git_repo)

    if ret == 0:
        OSConf.remove_app(app_name)
    else:
        print output
        if is500(output) or isDNS(output):
            pass
            #raise MercyException("500 or DNS")
    return ret


def add_sshkey(key_filepath="~/.ssh/id_rsa.pub", key_name="default", user_email=None, user_passwd=None, options=""):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    cmd = 'rhc sshkey add %s %s -l %s -p %s %s %s'% (key_name,
                                                     key_filepath,
                                                     user_email,
                                                     user_passwd,
                                                     options,
                                                     RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output) = command_getstatusoutput(cmd)
    if ret == 0:
        cmd = "ssh-keygen -lf %s" % (key_filepath)
        (ret, output) = command_getstatusoutput(cmd, quiet=True)
        try:
            pattern = re.compile(r'\d+ ([\w:]+) .*\(([DR]SA)\)')
            match_obj = pattern.search(output)
            fingerprint = match_obj.group(1)
            key_type = match_obj.group(2).lower()
            ret2 = OSConf.add_sshkey(key_name, key_type, fingerprint)
            if ret2 != 0:
                print "Warning: Failed to add ssh key to OSConf"
        except:
            print "Warning: Failed to add ssh key to OSConf"
    else:
        print output
    return ret


def remove_sshkey(key_name="default", user_email=None, 
                  user_passwd=None, options=""):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    cmd = ("rhc sshkey remove %s -l %s -p '%s' "
           " %s %s")% (key_name, user_email, user_passwd, 
                       options, RHTEST_RHC_CLIENT_OPTIONS)
    (ret, output) = command_getstatusoutput(cmd)
    if ret == 0:
        ret2 = OSConf.remove_sshkey(key_name)
        if ret2 != 0:
            print "Warning: Failed to remove ssh key from OSConf"
    else:
        print output
    return ret

def update_sshkey(key_filepath="~/.ssh/id_rsa.pub", key_name="default", user_email=None, user_passwd=None, options=""):
    '''Since there's no 'rhc sshkey update' now, this function is only used to make sure ssh key is correctly set'''
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    ret = remove_sshkey(key_name, user_email, user_passwd)
    if ret != 0:
        print "Failed to remove key %s: %s" % (key_name, key_filepath)
    ret = add_sshkey(key_filepath, key_name, user_email, user_passwd)
    if ret == 0:
        cmd = "ssh-keygen -lf %s" % (key_filepath)
        (ret, output) = command_getstatusoutput(cmd, quiet=True)
        try:
            pattern = re.compile(r'\d+ ([\w:]+) .*\(([DR]SA)\)')
            match_obj = pattern.search(output)
            fingerprint = match_obj.group(1)
            key_type = match_obj.group(2).lower()
            OSConf.update_sshkey(key_name, key_type, fingerprint)
        except:
            print "Warning: Failed to update the ssh key stored in OSConf"
    else:
        print "Failed to add ssh key %s: %s" % (key_name, key_filepath)
    return ret

def create_domain(domain_name, user_email=None, user_passwd=None, options=""):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    print domain_name
    cmd = 'rhc domain create %s -l %s -p "%s" %s %s'% (domain_name,
                                                       user_email, 
                                                       user_passwd, 
                                                       options,
                                                       RHTEST_RHC_CLIENT_OPTIONS)
    ret = command_get_status(cmd)
    if ret == 0:
        OSConf.initial_conf()
    return ret


def alter_domain(domain_name, user_email=None, user_passwd=None, options=""):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    old_domain = get_domain_name(user_email, user_passwd)
    cmd = 'rhc domain update %s %s -l %s -p "%s" %s %s'% (old_domain,
                                                          domain_name,
                                                          user_email, 
                                                          user_passwd, 
                                                          options,
                                                          RHTEST_RHC_CLIENT_OPTIONS)
    ret = command_get_status(cmd)
    if ret == 0:
        OSConf.alter_domain(domain_name)
    return ret


def fix_domain(domain_name, user_email=None, user_passwd=None):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()

    cmd = 'rhc domain show -l %s -p "%s"'% (user_email, user_passwd)
    (ret, output) = cmd_get_status_output(cmd)
    if ret != 0:
        print "Failed to get domain info"
        return 1
    if output.find("No namespaces found") != -1:
        print "Namespace is destroyed. Try to create it again."
        return create_domain(domain_name, user_email, user_passwd)
    elif output.find("Namespace: %s" % (domain_name)) != -1:
        return 0
    else:
        print "Alter namespace back"
        return alter_domain(domain_name, user_email, user_passwd)

