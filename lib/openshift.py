#!/usr/bin/env python

"""
This files contains utility classes that are Openshift related.

"""

#import urllib2 as urllib
import urllib
import socks
import httplib2
import base64
import os
import json
import exceptions
import sys
from optparse import OptionParser
from common import CONNECT_TIMEOUT
import time
import traceback

import clog


class OpenShiftException(exceptions.BaseException):
    pass

class OpenShiftLoginException(OpenShiftException):
    """Authorization failed."""
    pass

class OpenShiftNullDomainException(OpenShiftException):
    """User's domain hasn't been initialized."""
    pass

class OpenShift500Exception(OpenShiftException):
    """Internal Server Error"""
    pass

#### set this to True if we want to enable performance analysis
DOING_PERFORMANCE_ANALYSIS=False


def config_parser():
    # these are required options.
    parser.set_defaults(VERBOSE=False)
    parser.set_defaults(DEBUG=False)
    parser.add_option("-d", action="store_true", dest="DEBUG", help="enable DEBUG (default true)")
    #parser.add_option("-a", "--action", help="action you want to take (list|create|store)")
    parser.add_option("-i", "--ip", default="openshift.redhat.com", help="ip addaress of your devenv")
    parser.add_option("-v", action="store_true", dest="VERBOSE", help="enable VERBOSE printing")
    parser.add_option("-u", "--user", default=None, help="User name")
    parser.add_option("-p", "--password", default=None, help="RHT password")
    (options, args) = parser.parse_args()
    
    if options.user is None:
        options.user = os.getenv('OPENSHIFT_user_email')
 
    if options.password is None:
        options.password = os.getenv('OPENSHIFT_user_passwd')

    return options, args


log = clog.get_logger()
parser = OptionParser()


# helper function for to measure timedelta.
def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        log.info("%r (%r, %r) %2.2f sec" % (method.__name__, args, kw, te-ts))
        return result

    return timed

class conditional_decorator(object):
    def __init__(self, dec, condition):
        self.decorator = dec
        self.condition = condition

    def __call__(self, func):
        if not self.condition:
            return func
        else:
            return self.decorator(func)

class Response(object):
    """
    A base Response class to derive from.  Handle the JSON response from the
    REST API

    """
    json = None
    body = None
    status = None
    headers = {}
    error = None
    url = None
    debug = False

    def __init__(self, response, body, base_url, debug=False):
        self.body = body
        self.status = response.status
        self.headers = response.items()# TODO: dict(response.getheaders())
        self.error = response.reason
        self.url = base_url
        self.parse_body()
        self.data = None

    def parse_body(self):
        """
        call JSON library to translate string JSON response to a JSON object 
        """
        if len(self.body) > 2:  # just in cases where API return just '{}'
            try:
                self.json = json.loads(self.body)
            except:
                return self.body

        # the acutal JSON response is key by the url (w/o the leading slash
            self.data =self.json['data']
        else:
            self.data = None

        if self.debug:
            self.pprint()

        return self.data

    def pprint(self):  # pretty print
        """ do pretty print of JSON response """
        print json.dumps(self.json, sort_keys=True, indent=2)

    def __unicode__(self):
        return self.pprint(self.json)

