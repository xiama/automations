# OpenShift Conf File Operator
# lilu@redhat.com
# 2011-11-04
#
import os, commands, re
import cPickle as pickle
import openshift
from helper import *
import json

"""
Note:
  Access to cached object must be performed only via functions, not directly 
  through user object like:
    passwd = OSConf.default['sshkeky']['default]
  but
    passwd = OSConf.get_ssh_key('default')

  If such function doesn't exist, please create it. It will be more easier for
  maintanance.
"""


class OSConf:
    """Class for handling cache of openshift user with all of his settings."""

    def __init__(self, OSConf_dump = None):
        """Tries to load cache file. If whatever error occurs it will create
        a new one"""
        if OSConf_dump is None:
            self.conf_file = get_cache_file()
        else:
            self.conf_file = OSConf_dump
        try:
            self.load_conf()
        except Exception as e:
            log.warn("Unable to load cache: %s"% e)
            initial_conf(self)
            log.warn("New cache has been initialized")

    def load_conf(self):
        f = file(self.conf_file, 'rb')
        self.conf = pickle.load(f)
        f.close()

    def dump_conf(self):
        oldumask = os.umask(0000)
        f = file(self.conf_file, 'wb')
        pickle.dump(self.conf, f, True)
        f.close()
        os.umask(oldumask)

global default
default = None

def _get_default():
    """ Returns the content of pickle file if exists. Otherwise it will create
        a new instance of OSConf class with initialization."""
    global default
    if default is None:
        default = OSConf()
    return default

def initial_conf(user=None):
    """ This function is called, when the cache file doesn't exist.
    * It will try to set up the content.
    * Creates a new cache file.
    @return [Hash] newly initiated object with all of the information
    """
    if user is None:
        user = _get_default()
    if ('OPENSHIFT_user_email' not in os.environ) or ('OPENSHIFT_user_passwd' not in os.environ):
        log.error("Environment Variables OPENSHIFT_* Not Found.")
        log.error("Please check these ENV var: OPENSHIFT_user_email OPENSHIFT_user_passwd")
        return -1
    os.environ["HOME"] = os.path.expanduser("~")
    if os.path.exists(user.conf_file):
        os.remove(user.conf_file)
    apps = {}
    user.conf = {}
    try:
        user.conf = setup_by_rest()
        rhlogin = {
            'email'   : os.environ['OPENSHIFT_user_email'], 
            'password': os.environ['OPENSHIFT_user_passwd']}
        user.conf['rhlogin'] = rhlogin

    except Exception as e: #we will propagate exception to upper level
        raise e
    finally:
        user.conf['apps'] = apps # we need this for future accessing the empty cache
        user.dump_conf()

    return 0


def _initial_sshkey():
    """ Returns {} if success otherwise returns None """
    conf = {}
    (user_email, user_passwd) = get_default_rhlogin()

    #let's try it with REST API
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, data) = rest.keys_list()
    if status not in ('OK','ok'):
        raise Exception("Unable to initialize CACHE[sshkey] via REST: %s"%(status))

    for key in json.loads(data)['data']:
        key_name = str(key['name'])
        conf[key_name] = {}
        conf[key_name]['type'] = str(key['type'])
        conf[key_name]['fingerprint'] = sshPKeyToFingerprint(str(key['content']))
    return conf


def get_rhlogin(user=None):
    """Returns (login, password) from the cache"""
    if user is None:
        user = _get_default()
    return user.conf['rhlogin']['email'],user.conf['rhlogin']['password']


def get_sshkeys(user=None):
    """Returns all ssh keys, which are stored in the cache"""
    if user is None:
        user = _get_default()
    try:
        return user.conf['sshkey'].keys()
    except Exception as e:
        log.error('Failed to get all sshkeys:  %s' % (e))
        raise

def get_sshkey(key_name = 'default', user=None):
    if user is None:
        user = _get_default()
    try:
        return (user.conf['sshkey'][key_name]['type'], 
                user.conf['sshkey'][key_name]['fingerprint'])
    except:
        log.error('Failed to get sshkey %s' % (key_name))
        raise

def get_app_names(user=None):
    if user is None:
        user = _get_default()
    return user.conf['apps'].keys()

def get_apps(user=None):
    if user is None:
        user = _get_default()
    return user.conf['apps']

def get_app_url(app_name, user = None):
    if user is None:
        user = _get_default()
    if app_name not in user.conf['apps']:
        return 1
    return user.conf['apps'][app_name]['url']

def get_app_url_X(app_name, user = None):
    if user is None:
        user = _get_default()
    def closure():
        return get_app_url(app_name, user)
    return closure

