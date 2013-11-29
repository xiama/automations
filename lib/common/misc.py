import time, os, subprocess, sys, re
import OSConf
import pexpect
import json
import openshift  #rest api
import shutil
import random
from consts import CONNECT_TIMEOUT
from helper import *


def env_setup(cleanup=True):
    """Prepares environment for running a case by:
      * setting up proxy if necessary
      * removing SSH_AUTH_SOCK variable
      * deleting all apps if cleanup==True
    """
    # Default
    #http_proxy='file.rdu.redhat.com:3128'

    if os.environ.has_key("OPENSHIFT_http_proxy"):
        http_proxy=os.getenv("OPENSHIFT_http_proxy").strip()
        if http_proxy != '' and http_proxy != 'None':
            #os.putenv("http_proxy", http_proxy)
            os.environ["http_proxy"]=http_proxy

    if os.environ.has_key("http_proxy"):
        print "---http_proxy: %s---" %(os.getenv("http_proxy"))
    else:
        print "---no http_proxy---"

    os.environ["HOME"] = os.path.expanduser("~")
    #os.putenv("HOME", os.path.expanduser("~"))
    remove_env("SSH_AUTH_SOCK")
    #print os.environ["SSH_AUTH_SOCK"]
    try:
        if cleanup:
            return clean_up()
    except:
        pass
    return 0

def set_env(key, value):
    print "Setting %s=%s in os.environ" %(key, value)
    os.environ[key]=value
    return 0

def remove_env(key):
    if os.environ.has_key(key):
        print "Unsetting %s in os.environ" %(key)
        os.environ.pop(key)
    return 0


def get_git_repo_size(app_name):
    """
    This function returns the git repo size in KiloBytes
    """
    ( ret_code, ret_output ) = run_remote_cmd(app_name, "du -sk git/%s.git" % ( app_name ))
    obj = re.search(r"^(\d+)\s+git", ret_output)
    if ret_code == 0 and obj is not None:
        return obj.group(1)
    else:
        raise Exception(("Unable to parse the size of git repo from the output."
                        "(Maybe remote app/dir doesn't exist, "
                        "or problems with SSH connection)"))


def user_info(user_email=None, user_passwd=None, data_source_from_s3=False):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    '''
    if data_source_from_s3 == True:
        #TODO:  What was this s3  good for?
        # I WOULD LIKE TO REMOVE TO AVOID CONFUSION
        print "Getting user info from s3"
        if OSConf.initial_conf() != 0:
            return 1
    '''
    return OSConf.get_apps()


def get_app_url_from_user_info(app_name, user_email=None, user_passwd=None, data_source_from_s3=False):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    apps_dict = user_info(user_email, user_passwd, data_source_from_s3)
    if apps_dict.has_key(app_name):
        return apps_dict[app_name]['url']
    print apps_dict
    print "In user info, nothing about %s is found" %(app_name)
    return None


def grep_web_page(url, regular_expression, options={},
                  delay=7, count=7, strong=True):
    '''
    Fetch a page and grep it. 
        * if the page cannot be fetched/accessed then returns 254
        * elif matches - returns 0
        * otherwise    - returns 1

    [02/03/2012] Added extended version for matching string. 
                 `strong` argument means that all of the RE must be found.
    [24/04/2012] Added condition, when curl is not able to fetch the url - it will return 254
    '''
    pattern = ''
    patterns = []
    if isinstance(regular_expression, str) or isinstance(regular_expression, unicode):
        pattern = re.compile(regular_expression, re.M)
        log.info(("Trying to find all the strings matching regular expression"
                  " '%s' in %s")% (regular_expression, url))
    elif isinstance(regular_expression, tuple) or isinstance(regular_expression, list):
        for p in regular_expression:
            patterns.append(re.compile(p, re.M))
    else:
        raise TypeError("Wrong type of 2nd argument. Possible types: string or list/tuple")

    #fetch_cmd = "curl %s '%s'" % (options, url)
    # Retry 4 times
    retcode = 1

    #old curl support
    if isinstance(options, str):
        obj = re.search(re.compile("-u\s+['\"]?([^:]+):([^\s'\"]+)"), options)
        if obj:
            options = get_auth_headers(obj.group(1), obj.group(2))

    for i in range(count):
        time.sleep(delay)
        output = fetch_page(url, options)
        #(retcode, output) = command_getstatusoutput(fetch_cmd, quiet = True)
        if output is not None:
            retcode = 0
            if (isinstance(regular_expression,str) 
                or isinstance(regular_expression, unicode)):
                result = pattern.findall(output)
                if result != []:
                    log.debug("Found results: %s"% result)
                    return 0
            else:  # list or tuple
                summ = 0
                for p in patterns:
                    result = p.findall(output)
                    if result != []:
                        summ += 1
                if strong: #AND
                    if summ == len(patterns):
                        print "All of the patterns have been found"
                        return 0  #success
                    else:
                        continue
                else:  #OR
                    if sum(summ)>0: #at least one was found
                        print "At least one of the patterns have been found"
                        return 0
                    else:
                        continue
    if retcode == 0:
        return 1
    else:
        log.warning("Unable to access %s"% url)
        return 254