class RestApi(object):
    """
    A base connection class to derive from.
    """

    connection = None
    host = None
    port = (80, 443)
    secure = 1 # 0 or 1
    username = None
    password = None
    responseCls = Response
    headers = None
    response = None
    base_uri_root = '/broker/rest'
    base_uri = None
    verbose = False
    debug = False

    def __init__(self, host, port=80, username=username, password=password,
            debug=False, verbose=False, secure=True):
        self.host = host
        self.base_uri = 'https://%s/%s'%(host,self.base_uri_root)
        
        if username:
            self.username = username

        if password:
            self.password = password

        if verbose:
            self.verbose = verbose

        self.debug = debug
        proxy = None
        if os.getenv('http_proxy'):
            import re
            obj = re.search(r"http://([^:]+):(\d+)", os.getenv('http_proxy'))
            if obj:
                proxy_host = obj.group(1)
                proxy_port  =int(obj.group(2))
                proxy = httplib2.ProxyInfo(proxy_type=socks.PROXY_TYPE_HTTP, proxy_host=proxy_host, proxy_port=proxy_port)
            else:
                log.error("Warning: Wrong format of http_proxy!")

        self.connection = httplib2.Http(cache=None, timeout=CONNECT_TIMEOUT, proxy_info=proxy, disable_ssl_certificate_validation=True)

    def connect(self, host=None, port=80, headers=None):
        if host:
            self.host = host

        if port:
            self.port = port 
        else:
            self.port = self.port[self.secure]
        kwargs = {'host': host, 'port': port, 'timeout': CONNECT_TIMEOUT}
        connection = httplib2.Http(**kwargs)
        self.connection = connection
        return connection

    def _get_auth_headers(self, username=None, password=None):
        if username:
            self.username = username
        if password:
            self.password = password

        if 'OPENSHIFT_REST_API' in os.environ:
            HEADER_ACCEPT = 'application/json;version=' + str(os.environ['OPENSHIFT_REST_API'])
        else:
            HEADER_ACCEPT = 'application/json'
        return {
                "Content-type": "application/x-www-form-urlencoded",
                'Authorization':
                    "Basic %s"
                    % base64.b64encode('%s:%s' % (self.username, self.password)),
                'Accept': HEADER_ACCEPT 
                }


    def request(self, url, method, headers=None, params=None):
        conn = self.connection
        if url.startswith("https://") or url.startswith("http://") :
            self.url = url
        else:
            self.url = self.base_uri + url

        log.debug("URL: %s" % self.url)
        if self.headers is None:
            self.headers = self._get_auth_headers(self.username, self.password)
        else:
            self.headers.update(self._get_auth_headers(self.username, self.password))
        if headers is not None:
            self.headers.update(headers)

        response = None
        content = None
        try:
            if method == 'GET':
                (response, content) = conn.request(uri=self.url, method=method, headers=self.headers)
            else:
                (response, content) = conn.request(uri=self.url, method=method, body=params, headers=self.headers)

        except Exception as e:
            print >>sys.stderr, "-"*80
            traceback.print_exc(file=sys.stderr)
            print >>sys.stderr, "-"*80
            raise e

        raw_response = content
        self.response = Response(response, content, self.url)
        self.data = self.response.parse_body()

        # Workaround for bug 913796
        #add some debug messages if response is else than OK
        '''
        if self.response.error not in ('OK', 'Created', 'Not Content'):
            print >>sys.stderr, "-"*80
            log.debug("Response of non 'OK' [status/data]: %s/%s"%(self.response.error, self.data))
            print >>sys.stderr, "-"*80
        '''
        if self.response.status == 200:
            status = 'OK'
        else:
            status = self.response.error
        return (status, raw_response)
    

    def GET(self, url):
        """ wrapper around request() """
        url = self.base_uri
        res = self.request(url, method="GET")
        return res

    def POST(self, data):
        """ do a REST API POST """
        return self.connection.request(url=self.url, headers=self.headers, body=data, method='POST')
    
    def PUT(self, url, data):
        return self.connection.request(url=self.url, params=data, method='PUT')