def get_git_url(app_name, user = None):
    if user is None:
        user = _get_default()
    if app_name not in user.conf['apps']:
        return 1
    return user.conf['apps'][app_name]['git_url']

def get_ssh_url(app_name, user = None):
    if user is None:
        user = _get_default()
    if app_name not in user.conf['apps']:
        return 1
    return user.conf['apps'][app_name]['git_url'].split('/')[2]
    

def get_app_uuid(app_name, user = None):
    if user is None:
        user = _get_default()
    if app_name not in user.conf['apps']:
        return 1
    #return user.conf['apps'][app_name]['uuid']
    # Fix for REST API 1.6
    return user.conf['apps'][app_name]['id']

def get_app_uuid_X(app_name, user=None):
    if user is None:
        user = _get_default()
    def closure():
        return get_app_uuid(app_name, user)
    return closure

def setup_by_rest(user=None):
    """
    Returns Dict object with all of the fresh data, given from REST
      - domain
      - apps
        - embedded cartridges
      - ssh keys
    """
    conf = {} #we start with empty object
    conf['apps'] = {}

    (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, data) = rest.app_list()
    if status not in ('OK','ok'):
        raise Exception("Unable to initialize CACHE via REST: %s"%(status))

    for d in data:
        app_name = d['name']
        conf['apps'][app_name] = {}
        framework = d['framework']
        conf['apps'][app_name]['type'] = framework
        conf['apps'][app_name]['embed'] = {}
        conf['apps'][app_name]['git_url'] = d['git_url']
        #conf['apps'][app_name]['ssh_url'] = d['ssh_url']
        # Hot fix for Bug https://bugzilla.redhat.com/show_bug.cgi?id=950477
        obj = re.match(r'ssh://([^\s]+)', d['ssh_url'])
        if obj:
            conf['apps'][app_name]['ssh_url'] = str(obj.group(1))
        else:
            conf['apps'][app_name]['ssh_url'] = d['ssh_url']
        #conf['apps'][app_name]['uuid'] = d['uuid']
        conf['apps'][app_name]['id'] = d['id']
        conf['apps'][app_name]['scalable'] = d['scalable']
        conf['apps'][app_name]['url'] = d['app_url']
        conf['apps'][app_name]['gear_profile'] = d['gear_profile']
        conf['apps'][app_name]['aliases'] = d['aliases']
        # Hot fix fot Bug 956044
        #conf['apps'][app_name]['build_job_url'] = str(d['build_job_url'])

        if 'jenkins' in framework:
            (gears, glen) = rest.get_gears(app_name)
            conf['apps'][app_name]['username'] = gears[0]['cartridges'][0]['username']
            conf['apps'][app_name]['password'] = gears[0]['cartridges'][0]['password']
            #HACK due to bug#892878
            if conf['apps'][app_name]['username'] != 'admin':
                f = open('jenkins.password','r')
                credentials = f.read()
                (username, password) = credentials.split(' ')
                conf['apps'][app_name]['username'] = username
                conf['apps'][app_name]['password'] = password


        (status, data2) = rest.cartridge_list(app_name)
        for cartridge in json.loads(data2)['data']:
            cart_name = cartridge['name']
            emb_cart = {}
            for prop in cartridge['properties']:
                if prop['type'] != 'cart_data':
                    continue
                if prop['name'] == 'connection_url':
                    obj = re.search(r"([\d\.]+):(\d+)", prop['value'])
                    if obj:
                        emb_cart['url'] =  obj.group(1)
                        emb_cart['port'] = obj.group(2)
                    else:
                        emb_cart['url'] =  str(prop['value'])
                elif prop['name'] == 'job_url':
                    emb_cart['url'] = str(prop['value'])
                    emb_cart['job_url'] = str(prop['value'])
                elif prop['name'] == 'database_name':
                    emb_cart['database'] = str(prop['value'])
                else:
                # Temporary fix for bug: 903139
                    try:
                        emb_cart[str(prop['name'])] = str(prop['value'])
                    except KeyError:
                        print 'Warning: There is no value field for %s of cartridge %s' % (prop['name'], cartridge['name'])
                        continue
            if cartridge['name'] == 'rockmongo-1.1':
                emb_cart['username'] = get_embed_info(app_name, 'mongodb-2.2', 'username')
                emb_cart['password'] = get_embed_info(app_name, 'mongodb-2.2', 'password')
            elif cartridge['name'] == 'phpmyadmin-4':
                emb_cart['username'] = get_embed_info(app_name, 'mysql-5.1', 'username')
                emb_cart['password'] = get_embed_info(app_name, 'mysql-5.1', 'password')

            conf['apps'][app_name]['embed'][cart_name] = emb_cart

    conf['sshkey'] = _initial_sshkey()
    conf['domain'] = get_domain_name_()
    return conf