def check_web_page_output(app_name, path='', pattern='Welcome to'):
    app_url = OSConf.get_app_url(app_name)
    return grep_web_page("%s/%s" % ( app_url, path ), pattern)

def multi_subprocess(command_list=[]):
    sub_comm_dict={}
    sub_ret_dict={}
    for i in command_list:
        a = subprocess.Popen(i, stdin=open(os.devnull,'rb'), shell=True)
        sub_comm_dict[a]=i
        sub_ret_dict[a]=a.poll()

    ret_dict={}
    while len(sub_ret_dict)>0:
        print "sleep 5 seconds, will check again"
        time.sleep(5)

        for j in sub_ret_dict.keys():
            ret=j.poll()
            if ret != None:
                sub_ret_dict.pop(j)
                ret_dict[sub_comm_dict[j]] = ret
            #else:
                #print "Command {%s} is running." %sub_comm_dict[j]
    return ret_dict


def _ssh_keygen(passphrase=""):
    if not os.path.exists('~/.ssh/id_rsa'):
        command = "ssh-keygen -N '' -f ~/.ssh/id_rsa"
        ret = subprocess.call(command, shell=True)
        if ret != 0:
            return 1
        else:
            return 0
    else:
        print 'Warning: the ~/.ssh/id_rsa key already exist and will not be overwritten.'
        return 0



#@exclusive
def prepare_libra_sshkey():
    print "Preparing libra ssh key"
    if not os.path.exists(os.path.expanduser("~/.ssh/id_rsa")) or not os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
        print "~/.ssh/id_rsa or ~/.ssh/id_rsa.pub is not existing"
        if not os.path.exists(os.path.expanduser("~/.ssh/id_rsa")) or not os.path.exists(os.path.expanduser("~/.ssh/id_rsa.pub")):
            print "~/.ssh/id_rsa or ~/.ssh/id_rsa.pub is not existing"
            print "Generating new ssh key"
            ret = _ssh_keygen()
            if ret != 0:
                print "ssh ken gen failed"
                sys.exit(1)

    else:
        print "id_rsa and id_rsa.pub are existing in local host"


def command_getstatusoutput(command, quiet = False, timeout=COMMAND_TIMEOUT):
    return cmd_get_status_output(command, quiet, timeout)

        
def command_get_status(command, timeout=COMMAND_TIMEOUT, quiet=False):
    return cmd_get_status(command, timeout, quiet)


def clean_up(user_email=None, user_passwd=None):
    """Remove all applications and cleans up cache"""
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()
    try:
        app_dict = user_info(user_email, user_passwd)
        retcode = 0
        for app_name in app_dict.keys():
            ret = destroy_app2(app_name, user_email, user_passwd)
            if ret != 0:
                retcode = ret
                # Hot fix for Bug 958619
                # delete the app a second time
                # ret = destroy_app2(app_name, user_email, user_passwd)
                # if ret != 0:
                #    retcode = ret
    except:
        #this is the case, when cache file is missing
        pass

    try:
        rest = openshift.Openshift(host=get_instance_ip(), 
                                   user=user_email, 
                                   passwd=user_passwd)
        (status, l2) = rest.app_list()

        if (status == 'OK'):
            for app in l2:
                app_name = app['name']
                try:
                    (stat, resp) = rest.app_delete(app_name)
                except Exception as e:
                    log.error("Unable to destroy %s: %s"%(app_name, str(e)))
                try:
                    if os.path.exists(app_name):
                        shutil.rmtree(app_name)
                except:
                    pass
        else:
            log.warning("Unable to get the list of apps to clean up: status = %s"%status)
    except openshift.OpenShiftNullDomainException:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc(file=sys.stderr)
        log.error("Problem when destroying applications: %s"%str(e))

    try:
        OSConf.initial_conf()
    except Exception as e:
        log.warn("Error during initialising cache: %s"% e)

    return retcode