class Openshift(object):
    """
    wrappers class around REST API so use can use it with python
    """
    rest = None
    user = None
    passwd = None
    def __init__(self, host, user=None, passwd=None, debug=False, verbose=False, logger=None):
        if user:
            self.user = user
        if passwd:
            self.passwd = passwd
        if logger:
            global log
            log = logger
        self.rest = RestApi(host=host, username=self.user, password=self.passwd, debug=debug, verbose=verbose)
        # Hot fix for Bug 987799
        self.cart_list_url = ''
        if 'OPENSHIFT_REST_API' in os.environ:
            self.REST_API_VERSION = float(os.environ['OPENSHIFT_REST_API'])
        else:
            # just get the latest version returned from the server
            api_version, api_version_list = self.api_version()
            self.REST_API_VERSION = api_version 

    def get_href(self, top_level_url, target_link, domain_name=None):
        status, res = self.rest.request(method='GET', url=top_level_url)
        index = target_link.upper()
        if status == 'Authorization Required':
            #log.error("Authorization failed. (Check your credentials)")
            raise OpenShiftLoginException('Authorization Required')

        if self.rest.response.json is None:
            raise OpenShift500Exception(status)

        if domain_name is None:
            if self.rest.response.json['data']:
                res = self.rest.response.json['data'][0]['links'][index]
                return (res['href'], res['method'])
            else:
                raise OpenShiftNullDomainException("No domain has been initialized.")
                #return ('Not Found', self.rest.response.json)

        else:  # domain name is specified, now find a match
            json_data = self.rest.response.json['data']
            if json_data:
                for jd in json_data:
                    if jd['name'] == domain_name:
                        res = jd['links'][index]
                        return (res['href'], res['method'])
                ### if here, then user has given a domain name that does not match what's registered with the system
                return("Not Found", None)
            else:
                return(None, None)
        
    ##### /user  (sshkey)
    #@conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def get_user(self):
        log.debug("Getting user information...")
        (status, raw_response) = self.rest.request(method='GET', url='/user')
        if status == 'OK':
            return (status, self.rest.response.json['data']['login'])
        else:
            return (status, raw_response)
    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS) 
    def keys_list(self):
        log.debug("Getting ssh key information...")
        (status, raw_response) = self.rest.request(method='GET', url='/user/keys')
        return (status, raw_response)

    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def key_add(self, kwargs):
        """
        params: {name, type, key}
        """
        if not kwargs.has_key('key'):
            # use a default path
            sshkey = '~/.ssh/id_rsa.pub'
        else:
            sshkey = kwargs['key']
        ssh_path = os.path.expanduser(sshkey)
        ssh_key_str = open(ssh_path, 'r').read().split(' ')[1]
        print ssh_key_str

        if kwargs.has_key('impersonate'):
            self.headers = {'X-Impersonate-User':kwargs['impersonate']}

        if not kwargs.has_key('name'):

            kwargs['name'] = 'default'
        
        if not kwargs.has_key('type'):
            kwargs['type'] = 'ssh-rsa'
        
        data_dict = {
                    'name': kwargs['name'],
                    'type': kwargs['type'],
                    'content': ssh_key_str
                    }

        params = urllib.urlencode(data_dict)
        status, raw_response = self.rest.request(method='POST', url='/user/keys', params=params)
        return (status, raw_response)

    def key_update(self, kwargs):
        """
        params: {name, type, key}
        """
        if not kwargs.has_key('key'):
            # use a default path
            sshkey = '~/.ssh/id_rsa.pub'
        else:
            sshkey = kwargs['key']
        ssh_path = os.path.expanduser(sshkey)
        ssh_key_str = open(ssh_path, 'r').read().split(' ')[1]

        if kwargs.has_key('impersonate'):
            self.headers = {'X-Impersonate-User':kwargs['impersonate']}

        if not kwargs.has_key('name'):

            kwargs['name'] = 'default'

        if not kwargs.has_key('type'):
            kwargs['type'] = 'ssh-rsa'

        data_dict = {
                    'name': kwargs['name'],
                    'type': kwargs['type'],
                    'content': ssh_key_str
                    }

        params = urllib.urlencode(data_dict)
        status, raw_response = self.rest.request(method='POST', url='/user/keys', params=params)
        return (status, raw_response)

    ##### /domains
    #@conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def domain_create(self, name, impersonate=None):
        log.debug("Creating domain '%s'" % name)
        TESTDATA = {
        'name': name,
        'rhlogin': self.user
        }

        params = urllib.urlencode(TESTDATA)

        if impersonate:
            self.headers['X-Impersonate-User'] = impersonate

        self.rest.request(method='POST', url='/domains', params=params)
        """
        if self.rest.response.status == 201:
            log.info("Domain name '%s' created successfully." % name)
        else:
            log.info("Domain creation failed, reason: %s" % self.rest.response.json['messages'])
        """
        return self.rest.response.status, self.rest.response.body

    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def domain_delete(self, domain_name=None, force=True):
        """ destory a user's domain, if no name is given, figure it out"""
        if domain_name is None:
            status, res = self.domain_get()
            domain_name = status[1]


        url, method = self.get_href('/domains', 'delete', domain_name)
        #log.info("URL: %s" % url)
        #res = self.rest.response.data[0]['links']['DELETE']
        if force:
            params = urllib.urlencode({'force': 'true'})
        if url:
            (status, raw_response)= self.rest.request(method=method,  url=url, params=params)
        else:  ## problem
            return (url, raw_response)

    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def domain_get(self, name=None):
        log.debug("Getting domain information...")
        url, method = self.get_href('/domains', 'get', name)
        
        if self.REST_API_VERSION < 1.6:
            domain_index_name = 'id'
        else:
            domain_index_name = 'name'

        if url == 'Not Found':
            return ('Not Found', None)
        else:
            (status, raw_response) = self.rest.request(method=method, url=url)

            if status == 'OK':
                return (status, self.rest.response.json['data'][domain_index_name])

    def domain_update(self, new_name):
        params = urllib.urlencode({'name': new_name})
        url, method = self.get_href("/domains", 'update')
        (status, res) = self.rest.request(method=method, url=url, params=params)
        return (status, res)

    def app_list(self):
        url, method = self.get_href('/domains', 'list_applications')
        (status, res) = self.rest.request(method=method, url=url)
        #print status, res
        #print self.rest.response.json['data']
        #return (status, res.json['data'])
        return (status, self.rest.response.json['data'])
        #jres = json.loads(res)
        #return (status, jres['data'])

    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def app_create(self, app_name, app_type, scale='false', init_git_url=None, template_uuid=None):
        url, method = self.get_href('/domains', 'add_application')
        #valid_options = self.rest.response.json['data'][0]['links']['ADD_APPLICATION']['optional_params'][0]['valid_options']
        #if app_type not in valid_options:
        #    log.error("The app type you specified '%s' is not supported!" % app_type)
        #    log.debug("supported apps types are: %s" % valid_options)
        if init_git_url:
            data_dict = {'name':app_name, 'scale': scale, 'init_git_url': init_git_url}
        else:
            data_dict = {'name':app_name, 'scale': scale }

        params = urllib.urlencode(data_dict)
        if type(app_type) is list:
            is_str = all(isinstance(i, str) for i in app_type)
            if is_str:
                carts = "&" + urllib.urlencode([('artridges[]', i) for i in app_type])
            else: # it's a list of dictionary {'name': <cart_name>}
                carts = "&" + urllib.urlencode([('cartridges[]', i['name']) for i in app_type])
        else:
            cart_param = {
                         'cartridges' : app_type,
                         }
            carts = "&" + urllib.urlencode(cart_param)
        if template_uuid:
            data_dict['template'] = template_uuid
            del data_dict['cartridges']
        params = params + carts
        (status, res) = self.rest.request(method=method, url=url, params=params)
        return (status, res)

    ##### /cartridges
    def cartridges(self):
        (status, raw_response) = self.rest.request(method='GET', url='/cartridges')
        if status == 'OK':
            # return a list of cartridges that are supported
            return (status, self.rest.response.json['data'])
        else:
            return (status, raw_response)

    ##### /api  get a list of support operations
    def api(self):
        #log.debug("Getting supported APIs...")
        (status, raw_response) = self.rest.request(method='GET', url='/api')
        return (status, raw_response)
    
    def api_version(self):
        # return the current version being used and the list of supported versions
        status, res = self.api()
        json_obj = json.loads(res)
        return (float(json_obj['version']), json_obj['supported_api_versions'])
        
    ##### helper functions
    def do_action(self, kwargs):
        op = kwargs['op_type']
        if op == 'cartridge':
            status, res = self.cartridge_list(kwargs['app_name'])
        elif op == 'keys':
            status, res = self.keys_list()

        json_data = self.rest.response.json
        action = kwargs['action']
        name = kwargs['name']
        raw_response = None
        for data in json_data['data']:
            if data['name'] == name:
                params = data['links'][action]
                log.debug("Action: %s" % action)
                if len(params['required_params']) > 0:
                    # construct require parameter dictionary
                    data = {}
                    for rp in params['required_params']:
                        param_name = rp['name']
                        if kwargs['op_type'] == 'cartridge':
                            data[param_name] = action.lower()
                        else:
                            data[param_name] = kwargs[param_name]
                    data = urllib.urlencode(data)
                else:
                    data = None
                # Hot fix for Bug 987799
                if op == 'cartridge' and action == 'GET':
                    href = self.cart_list_url + '/' + name
                else:
                    href = params['href']
                log.debug("Cart URL: %s" % href)
                #(status, raw_response) =  self.rest.request(method=params['method'], 
                #                                    url=href,
                #                                    params=data)
                (status, raw_response) =  self.rest.request(method=params['method'], 
                                                    url=params['href'],
                                                    params=data)
                return (status, self.rest.response.json)

        return (status, raw_response)

    #### application tempalte
    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def app_templates(self):
        (status, raw_response) = self.rest.request(method='GET', url='/application_template')
        if status == 'OK':
            return (status, self.rest.response.json)
        else:
            return (status, raw_response)

    ##### keys
    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def key_delete(self, key_name):
        """
        li.key_delete('ssh_key_name')

        """
        params = {"action": 'DELETE', 'name': key_name, "op_type": 'keys'}
        return self.do_action(params)

    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)    
    def key_update(self, kwargs): #key_name, key_path, key_type='ssh-rsa'):
        """
        li.key_update({'name': 'new_key_name', 'key': new_key_path})

        """
        key_path = kwargs['key']
        key_name = kwargs['name']
        if kwargs.has_key('key_type'):
            key_type = kwargs['key_type']
        else:
            key_type = 'ssh-rsa'
        ssh_path = os.path.expanduser(key_path)
        ssh_key_str = open(ssh_path, 'r').read().split(' ')[1]

        params = {'op_type':'keys', 'action': 'UPDATE', 'name': key_name, 'content': ssh_key_str, 'type': key_type}
        return self.do_action(params)
    
    @conditional_decorator(timeit, DOING_PERFORMANCE_ANALYSIS)
    def key_get(self, name):
        """
        li.key_get('target_key_name')
        returns the actual key content :$
        
        """
        #params = {'action': 'GET', 'name': name, 'op_type': 'keys'}
        url = "/user/keys/" + name
        (status, raw_response) = self.rest.request(method='GET', url=url)
        if status == 'OK':
            return status, self.rest.response.json['data']
        else:
            return (status, raw_response)

    def key_action(self, kwargs):
        status, res = self.keys_list()
        json_data = self.rest.response.json
        action = kwargs['action']
        name = kwargs['name']
        for data in json_data['data']:
            if data['name'] == name:
                params = data['links'][action]
                log.debug("Action: %s" % action)
                if len(params['required_params']) > 0:
                    # construct require parameter dictionary
                    data = {}
                    for rp in params['required_params']:
                        param_name = rp['name']
                        data[param_name] = kwargs[param_name]
                    data = urllib.urlencode(data)
                else:
                    data = None
                break
        (status, raw_response) =  self.rest.request(method=params['method'], 
                                                    url=params['href'], 
                                                    params=data)
        return (status, raw_response)





    ##### apps
    @timeit
    def app_create_scale(self, app_name, app_type, scale='true'):
        return self.app_create(app_name=app_name, app_type=app_type, scale=scale)
        
    @timeit
    def app_delete(self, app_name):
        params = {'action': 'DELETE', 'app_name': app_name}
        return self.app_action(params)
    @timeit
    def app_start(self, app_name):    
        params = {"action": 'START', 'app_name': app_name}
        return self.app_action(params)
    @timeit 
    def app_stop(self, app_name):
        params = {"action": 'STOP', 'app_name': app_name}
        return self.app_action(params)
    @timeit
    def app_restart(self, app_name):
        params = {"action": 'RESTART', 'app_name': app_name}
        return self.app_action(params)
    @timeit
    def app_force_stop(self, app_name):
        params = {"action": 'FORCE_STOP', 'app_name': app_name}
        return self.app_action(params)
    @timeit
    def app_get_descriptor(self, app_name):
        params = {'action': 'GET', 'app_name': app_name}
        return self.app_action(params)
    
    def app_get(self, app_name):
        params = {'action': 'GET', 'app_name': app_name}
        status, res = self.app_action(params)
        if status == 'OK':
            data_json = self.rest.response.json['data']
            return status, data_json
        else:
            return status, res

    #############################################################
    # event related functions
    #############################################################
    def app_scale_up(self, app_name):
        params = {'action': 'SCALE_UP', 'app_name': app_name}
        return self.app_action(params)

    def app_scale_down(self, app_name):
        params = {'action': 'SCALE_DOWN', 'app_name': app_name}
        return self.app_action(params)
    
    def app_add_alias(self, app_name, alias):
        params = {'action': 'ADD_ALIAS', 'app_name': app_name, 'alias': alias}
        return self.app_action(params)
  
    def app_remove_alias(self, app_name, alias):
        params = {'action': 'REMOVE_ALIAS', 'app_name': app_name, 'alias': alias}
        return self.app_action(params)

    def app_get_estimates(self):
        url, method = self.get_href('/estimates', 'get_estimate')
        (status, res) = self.rest.request(method=method, url=url)
        return (status, self.rest.response.json['data'])

        #params = {'action': 'GET_ESTIMATE'}
        #return self.app_action(params)
        
    def app_action(self, params):
        """ generic helper function that is capable of doing all the operations
        for application
        """
        # step1. find th url and method
        status, res = self.app_list()

        app_found = False
        action = params['action']
        if params.has_key('app_name'):
            app_name = params['app_name']
        if params.has_key('cartridge'):
            cart_name = params['cartridge']

        for app in res:
        #for app in res['data']:

            if app['name'] == app_name:
                # found match, now do your stuff
                params_dict = app['links'][action]
                method = params_dict['method']
                log.info("Action: %s" % action)
                data = {}
                if len(params_dict['required_params']) > 0:
                    param_name = params_dict['required_params'][0]['name']
                    rp = params_dict['required_params'][0]
                    #data[param_name] = cart_name #'name'] = rp['name']
                    for rp in params_dict['required_params']:
                        # construct the data 
                        param_name = rp['name']
                        if param_name == 'event':
                            if isinstance(rp['valid_options'],list):
                                data[param_name] = rp['valid_options'][0] 
                            else:
                                data[param_name] = rp['valid_options']
                        elif param_name == 'name':
                            data[param_name] = params['cartridge']
                        else:
                            data[param_name] = params[param_name] #cart_name #params['op_type']
                            #data[param_name] = params[param_name]
                    data = urllib.urlencode(data)
                else:
                    data = None
                req_url = params_dict['href']
                # Hot fix for Bug 987799
                if action == 'LIST_CARTRIDGES':
                    self.cart_list_url = req_url
                #print "DATA: %s, URL: %s, METHOD: %s " % (data, req_url, method)
                (status, raw_response) =  self.rest.request(method=method, url=req_url, params=data)
                app_found = True
                return (status, raw_response)
        if not app_found:
            log.error("Can not find app matching your request '%s'"% app_name)
            return ("Error", None)

    def get_gears(self, app_name, domain_name=None):
        """ return gears information """
        params = {"action": 'GET_GEAR_GROUPS', 'app_name': app_name}
        status, res =  self.app_action(params)
        gear_count = 0
        for gear_group in self.rest.response.json['data']:
            gear_count += len(gear_group['gears'])
        return (self.rest.response.json['data'], gear_count) 

    ################################
    # cartridges
    ################################
    def cartridge_list(self, app_name):
        params = {"action": 'LIST_CARTRIDGES', 'app_name': app_name}
        return self.app_action(params)

    def cartridge_add(self, app_name, cartridge):
        params = {"action": 'ADD_CARTRIDGE', 'app_name': app_name,
            'cartridge': cartridge}
        status, res = self.app_action(params)
        return (status, self.rest.response.json['messages'])
    
    def cartridge_delete(self, app_name, name):
        params = {"action": 'DELETE', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)
    
    def cartridge_start(self, app_name, name):
        params = {"action": 'START', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)
    
    def cartridge_stop(self, app_name, name):
        params = {"action": 'STOP', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)
     
    def cartridge_restart(self, app_name, name):
        params = {"action": 'RESTART', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)
    
    def cartridge_reload(self, app_name, name):
        params = {"action": 'RELOAD', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)
 
    def cartridge_get(self, app_name, name):
        params = {"action": 'GET', 'name': name, "op_type": 'cartridge', 'app_name': app_name}
        return self.do_action(params)


    def app_template_get(self):
        """ returnn a list of application template from an app """
        status, res = self.rest.request(method='GET', url='/application_template')
        if status == 'OK':
            return (status, self.rest.response.json['data'])
        else:
            return (status, res)
        