def add_app(app_name, framework, output, user=None):
    '''
    This function no more parses output, but takes info from REST.
    '''
    if user is None:
        user = _get_default()
    user.conf['apps'][app_name] = {}
    user.conf['apps'][app_name]['type'] = framework
    user.conf['apps'][app_name]['embed'] = {}
    (user_email, user_passwd) = get_default_rhlogin()
    rest = openshift.Openshift(host=get_instance_ip(), 
                               user=user_email, 
                               passwd=user_passwd)
    (status, data) = rest.app_get_descriptor(app_name)
    d = json.loads(data)['data']
    user.conf['apps'][app_name]['url'] = str(d['app_url']).split('/')[2]
    #user.conf['apps'][app_name]['uuid'] = str(d['uuid'])
    user.conf['apps'][app_name]['id'] = str(d['id'])
    user.conf['apps'][app_name]['git_url'] = str(d['git_url'])
    # Hot fix fot Bug 956044
    #user.conf['apps'][app_name]['build_job_url'] = str(d['build_job_url'])
    if 'jenkins' in framework:
        (gears, glen) = rest.get_gears(app_name)
        user.conf['apps'][app_name]['username'] = gears[0]['cartridges'][0]['username']
        user.conf['apps'][app_name]['password'] = gears[0]['cartridges'][0]['password']

        #HACK due to bug#892878
        if user.conf['apps'][app_name]['username'] != 'admin':
            username = re.findall(r"User:\s+(\w+)", output)[-1]
            password = re.findall(r"Password:\s+(\S+)", output)[-1]
            user.conf['apps'][app_name]['username'] = username
            user.conf['apps'][app_name]['password'] = password
            write_file('jenkins.password',"%s %s"%(username, password))

    user.dump_conf()
    return 0

def remove_app(app_name, user=None):
    if user is None:
        user = _get_default()
    try:
        user.conf['apps'].pop(app_name)
        user.dump_conf()
        return 0
    except:
        log.warning("the app doesn't exist in OSConf db.")
        return 1

def alter_domain(domain_name, user=None):
    """
    We have to reinitialize whole cache!
    It doesn't make sense to update particular fields with new domain
    it's too sensitive.
    """
    if user is None:
        user = _get_default()
    user.conf = setup_by_rest()
    user.dump_conf()
    return 0

def add_sshkey(key_name, key_type, fingerprint, user=None):
    """
    Returns 0 if successfully added new key into cache.
    """
    if user is None:
        user = _get_default()
    if user.conf['sshkey'].has_key(key_name):
        log.error('A ssh key named %s(%s) already exists.' % (key_name, user.conf['sshkey'][key_name]['fingerprint']))
        return 1
    user.conf['sshkey'][key_name] = {}
    user.conf['sshkey'][key_name]['type'] = key_type
    user.conf['sshkey'][key_name]['fingerprint'] = fingerprint
    user.dump_conf()
    return 0

def remove_sshkey(key_name, user=None):
    """Remove the ssh key from cache only.
    This method should be called only from common, not directly 
    @param [String] key_name the name of the key to get from cache
    @return (type, fingerprint) tuple
    """
    if user is None:
        user = _get_default()
    if user.conf['sshkey'].has_key(key_name):
        user.conf['sshkey'].pop(key_name)
        user.dump_conf()
        return 0
    else:
        log.error("ssh key named %s doesn't exist!" % (key_name))
        return 1

def update_sshkey(key_name, key_type, fingerprint, user=None):
    if user is None:
        user = _get_default()
    if user.conf['sshkey'].has_key(key_name):
        user.conf['sshkey'][key_name]['type'] = key_type
        user.conf['sshkey'][key_name]['fingerprint'] = fingerprint
        user.dump_conf()
        return 0
    else:
        log.error("ssh key named %s doesn't exist!" % (key_name))
        return 1
            