def raw_str(regex):
    special_chars = (".", "^", "$", "*", "+", "?", "\\", "|", "{", "}", "[", "]", "(", ")")
    result = []
    l = 0
    r = 0
    while r < len(regex):
        if regex[r] in special_chars:
            if l < r:
                result.append(regex[l:r])
            result.append("\\" + regex[r])
            l = r + 1
        r += 1
    if l < r:
        result.append(regex[l:r])
    return ''.join(result)


def getRandomString(length = 10):
    return get_random_string(length)


def rhcsh(app_name, commands):
    '''
    Execute commands inside rhcsh shell:
        `commands' as an argument has to be list of pexpect commands:
            [
                (<sendline|expect>, <value>, [timeout_in_seconds]),
                ('sendline', 'ls -l'),
                ('expect', '/tmp/*',10),
                ('sendline', 'cd /bin'),
                ('sendline', 'exit'),
            ]
    '''
    ssh_url = OSConf.get_app_url(app_name)
    username = OSConf.get_app_uuid(app_name)
    ssh_options = " -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "
    p = pexpect.spawn('ssh %s %s@%s rhcsh '%(ssh_options, username, ssh_url))
    p.logfile = sys.stdout
    for cmd in commands:
        eval("p.%s('%s')"%cmd)
    p.terminate(force=True)

    return 0


def run_remote_cmd_as_root2(cmd, host=None, quiet=False):
    """
    If host==None => "broker" (sufficient in single node environment)
    """
    return run_remote_cmd2(None, cmd, as_root=True, host=host, quiet=quiet)


def run_remote_cmd_as_root(cmd, host=None, quiet=False):
    """
    If host==None => "broker" (sufficient in single node environment)
    """
    return run_remote_cmd(None, cmd, as_root=True, host=host, quiet=quiet)


def run_remote_cmd(app_name, cmd, as_root=False, host=None, quiet=False):
    """Using paramiko client"""
    if as_root:
        user = 'root'
        if not host:
            #host = get_instance_ip()
            ssh_url = OSConf.get_ssh_url(app_name)
            host = os.popen('ssh %s hostname'%ssh_url).read().strip('\n')
        key_filename = get_root_ssh_key()
    else:
        user = OSConf.get_app_uuid(app_name)
        if not host:
            host = OSConf.get_app_url(app_name)
        key_filename = get_default_ssh_key()
    return rcmd_get_status_output(cmd, user, host, key_filename, quiet)


def run_remote_cmd2(app_name, cmd, as_root=False, host=None, quiet=False):
    """
    Using ssh client
    """
    if as_root:
        user = 'root'
        if not host:
            host = get_instance_ip()
        #key_filename = get_root_ssh_key()
        key_filename = get_default_ssh_key()
    else:
        user = OSConf.get_app_uuid(app_name)
        if not host:
            host = OSConf.get_app_url(app_name)
        key_filename = get_default_ssh_key()
    return rcmd_get_status_output2(cmd, user, host, key_filename, quiet)


def check_json_web_page(url, touples, options='-H "Pragma:no-cache"', delay=5, count=1):
    '''fetch a page and check JSON'''
    log.debug("Trying to find all the touples  in %s" % (url))
    fetch_cmd = "curl -k -s %s '%s'" % (options, url)
    # Retry 4 times
    retcode = 1
    for i in range(count):
        time.sleep(delay)
        (retcode, output) = command_getstatusoutput(fetch_cmd, quiet = True)
        if retcode == 0:
            json_array = json.loads(output) #get the dict
            for key in json_array:
                for touple in touples:
                    if (key == touple[0] and json_array[key]==touple[1]):
                        print "Found results:"
                        return 0
    return 1


#@exclusive
def restore_config():
    (user, passwd) = get_default_rhlogin()
    f = open("%s/libra_server-%s"%(get_tmp_dir(), user), 'r')
    libra_ip = f.read().strip()
    libra_ip.strip()
    log.debug("Restoring libra server to default")
    cmd = "sed -i 's/libra_server=%s/libra_server=$libra_ip/g' %s" % (libra_ip.strip(), express_conf_file)
    os.system(cmd)


class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
    pass