############################################################################
# helper functions
############################################################################

def get_black_list(rest_obj):
    status, res = rest_obj.api()
    json_obj = json.loads(res)
    black_list = json_obj['data']['ADD_DOMAIN']['required_params'][0]['invalid_options']
    return black_list

def sortedDict(adict):
    keys = adict.keys()
    keys.sort()
    return map(adict.get, keys)

def perf_test(li):
    cart_types = ['php-5.3']
    od = {  
        1: {'name': 'app_create', 'params': {'app_name': 'perftest'}},
        #2: {'name': 'app_delete', 'params': {'app_name': 'perftest'}},
        }
    sod = sortedDict(od)
    #li.domain_create('blahblah')
    cart_types = ['php-5.3']#'php-5.3', 'ruby-1.8', 'jbossas-7']
    for cart in cart_types:
        for action in sod:
            method_call = getattr(li, action['name'])
            k, v = action['params'].items()[0]
            if action['name'] == 'app_create':
                method_call(v, cart)
            else:
                method_call(v)


if __name__ == '__main__':
    (options, args) = config_parser()
    li = Openshift(host=options.ip, user=options.user, passwd=options.password,
        debug=options.DEBUG,verbose=options.VERBOSE)
    #status, res = li.app_get_descriptor('xxxx')
    #status, res = li.get_gears('myjboss')
    #status, res = li.app_get_estimates()
    status, res = li.domain_get(name=None)
    #app_type = [{'name': 'php-5.3'}, {'name':'mysql-5.1'}, {'name':'phpmyadmin-3.4'}]
    #status, res = li.app_create(app_name="app1", app_type=app_type,
    #        init_git_url="https://github.com/openshift/wordpress-example")
    #print "STAUS: %s" % status
    #app_type=["ruby-1.9", "rockmongo-1.1"]
    #status, res = li.app_create(app_name="app4", app_type=app_type)
    #status, res = li.app_create(app_name="app3", app_type='nodejs-0.6')
    #status, res = li.cartridge_add(app_name='app1', cartridge='mysql-5.1') #restart_app('myruby')
    #status, res = li.cartridge_delete(app_name='app1', name='mysql-5.1')
    #status, res = li.domain_delete(domain_name='pruan08')
    self.info('xxx', 1)
    #status, res = li.get_gears('27qxjfyjeo')
    #status, res = li.app_get('27qxjfyjeo')
    #self.info("xxx", 1)
    #status, res = li.app_template_get() #app_get_descriptor('myapp2php')
    #li.app_remove_alias('php', 'new_name')
    #li = Openshift(host="stg.openshift.redhat.com")
    #li = Openshift(host='107.20.38.71')
    #status, res = li.domain_create('pppx')

    #status, res = li.get_user()
    #gear, count = li.get_gears(app_name='php')
    #self.info("xxx",1 )
    #status, res = li.app_list()
    #self.info("xxx", 1)
    #perf_test(li)
    
    #status, res = li.add_application('abcdefg0123456789012345678901234567890', 'php-5.3')
    #li.create_domain('testbcc09a')
    #status, res = li.get_domain()
    #li.delete_domain(force=True)#delete_domain("testapp")
    #self.info("xx",1 )
    #status, res = li.add_key({'name': 'default', 'key':'~/.ssh/libra_id_rsa.pub'})
    #self.info("xxx", 1)
    #li = Openshift(host='50.16.148.99') #107.21.64.242') 
    #status, res = li.get_cartridge(app_name='myphp', name='mongodb-2.2')
    #og.debug("STATUS: %s" % status)
    #status, res = li.reload_cartridge(app_name='myphp', name='phpmyadmin-3.4') #restart_app('myruby')
    #log.debug('STATUS: %s' % status)    

 
    #status, res = li.delete_domain(force=True)
    #status, res = li.cartridges() 
    #status, res = li.list_cartridges('myruby')
    #status, res = li.cartridge_add(app_name='myapp', cartridge='mysql-5.1') #restart_app('myruby')
    #status, res = li.cartridge_delete(app_name='myapp', name='mysql-5.1')
    
    #self.info("xxx", 1)
    #status, res = li.delete_cartridge(app_name='myphp', name='mongodb-2.2') #restart_app('myruby')
    #status, res = li.delete_app('myperl')
    #status, res = li.add_application('myperl', 'perl-5.10')
    #status, res = li.delete_app(myperl')
    
#
    #stat, res = li.create_domain('ab012345678901234567890123456789')
    #stat, res = li.delete_app('ab012345678901234567890123456789')
    #self.info("xxx", 1)
    #status, res = li.get_domain()
    #log.info("status: %s" % status)
    
    #li.add_application('myruby',  'ruby-1.8')
    #li.add_application('myphp',  'php-5.3')
    #status, res = li.update_domain('pnew')
    #self.info("xxx", 1)
    #key = li.get_key('new1') #{'name':'new1'})
    #key_content = li.get_key(name='key1')
    #status, res = li.update_key({'name': 'new1', 'key':'~/.ssh/test.pub'})
    #li.delete_key({'name': 'newkey1', 'key': '~/.ssh/test.pub'})


 
