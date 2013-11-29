import os
from helper import get_instance_ip

if os.environ.has_key('RHTEST_ORIGIN') and os.environ['RHTEST_ORIGIN'] == '1':
    app_types = {
            'php'        : 'php-5.4',
            'ruby'       : 'ruby-1.9',
            'ruby-1.9'   : 'ruby-1.9',
            'rack'       : 'ruby-1.9',   #for backward compatibility...
            'python'     : 'python-2.7',
            'python-3.3' : 'python-3.3',
            'perl'       : 'perl-5.16' ,
            'raw'        : 'diy-0.1',
            'diy'        : 'diy-0.1',
            'nodejs'     : 'nodejs-0.6',
            'jenkins'    : 'jenkins-1.4'}
    cartridge_types = {
            'mongodb'       : 'mongodb-2.2',
            'mongo'         : 'mongodb-2.2',
            'cron'          : 'cron-1.4',
            'mysql'         : 'mysql-5.1',
            'postgresql'    : 'postgresql-9.2',
            'postgresql-9.2'    : 'postgresql-9.2',
            '10gen'         : '10gen-mms-agent-0.1',
            'phpmyadmin'    : 'phpmyadmin-3.4',
            'metrics'       : 'metrics-0.1',
            'phpmoadmin'    : 'phpmoadmin-1.0',
            'switchyard'    : 'switchyard-0.6',
            'haproxy'       : 'haproxy-1.4 ',
            'jenkins-client': 'jenkins-client-1.4',
            'jenkins'       : 'jenkins-client-1.4'}
else:
    app_types = { 'jbossas': 'jbossas-7',
                  'jbosseap-6.0': 'jbosseap-6',
                  'jbosseap': 'jbosseap-6',
                  'jbossews': 'jbossews-1.0',
                  'jbossews-1.0': 'jbossews-1.0',
                  'jbossews-2.0': 'jbossews-2.0',
                  'jbossews2': 'jbossews-2.0',
                  'php': 'php-5.3',
                  'ruby': 'ruby-1.8',
                  'ruby-1.8': 'ruby-1.8',
                  'ruby-1.9': 'ruby-1.9',
                  'rack': 'ruby-1.8',   #for backward compatibility...
                  'python': 'python-2.6',
                  'python-2.6': 'python-2.6',
                  'python27': 'python-2.7',
                  'python-2.7':'python-2.7',
                  'python-3.3':'python-3.3',
                  'wsgi': 'python-2.6', #for backward compatibility...
                  'perl-5.10': 'perl-5.10',
                  'perl': 'perl-5.10' ,
                  'raw':  'diy-0.1',
                  'diy':  'diy-0.1',
                  'diy-0.1': 'diy-0.1',
                  'nodejs-0.6': 'nodejs-0.6',
                  'nodejs': 'nodejs-0.6',
                  'nodejs-0.10': 'nodejs-0.10',
                  'jenkins' : 'jenkins-1',
                  'zend' : 'zend-5.6'}
    cartridge_types = { 'mongodb' : 'mongodb-2.2',
                   'mongodb2.0' : 'mongodb-2.0',
                   'cron': 'cron-1.4', 
                   'mysql': 'mysql-5.1', 
                   'postgresql' : 'postgresql-8.4', 
                   'postgresql-9.2' : 'postgresql-9.2', 
                   '10gen' : '10gen-mms-agent-0.1', 
                   'phpmyadmin': 'phpmyadmin-4', 
                   'haproxy': 'haproxy-1.4', 
                   'metrics' : 'metrics-0.1', 
                   'phpmoadmin' : 'phpmoadmin-1.0', 
                   'rockmongo': 'rockmongo-1.1', 
                   'jenkins' : 'jenkins-client-1'}

APP_TYPES = app_types
CARTRIDGE_TYPES = cartridge_types

cartridge_deps = {'10gen': 'mongodb', 
                  'phpmyadmin': 'mysql', 
                  'phpmoadmin': 'mongodb', 
                  'rockmongo': 'mongodb'}

CARTRIDGE_DEPS = cartridge_deps

APP_SUFFIX = {"php": ".php",
              "nodejs": '.js',
              "ruby": ".rb",
              "ruby-1.9" : ".rb",
              "rack": ".rb",
              "jbossas": ".jsp",
              "jbosseap": ".jsp",
              "jbossews": ".jsp",
              "perl": ".pl",
              "python": ".py",
              "wsgi": ".py"}


MAX_GEARS = 3             # normal max gears count
DEV_MAX_GEARS = 20       # max gears count used for testing on DEV

RHC_CLIENT_TIMEOUT = 360

instance_ip = get_instance_ip()
if instance_ip == 'int.openshift.redhat.com':
    run_mode = 'INT'
elif instance_ip == 'stg.openshift.redhat.com':
    run_mode = 'STG'
elif instance_ip == 'openshift.redhat.com':
    run_mode = 'PROD'
elif instance_ip.find("example.com") != -1 or instance_ip.find("test.com") != -1 or instance_ip.find("broker") != -1:
    run_mode = 'OnPremise'
else:
    run_mode = 'DEV'

if os.environ.has_key('RHTEST_RHC_CLIENT_OPTIONS'):
    RHTEST_RHC_CLIENT_OPTIONS = os.getenv('RHTEST_RHC_CLIENT_OPTIONS')
else:
     RHTEST_RHC_CLIENT_OPTIONS = "--insecure --timeout %s"% RHC_CLIENT_TIMEOUT
    #if run_mode in ('DEV', 'INT'):
    #    RHTEST_RHC_CLIENT_OPTIONS = "--insecure --timeout %s"% RHC_CLIENT_TIMEOUT
    #else:
    #    RHTEST_RHC_CLIENT_OPTIONS = "--timeout %s"% RHC_CLIENT_TIMEOUT

# For all of the network operations:
if os.getenv('RHTEST_REST_TIMEOUT'):
    CONNECT_TIMEOUT=os.getenv('RHTEST_REST_TIMEOUT')
else:
    CONNECT_TIMEOUT=360