def update_embed(app_name, op, embed_cart, output, user=None):
    if user is None:
        user = _get_default()
    if cmp(op, 'add') == 0:
        embed_cart = embed_cart.replace('add-','')
        user.conf['apps'][app_name]['embed'][embed_cart] = {}

        (user_email, user_passwd) = get_default_rhlogin()
        rest = openshift.Openshift(host=get_instance_ip(), 
                                   user=user_email, 
                                   passwd=user_passwd)
        (status, data) = rest.cartridge_get(app_name, embed_cart)
        emb_cart = {}

        for prop in data['data']['properties']:
            if prop['type'] != 'cart_data':
                continue
            if prop['name'] == 'connection_url':
                ssh_url = get_ssh_url(app_name)
                (ret, output) = commands.getstatusoutput('''ssh -o LogLevel=quiet %s "env | grep -P 'OPENSHIFT_\w+?_DB_(HOST|PORT)'"''' % (ssh_url))
                if ret != 0:
                    print (re, output)
                    print ssh_url
                    print "Failed to get database connection url via env var"
                else:
                    for line in output.splitlines():
                        (key, value) = line.split('=')
                        if key.find('HOST') != -1:
                            emb_cart['url'] = value
                        else:
                            emb_cart['port'] = value

                if data['data']['name'] in ['phpmyadmin-4', 'rockmongo-1.1']:
                    emb_cart['url'] = str(prop['value'])
                '''
                obj = re.search(r"([\w\.\-]+):(\d+)", prop['value'])
                if obj:
                    emb_cart['url'] =  obj.group(1)
                    emb_cart['port'] = obj.group(2)
                else:
                    emb_cart['url'] =  str(prop['value'])
                '''
            elif prop['name'] == 'database_name':
                emb_cart['database'] = str(prop['value'])
            elif prop['name'] == 'job_url':
                emb_cart['url'] = str(prop['value'])
            else:
            # Temporary fix for bug: 903139
                try:
                    #emb_cart[str(prop['name'])] = str(prop['value'])
                    emb_cart[str(prop["name"])] = str(prop["value"])
                    #emb_cart[prop['name']] = str(prop['value'])
                except KeyError:
                    print 'Warning: There is no value field for %s of cartridge %s' % (prop['name'], embed_cart)
                    continue
        if embed_cart == 'rockmongo-1.1':
            emb_cart['username'] = get_embed_info(app_name, 'mongodb-2.2', 'username')
            emb_cart['password'] = get_embed_info(app_name, 'mongodb-2.2', 'password')
            # Temporary fix of rockmongo
            #emb_cart['url'] = get_app_url(app_name) + '/rockmongo/'
        elif embed_cart == 'jenkins-client-1':
            # Hot fix for Bug 956044
            # https://jenkins-dev3184tst.dev.rhcloud.com/job/prl-build
            (status1, data1) = rest.app_get(app_name)
            user.conf['apps'][app_name]['build_job_url'] = data1['build_job_url']
            emb_cart['url'] = data1['build_job_url']
            print emb_cart['url'] 
        elif embed_cart == 'phpmyadmin-4':
            emb_cart['username'] = get_embed_info(app_name, 'mysql-5.1', 'username')
            emb_cart['password'] = get_embed_info(app_name, 'mysql-5.1', 'password')
            #emb_cart['url'] = get_app_url(app_name) + '/phpmyadmin/'
        #finally, update user.conf[...]
        user.conf['apps'][app_name]['embed'][embed_cart] = emb_cart
    elif cmp(op, 'remove') == 0:
        embed_cart = embed_cart.replace('remove-','')
        user.conf['apps'][app_name]['embed'].pop(embed_cart)
    else:
        return 1
    user.dump_conf()
    return 0

def get_embed_info(app_name, embed_cart, info = None, user=None):
    if user is None:
        user = _get_default()
    if app_name not in user.conf['apps']:
        return 1
    if embed_cart not in user.conf['apps'][app_name]['embed']:
        return 1
    if info == None:
        return user.conf['apps'][app_name]['embed'][embed_cart]
    return user.conf['apps'][app_name]['embed'][embed_cart][info]

def get_embed_info_X(app_name, embed_cart, info = None, user=None):
    def closure():
        return get_embed_info(app_name, embed_cart, info, user=user)
    return closure

def get_cache_file():
    """
    Returns a default name for cache file.
    """
    (user, passwd) = get_default_rhlogin()
    return "%s/OPENSHIFT_OSConf-%s.dump" % (get_tmp_dir(), user)

# hot fix for Bug 912255, obtaining DB credentials with env vars instead of REST API
#def get_db_cred(db_type)
#   db_cred = {

#        'database' : os.environ['OPENSHIFT_APP_NAME'],
#        'url'      : os.environ['OPENSHIFT_' + db_type + '_DB_HOST'],
#        'port'     : os.environ['OPENSHIFT_' + db_type + '_DB_PORT'],
#        'username' : os.environ['OPENSHIFT_' + db_type + '_DB_USERNAME'],
#        'password' : os.environ['OPENSHIFT_' + db_type + '_DB_PASSWORD']

#    } 

#   return db_cred



# debugging
if __name__ == "__main__":
#    initial_conf()
    #print default.conf
    pass