def check_ip_type(ip, expected_type, str=''):
    try:
    	if expected_type == str:
	    if type(ip) is not str:
	        return type(str(ip)) is str
	if expected_type == int:
	    if type(ip) is not int:
		return type(int(ip)) is int
	if expected_type == list:
	    if type(ip) is str:
		return type(eval(ip)) is list
	    else:
		return type(ip) is list
	if expected_type == dict:
	    if type(ip) is dict:
		return type(eval(ip)) is dict
	    else:
		return type(ip) is dict
    except:
	raise InputError("% s, expected %s, got %s" % (str, expected_type, ip))


def get_work_dir():
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))
    return WORK_DIR


def get_app_tmpl_dir():
    return ""


def sleep(delay):
    time.sleep(delay)


def fetch_page_curl(url, options='-H "Pragma:no-cache" -L'):
    """Returns (status, output) from curl"""
    fetch_cmd = "curl -k -s %s '%s'" % (options, url)
    return cmd_get_status_output(fetch_cmd)


def fetch_page(url, headers={}):
    """Returns body of web page, otherwise None if error occured"""

    if not url.startswith('http'):
        url = 'http://'+url
    log.debug("Fetching %s"%url)
    import httplib2
    proxy = None
    if os.getenv('http_proxy'):
        obj = re.search(r"http://([^:]+):(\d+)", os.getenv('http_proxy'))
        if obj:
            proxy_host = obj.group(1)
            proxy_port = int(obj.group(2))

            if url.startswith('https'):
                proxy_type=httplib2.socks.PROXY_TYPE_HTTP
            else:
                proxy_type=httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL

            proxy = httplib2.ProxyInfo(proxy_type=proxy_type, 
                                       proxy_host=proxy_host, 
                                       proxy_port=proxy_port)
        else:
            log.warning("Wrong format of http_proxy!")

    conn = httplib2.Http(cache=None, timeout=CONNECT_TIMEOUT, proxy_info=proxy,
                         disable_ssl_certificate_validation=True)
    _headers = {'Content-type': 'text/html;charset=utf-7)',
               'User-Agent': 'Python-httplib2/7 (gzip)',
               'Accept': '*/*',
               'Pragma': 'no-cache' }
    if isinstance(headers, dict):
        if len(headers)>0:
            _headers.update(headers)
    elif isinstance(headers, str):
        obj = re.search(re.compile("-u\s+['\"]?([^:]+):([^\s'\"]+)"), headers)
        if obj:
            _headers.update(get_auth_headers(obj.group(1), obj.group(2)))
        
    (response, content) = conn.request(uri=url, method='GET', headers=_headers)

    if response.status >= 400:
        log.warning("fetch_page(%s): %s"%(url, response.reason))
    return content


def get_default_ssh_key():
    return get_default_ssh_key_()


def get_root_ssh_key():
    return get_root_ssh_key_()


def setup_c9_environment(node=None, user_email=None):
    if user_email is None:
        (user_email, user_passwd) = get_default_rhlogin()

    try:
        change_node_profile("c9", node=node)
        add_gearsize_capability("c9", user_email)
        set_user_capability("allowsubaccounts","true", user_email)
    except Exception as e:
        log.error("%s"%str(e))
        return 1

    return 0


def has_node_profile(profile):
    """
    Returns True/False whether environment has at least one node with such profile
    """
    if not is_multinode_env():
        return (profile == get_node_profile())
    else:
        for d in get_districts():
            for si in d['server_identities']:
                if si['node_profile'] == profile:
                    return True
        return False


def is_multinode_env():
    log.info("MULTI NODE is not yet fully tested/supported")
    return False
    if len(get_nodes())>1:
        return True
    return False


def get_facter(fact=None, node=None):
    (status, output) = run_remote_cmd_as_root("facter %s"%fact, node, quiet=True)
    if status == 0:
        return output.strip()
    else:
        log.error(output)
        return status


def get_node_profile(server_identity=None, node=None):
    """
    Returns True/False whether environment has at least one node with such profile
    * if server_identity==None => broker
    * node => public IP address (facter method will be used)
    * server_identity => private IP address (will be used district table from mongo)
    """
    if not is_multinode_env():
        return get_facter("node_profile")

    if node is not None:
        return get_facter("node_profile", node)

    for d in get_districts():
        for si in d['server_identities']:
            if si['name'] == server_identities:
                return si['node_profile']
    return None


def change_node_profile(gear_size = "small", safe_mode=True, node=None):
    """
    * if node==None => use the Broker
    * safe_mode => revert back if any problems...
    * if the given node is of such profile, there will be none change 
    * if such profile is already in that cluster, there will none change as well
    * if node!=None
    """
    if is_multinode_env():
        if node is None and has_node_profile(gear_size):
            log.debug("Don't need to change profile => env already contains such profile")
            return 0
    else:
        if get_node_profile(node) == gear_size:
            log.debug("No profile change -> node[%s] has such profile[%s] already."%(node, gear_size))
            return 0

    config_file = "/etc/openshift/resource_limits.conf"
    config_steps = [
        "rm -fv %s" % ( config_file ),
        "ln -v -s %s.%s %s" % ( config_file, gear_size, config_file ),
        "/usr/libexec/mcollective/update_yaml.rb /etc/mcollective/facts.yaml"]

    ret = run_remote_cmd_as_root(" && ".join(config_steps), host=node)[0]
    if safe_mode and ret != 0:
        log.error("ERROR detected => Setting default profile...")
        config_steps = [
            "rm -fv %s" % ( config_file ),
            "ln -v -s %s.%s %s" % ( config_file, "small", config_file ),
            "/usr/libexec/mcollective/update_yaml.rb /etc/mcollective/facts.yaml",
            "sleep 5"]

        run_remote_cmd_as_root(" && ".join(config_steps), host=node)[0]

    return ret


def get_cgroup_threshold(uuid, controller, attribute):
    ( ret_code, ret_output ) = run_remote_cmd_as_root(
        "cat /cgroup/all/openshift/%s/%s.%s" % ( uuid, controller, attribute )
    )
    return int(ret_output.strip())


def get_lib_dir():
    return os.path.dirname(os.path.join(os.path.abspath(__file__),"../../"))


def get_etc_dir():
    return os.path.abspath(get_lib_dir() + "/../etc")


def get_domain_name(user_email=None, user_passwd=None):
    return get_domain_name_(user_email, user_passwd)


def isDNS(output):
    """ Returns True if the response contains notes regarding DNS issues.  """
    err_strings = ["WARNING: We were unable to lookup your hostname",
                   "retry # 7 - Waiting for DNS:"]
    for st in err_strings:
        obj = re.search(st, output)
        if obj:
            return True

    return False


def is500(output):
    """
    Function validates the given output and returns True, if contains 500 
    exit code (Internal Server Error) lines.
    """
    err_strings = ["Response code was 500", "Internal Server Error"]
    for st in err_strings:
        obj = re.search(st, output)
        if obj:
            return True

    return False


def setup_testbed(**kwargs):
    """
    obj is rhtest object

    setup a testbed for subsequent tests.  There are several modes that can be 
    run.
    0. plain   (no domain, no app)
    1. basic   (has a domain name, no app)
    2. common  (has a domain name, one app)

    """
    klass = kwargs['klass']
    cf = klass.config
    rest = cf.rest_api

    if len(kwargs) == 0:
        kwargs['mode'] = 1

    mode = kwargs['mode']
    
    status, res = rest.domain_get()
    if status == 'OK':
        cf.domain_name = res
        status, res = rest.app_list()
        if len(res) > 0:
            # if mode == 1, we need to remove the existing apps
            if mode == 1:
                for app in res:
                    rest.app_delete(app['name'])
        else:
            if mode == 2:
                cf['app_name'] = getRandomString()
                if not kwargs.has_key('app_type'):
                    # make php the default
                    app_type = app_types['php']
                else:
                    app_type = app_types[kwarg['app_type']]
                klass.info("Creating an app '%s' of type '%s'..." % (cf.app_name, app_type))
                status, res = rest.app_create(cf.app_name, app_type)
    else:
        cf['domain_name'] = getRandomString()
        self.info("No domain found, creating an new one '%s'..." % cf.domain_name)
        status, res = rest.domain_create(cf.domain_name)
    return cf


def trigger_jenkins_build(git_repo, try_count=3, try_interval=5, quiet=False, timeout=COMMAND_TIMEOUT):
    unexpected_str_lst = ["BUILD FAILED/CANCELLED", "Deployment Halted"]
    for i in range(try_count):
        flag = True
        print "-" * 80
        print "Trying to trigger jenkins build - %d" % (i)
        print "-" * 80
        cmd = "cd %s && echo '%d\n' >> jenkins_trigger.txt && git add . && git commit -amt && git push" % (git_repo, i)
        (ret, output) = command_getstatusoutput(cmd, quiet, timeout)
        for s in unexpected_str_lst:
            if output.find(s) != -1:
                time.sleep(try_interval)
                flag = False
                break
        if flag == True:
            return True
    return False


def trigger_env_reload(git_repo, try_count=3, try_interval=5, quiet=False, timeout=COMMAND_TIMEOUT):
    for i in range(try_count):
        flag = True
        print "-" * 80
        print "Trying to trigger env reload - %d" % (i)
        print "-" * 80
        cmd = "cd %s && echo '%d\n' >> env_trigger.txt && git add . && git commit -amt && git push" % (git_repo, i)
        (ret, output) = command_getstatusoutput(cmd, quiet, timeout)
        if ret == 0:
            return True
    return False


def create_subdomain(sub_domain, sub_account, user=None, passwd=None):
    if user is None:
        (user, passwd) = get_default_rhlogin()
    headers = "-H 'Accept: application/json' -H 'X-Impersonate-User: %s'"%sub_account
    headers += " --user %s:%s"%(user, passwd) 
    data = " -d id=%s "%sub_domain
    url = "https://%s//broker/rest/domains"%get_instance_ip()
    cmd = "curl %s -s -k -X POST -d nolinks=1 -d id=%s %s"%(headers, data, url) 
    return cmd_get_status_output(cmd, quiet=True)[0]


def get_public_key_type(key='default'):
    try:
        f = open(get_default_ssh_key_()+".pub", 'r')
        dump = f.read()
        f.close()
        obj = re.search(r'^(ssh-...)\s+([\S]+)', dump)
        if obj:
            return obj.group(1)
    except Exception as e:
        log.error("Unable to dump public key: %s"%str(e))

    return None


def dump_public_key(key='default'):
    try:
        f = open(get_default_ssh_key_()+".pub", 'r')
        dump = f.read()
        f.close()
        obj = re.search(r'^ssh-...\s+([\S]+)', dump)
        if obj:
            return obj.group(1)
    except Exception as e:
        log.error("Unable to dump public key: %s"%str(e))

    return None

def add_sshkey4sub_account(sub_account, user=None, passwd=None):
    #curl -k -X POST -H 'Accept: application/json' -H 'X-Impersonate-User: <sub_account>' --data-urlencode name=default -d type=<ssh-rsa|ssh-dss> --data-urlencode content=<public_ssh_key_value>--user <your_rhlogin>:<password> https://openshifttest.redhat.com/broker/rest/user/keys
    if user is None:
        (user, passwd) = get_default_rhlogin()
    headers = "-H 'Accept: application/json' -H 'X-Impersonate-User: %s' "%sub_account
    headers += " --user %s:%s "%(user, passwd)
    data = " -d nolinks=1 -d name=default -d type=ssh-rsa --data-urlencode content='%s'"%dump_public_key()
    url = "https://%s//broker/rest/user/keys"%get_instance_ip()
    cmd = "curl -s -k -X POST %s %s %s"%(headers, data, url) 
    return cmd_get_status_output(cmd, quiet=True)


def create_app_using_subaccount(sub_domain, sub_account, app_name, app_type, user=None, passwd=None):
    #curl -k -X POST -H 'Accept: application/json' -H 'X-Impersonate-User: <sub_account>' -d name=<app_name> -d cartridge=<cartridge_type> -d gear_profile=c9 --user <your_rhlogin>:<password> https://openshifttest.redhat.com/broker/rest/domains/<sub_domain>/applications
    if user is None:
        (user, passwd) = get_default_rhlogin()
    headers = "-H 'Accept: application/json' -H 'X-Impersonate-User: %s' "%sub_account
    headers += " --user %s:%s "%(user, passwd) 
    data = " -d nolinks=1 -d name=%s -d cartridge=%s -d gear_profile=c9 "%(app_name, app_type)
    url = "https://%s//broker/rest/domains/%s/applications"%(get_instance_ip(), sub_domain)
    cmd = "curl -s -k -X POST %s %s %s"%(headers, data, url) 
    (status, output) = cmd_get_status_output(cmd, quiet=True)
    obj = json.loads(output)
    if obj['status'] not in ('OK', 'Created', 'created'):
        status = 1
    return (status, obj)



def touch(filename):
    try:
        f = open(os.path.normpath(filename),'w')
        f.write(' ')
        f.close()
        return 0
    except:
        return 1


def git_commit_push_all(app_name):
    cmds = [
        "cd %s" % (app_name),
        "git add .",
        "git commit -a -m hurray",
        "git push"]
    return command_get_status(" && ".join(cmds))


def inject_app_index_with_env(app_name, app_type):
    """
        Create /env.[php|pl|jsp|...] page with list of environmental variables
        Runs 'git commit|push' with this change
        Returns 0 if success
    """
    if not os.path.exists(app_name):
        raise Exception("App dir doesn't exist")
    if app_type.startswith('php'):
        content = r"""<?php header("Content-Type: text/plain"); 
            foreach ($_ENV as $key => $val){ 
                echo "$key=$val\n"; 
            } ?>"""
        xfile = "php/env.php"
    elif app_type.startswith("nodejs"):
        xfile = "server.js"
        f = open(os.path.join(app_name, xfile), 'r')
        content = f.read()
        f.close()
        new = r"""
        self.routes['/env.js'] = function(req, res) {
            var result = '';
            for (var key in process.env){
                result = result + key +'='+process.env[key] + "\n";
            }
            res.send(result);
        };"""
        seek_str=r"Routes for "
        content = inject_string_by_re(seek_str, new, content, after=False)

    elif app_type.startswith("ruby") or app_type.startswith("rack"):
        xfile = "config.ru"
        f = open(os.path.join(app_name, xfile), 'r')
        content = f.read()
        f.close()
        seek_str1 = "map '/health' do"
        seek_str2 = "get '/' do"
        if content.find(seek_str1) != -1:
            seek_str = seek_str1
            new = r"""
map '/env.rb' do
  xenv = proc do |env|
    output = ""
    ENV.each do|k,v|
      output += "#{k}=#{v}\n"
    end
    [200, { "Content-Type" => "text/html" }, [output]]
  end
  run xenv
end"""
        else:
            seek_str = seek_str2
            new = r"""
get '/env.rb' do
    output = ""
    ENV.each do|k,v|
      output += "#{k}=#{v}\n"
    end
    response_body = [200, output]
end
"""

        content = inject_string_by_re(seek_str, new, content, after=False)

    elif app_type.startswith("jboss"):
        xfile = "src/main/webapp/env.jsp"
        content = """
            <%@ page contentType="text/plain" language="java" import="java.sql.*" %>
            <%@ page import="javax.naming.*" %>
            <%@ page import="java.util.*" %>
            <%@ page trimDirectiveWhitespaces="true" %>
            <%
            Map envs = System.getenv();
            Set keys = envs.keySet();
            Iterator i = keys.iterator();
            while (i.hasNext()) {
                 String k = (String) i.next();
                 String v = (String) envs.get(k);
                 out.println(k+"="+v);
            }
            %>"""

    elif app_type.startswith("perl"):
        xfile = "perl/env.pl"
        content = r"""#!/usr/bin/perl
print "Content-type: text/plain\r\n\r\n";
foreach my $key (sort keys %ENV) {
    print "$key=$ENV{$key}\n";
}"""

    elif app_type.startswith("python") or app_type.startswith("wsgi"):
        xfile = "wsgi/application"
        f = open(os.path.join(app_name, xfile), 'r')
        content = f.read()
        seek_str = "PATH_INFO.+/env"
        new = """
    elif environ['PATH_INFO'] == '/env.py':
        response_body = ""
        for k in os.environ.keys():
            response_body += "%s=%s\\n"%(k, os.environ[k])
"""
        content = inject_string_by_re(seek_str, new, content, after=False)
    else:
        raise Exception("Unknown cartridge: %s"%app_type)

    write_file(os.path.join(app_name, xfile) ,content)
    return git_commit_push_all(app_name)


def git_clone_app(app_name):
    git_url = OSConf.get_git_url(app_name)
    if not git_url:
        pass
    
    cmd = "git clone %s"% git_url
    (status, output) = cmd_get_status_output(cmd)
    return status


def type_to_cart(app_type):
    return ''.join(app_type.split('-')[:-1]).upper()


def random_variant(valid_variant_list=[]):
    if valid_variant_list == []:
        valid_variant_list = app_types.keys()
        try:
            valid_variant_list.remove('jenkins')
        except ValueError:
            pass
    return random.choice(valid_variant_list)
