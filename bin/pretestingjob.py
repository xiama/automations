#!/usr/bin/env python
import os
import sys
import commands
import re
import time
import yaml
import random
import string
import fcntl
import pymongo
from urllib import quote, unquote
from pymongo.errors import *
from bson.objectid import ObjectId

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class DotDict(object):

    def __getattr__(self, name):
        return self.data[name]

    def __setattr__(self, name, value):
        if not self.__dict__.has_key('data'):
            self.__dict__['data'] = {}
        self.__dict__['data'][name] = value


class DefaultValueDict(dict):
    DEFAULT = {'instance_count' : 1, 'job_count' : 2}

    def __getitem__(self, key):
        if not self.has_key(key):
            return DefaultValueDict.DEFAULT
        else:
            return super(DefaultValueDict, self).__getitem__(key)

class PreTestingJob(object):
    KEY_PATH = os.path.join(SCRIPT_PATH, '..', 'etc', 'libra.pem')
    IP_ADDR = '184.73.182.48'
    FILE_PATH = '/var/lib/jenkins/fork_ami_qe_test_queue'
    TESTPLAN_ID = '4962'
    PLAN =  DefaultValueDict({  'fullfunction'  :   {'instance_count' : 2, 'job_count' : 6},
                                'stage'         :   {'instance_count' : 2, 'job_count' : 6},
                                'acceptance'    :   {'instance_count' : 2, 'job_count' : 4},
                                'smoke'         :   {'instance_count' : 1, 'job_count' : 2},
            })

    def __init__(self):
        # Change key file permission
        os.system("chmod 600 %s" % (PreTestingJob.KEY_PATH))
        # Setup environment variables
        os.environ['RHTEST_HOME'] = os.path.abspath(os.curdir)
        os.environ['PATH'] = os.path.expandvars(os.path.expanduser('${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PATH'))
        os.environ['PYTHONPATH'] = os.path.expandvars(os.path.expanduser('${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PYTHONPATH'))
        # Init kerberos
        if not self.init_kerberos():
            print 'Failed to init kerberos. Please check your TCMS_USER and TCMS_PASSWORD'
            sys.exit(255)
        # Init parameters
        self.init_params()
        if not self.preprocess():
            sys.exit(255)
        # Connect to mongodb
        mongo_url = os.environ['MONGO_CONN_URL']
        try:
            self.conn = pymongo.Connection('mongodb://%s' % (mongo_url))
        except ConnectionFailure:
            print 'Error: Failed to connect to MongoDB at %s. Please check your system configurations.' % (mongo_url)
            sys.exit(255)
        self.db = self.conn['devenv']

    def __del__(self):
        # Disconnect from MongoDB
        if hasattr(self, 'conn'):
            self.conn.close()

    def get_instance_tag(self, ami_id):
        return 'QE_auto_%s' % (ami_id)

    def get_testrun_tag(self, testcase_tags, ami_id=None):
        result = 'Test Run for %s Testing' % (testcase_tags)
        if ami_id == None:
            return result
        else:
            return ' - '.join([result, ami_id])

    def get_ami_tags(self): # get ami_id and testcase_tags from remote machine for fork ami testing
        # Get lock
        try:
            f = file(".trigger.lock", "w")
            fcntl.flock(f, fcntl.LOCK_EX)
        except IOError, e:
            fcntl.flock(f, fcntl.LOCK_UN)
            print "Failed to create lock file\n", e
            return None
        except ValueError, e:
            print 'Failed to get lock\n', e
            f.close()
            return None
        # Get the first line
        cmd = 'ssh -t -t -q -i %s -o StrictHostKeyChecking=no -o ConnectTimeout=20 root@%s \"head -n 1 %s\"' % (    PreTestingJob.KEY_PATH,
                                                                                                PreTestingJob.IP_ADDR,
                                                                                                PreTestingJob.FILE_PATH)
        (ret, output) = commands.getstatusoutput(cmd)
        if ret != 0:
            print 'Failed to get the first line of %s on %s' % (PreTestingJob.FILE_PATH, PreTestingJob.IP_ADDR)
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
            return None
        try:
            print "The first line of remote file:\n%s\n" % (output)
            # Get ami id and test tags
            output = output.strip().replace(' ','')
            match = re.search(r'([\w\-_]+)=(\w+[\w,]*)', output, re.M)
            ami_id = match.group(1)
            testcase_tags = match.group(2)
            print '\nFound ami id and test case tags in remote file'
            print 'ami id: %s, test case tags: %s\n' % (ami_id, testcase_tags)
        except AttributeError, e:
            print "No fork ami found in remote file. The job will quit."
            sys.exit(0)
        finally:
            # Remove the first line
            cmd = "ssh -t -t -q -i %s -o StrictHostKeyChecking=no -o ConnectTimeout=20 root@%s \"sed -i -e '1 d' %s\"" % (  PreTestingJob.KEY_PATH,
                                                                                                    PreTestingJob.IP_ADDR,
                                                                                                    PreTestingJob.FILE_PATH)
            (ret, output) = commands.getstatusoutput(cmd)
            if ret != 0:
                print 'Warning!!! Failed to delete the first line of %s on %s' % (PreTestingJob.FILE_PATH, PreTestingJob.IP_ADDR)
            # Release lock
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()
        return (ami_id, testcase_tags)

    def get_build_uuid(self, length = 32):
        random.seed()
        return random.choice(string.ascii_lowercase) + ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(0, length-1))

    def get_instance_count(self, testcase_tags):
        for testcase_tag in ['fullfunction', 'stage', 'acceptance', 'smoke']:
            if testcase_tag in testcase_tags:
                return PreTestingJob.PLAN[testcase_tag]['instance_count']
        return DefaultValueDict.DEFAULT['instance_count']

    def get_job_count(self, testcase_tags):
        for testcase_tag in ['fullfunction', 'stage', 'acceptance', 'smoke']:
            if testcase_tag in testcase_tags:
                return PreTestingJob.PLAN[testcase_tag]['job_count']
        return DefaultValueDict.DEFAULT['job_count']

    def user_email_generator(self, prototype):
        if '@' in prototype:
            parts = prototype.split('@')
        else:
            parts = [prototype, 'redhat.com']
        i = 1
        while True:
            first_part = ''.join([parts[0], '+%d' % (i)])
            yield '@'.join([first_part, parts[1]])
            i += 1

    def get_users(self, count=None):
        result = {}
        if self.config.openshift_users != None:
            for pair in self.config.openshift_users.splitlines():
                try:
                    [email, passwd] = pair.split(':')
                except ValueError:
                    print 'Invalid OPENSHIFT_USERS'
                    return None
                result[email] = passwd
        elif self.config.openshift_user_prototype != None:
            if count == None:
                return None
            try:
                [email, passwd] = self.config.openshift_user_prototype.split(':')
            except ValueError:
                print 'Invalid OPENSHIFT_USER_PROTOTYPE'
                return None
            iuser = self.user_email_generator(email)
            for i in range(count):
                result[iuser.next()] = passwd
        else:
            return None
        return result

    def init_kerberos(self):
        cmd = 'cd bin/ && ./kinit.sh'
        if os.system(cmd) != 0:
            return False
        return True

    def init_params(self):
        self.config = DotDict()
        self.param_list = ['INSTANCES', 'INSTANCE_TAG', 'AMI_ID', 'TESTRUN_ID', 'TESTRUN_TAG', 'TESTCASE_TAGS', 'SUB_JOB_NAME', 'INSTANCE_COUNT', 'JOB_COUNT', 'OPENSHIFT_USER_PROTOTYPE', 'OPENSHIFT_USERS', 'SHUTDOWN_INSTANCE', 'RESET_TESTRUN', 'UPDATE_CLIENT', 'RHC_VERSION', 'RHC_BRANCH', 'TCMS_USER', 'TCMS_PASSWORD']
        for param in self.param_list:
            setattr(self.config, param.lower(), os.environ.get(param))

    def strip_params(self):
        # Remove spaces from parameters
        for param in self.param_list:
            value = getattr(self.config, param.lower())
            if value != None:
                if param in ['INSTANCES', 'TESTCASE_TAGS', 'OPENSHIFT_USERS']:
                    value = value.replace(' ', '')
                else:
                    value = value.strip()
                if value != '':
                    if param in ['INSTANCE_COUNT', 'JOB_COUNT']:
                        try:
                            setattr(self.config, param.lower(), int(value))
                        except ValueError:
                            print 'Invalid parameter: INSTANCE_COUNT or JOB_COUNT. They must be numbers'
                            return False
                    else:
                        setattr(self.config, param.lower(), value)
                else:
                    setattr(self.config, param.lower(), None)
        return True

    def preprocess(self):
        if not self.strip_params():
            return False
        if self.config.tcms_user == None or self.config.tcms_password == None:
            print 'TCMS_USER and TCMS_PASSWORD are needed'
            return False
        if self.config.reset_testrun not in ['true', 'false']:
            print 'RESET_TESTRUN can only be one of "true" and "false"'
            return False
        if self.config.shutdown_instance not in ['true', 'false']:
            print 'SHUTDOWN_INSTANCE can only be one of "true" and "false"'
            return False
        # Check if it's possible to get/generate openshift users
        if self.config.openshift_users == None:
            if self.config.openshift_user_prototype == None:
                self.config.openshift_user_prototype = "openshift" + self.get_build_uuid(6) + "@redhat.com:redhat"
                print 'Generated random OPENSHIFT_USER_PROTOTYPE: %s' % (self.config.openshift_user_prototype)
        # fork ami test. Get ami_id and testcase_tags from remote
        if self.config.instances == None and self.config.ami_id == None and self.config.testrun_id == None and self.config.testcase_tags == None:
            try:
                (self.config.ami_id, self.config.testcase_tags) = self.get_ami_tags()
            except TypeError:
                print 'Error: Failed to get AMI_ID and TESTCASE_TAGS from remote.'
                sys.exit(0)
        # Check if it's possible to get/create test run with current parameters
        if self.config.testrun_id == None:
            if self.config.testcase_tags == None:
                print "Please specify TESTCASE_TAGS or provide TESTRUN_ID"
                return False
        # Check if it's possible to get/create instances with current parameters
        if self.config.instances == None:
            if self.config.ami_id == None:
                print 'Please specify AMI_ID or provide existing INSTANCES'
                return False
        # Check if it's possible to get/calculate instance count with current parameters
        if self.config.instances == None:
            if self.config.instance_count == None:
                if self.config.testcase_tags == None:
                    print 'Error: Please provide INSTANCE_COUNT or TESTCASE_TAGS(INSTANCE_COUNT can be calculated using TESTCASE_TAGS)'
                    return False
                else:
                    self.config.instance_count = self.get_instance_count(self.config.testcase_tags)
        else:
            self.config.instance_count = len(self.config.instances.splitlines())
        # Check if it's possible to get/calculate job count with current parameters
        if self.config.openshift_users != None:
            self.config.job_count = len(self.config.openshift_users.splitlines())
        if self.config.job_count == None:
            if self.config.testcase_tags == None:
                print 'Error: Please provide JOB_COUNT or TESTCASE_TAGS(JOB_COUNT can be calculated using TESTCASE_TAGS)'
                return False
            else:
                self.config.job_count = self.get_job_count(self.config.testcase_tags)
        # Get user emails
        self.openshift_user_dict = self.get_users(self.config.job_count)
        if self.openshift_user_dict == None:
            print 'Failed to get user emails. Please check'
            return False
        # Check if INSTANCE_COUNT is less than/equal to JOB_COUNT
        if self.config.instance_count > self.config.job_count:
            print 'Error: INSTANCE_COUNT is larger than JOB_COUNT, which may cause waste of instances.'
            return False
        return True

    def create_testrun(self, testrun_tag, testcase_tags):
        cmd = "python bin/create_test_run.py -t '%s' -g '%s'" % (testrun_tag, testcase_tags)
        (ret, output) = commands.getstatusoutput(cmd)
        print output
        if ret == 0:
            match = re.search(r'(?<=test_run_id=)\w+$', output, re.M)
            if match != None:
                return match.group(0)
        return None

    def reset_testrun(self, testrun_id, *states):
        cmd = 'python bin/reset_testrun.py %s %s' % (testrun_id, ' '.join(states))
        (ret, output) = commands.getstatusoutput(cmd)
        if ret != 0:
            print output
        return ret

    def trigger_job(self, **args):
        url = 'http://ciqe.englab.nay.redhat.com/job/%s/buildWithParameters?token=openshift&delay=0sec&%s' % (self.config.sub_job_name, '&'.join(['%s=%s' % (key,value) for (key,value) in args.items()]))
        #url = 'http://ciqe.englab.nay.redhat.com/job/%s/buildWithParamters?token=openshift' % (self.config.sub_job_name)
        #json = '{"parameter": [%s]}' % (', '.join(['{"name":"%s","value":"%s"}' % (key,value) for (key,value) in args.items()]))
        cmd = "curl -s -k --user 'test:redhat' '%s'" % (url)
        #cmd = "curl -X POST -s -k --user 'test:redhat' '%s' --data-urlencode json='%s'" % (url, json)
        (ret, output) = commands.getstatusoutput(cmd)
        if ret != 0:
            print output
        return ret

    def check_instance(self, ip, retry=2, timeout=20):
        cmd = "ssh -t -t -i %s -o StrictHostKeyChecking=no -o ConnectTimeout=%d root@%s \"ls\"" % (PreTestingJob.KEY_PATH, timeout, ip)
        for i in range(retry):
            (ret, output) = commands.getstatusoutput(cmd)
            if ret == 0:
                return True
        return False

    def check_existing_instances(self, retry=2, timeout=20):
        cursor = self.db.instances.find()
        for instance in cursor:
            print 'Checking instance: %s' % (instance['ip'])
            if instance['ip'] in ("int.openshift.redhat.com", "stg.openshift.redhat.com"):
                print 'No need to check stage or INT server'
            elif self.check_instance(instance['ip'], retry=2, timeout=20):
                print 'Instance %s is Active' % (instance['ip'])
            else:
                print 'Failed to ssh connect instance: %s. Remove it from MongoDB.' % (instance['ip'])
                try:
                    self.db.instances.remove(instance['_id'], safe=True)
                except OperationFailure, e:
                    print 'Warning: failed to remove inactive instance %s(%s) from MongoDB.\n%s' % (instance['tag'], instance['ip'], e)

    def use_instance(self, build_uuid, tag, ip, value=1):
        cursor = self.db.instances.find({'tag':tag, 'ip':ip})
        if cursor.count() == 1:
            instance = cursor[0]
            if build_uuid in instance['users']:
                print 'instance %s(%s) is already being used by user: %s' % (tag, ip, build_uuid)
                return True
            self.db.instances.update({'_id':ObjectId(instance['_id'])}, {'$inc' : {'user_count' : value}})
            self.db.instances.update({'_id':ObjectId(instance['_id'])}, {'$push' : {'users' : build_uuid}})
            return True
        elif cursor.count() <= 0:
            print 'No such instance found: %s(%s)' % (tag, ip)
            return False
        else:
            print 'Multiple instances found: %s(%s). Please check.' % (tag, ip)
            return False

    def create_instance(self, tag, ami_id):
        cmd = "python bin/create_instance.py -n '%s' -m '%s'" % (tag, ami_id)
        (ret, output) = commands.getstatusoutput(cmd)
        if ret == 0:
            match = re.search(r'(?<=instance_ip=)[\w.]+$', output, re.M)
            if match != None:
                ip = match.group(0)
                return ip
        else:
            print output
        return None

    def add_instance(self, tag, ip):
        cursor = self.db.instances.find({'tag':tag, 'ip':ip})
        if cursor.count() > 0:
            print 'Instance %s(%s) is already in MongoDB' % (tag, ip)
            return True
        try:
            self.db.instances.insert({'tag' : tag, 'ip' : ip, 'user_count' : 0, 'users' : []}, safe=True)
        except OperationFailure, e:
            print 'Error: Failed to add instance to mongodb\n', e
            return False
        return True

    def start(self):
        # To run a test, we need a test run, several instances, and trigger sub jenkins job several times. There're 3 situations:
        # If instances aren't provides, we need to create new instances using AMI_ID and INSTANCE_TAG(optional).
        # If testrun_id isn't provided, we need to create a new test run using TESTCASE_TAGS and TESTRUN_TAG(optional).
        # If instances, testrun_id, ami_id, and testcase_tags are not provided, we need to get AMI_ID and TESTCASE_TAGS from remote.
        # Generate report
        self.report = {}
        self.report['6. Shutdown Instance'] = self.config.shutdown_instance
        self.report['2. TCMS User'] = self.config.tcms_user
        if self.config.testrun_id == None:
            # Get testrun_tag
            if self.config.testrun_tag == None:
                self.config.testrun_tag = self.get_testrun_tag(self.config.testcase_tags, self.config.ami_id)
            # Create test run using testcase_tags
            self.config.testrun_id = self.create_testrun(self.config.testrun_tag, self.config.testcase_tags)
            if self.config.testrun_id == None:
                print 'Error: Unable to create test run.'
                sys.exit(2)
        else:
            # If existing TESTRUN_ID is provided
            if self.config.reset_testrun == 'true':
                if self.reset_testrun(self.config.testrun_id, 'FAILED', 'ERROR', 'RUNNING') == 0:
                    print 'Test run %s has been reset' % (self.config.testrun_id)
                else:
                    print 'Failed to reset testrun: %s' % (self.config.testrun_id)
                    sys.exit(3)
        # Add test run to report
        self.report['1. Test Run'] = 'https://tcms.engineering.redhat.com/run/%s/' % (self.config.testrun_id)
        # Add users to report
        self.report['3. OpenShift Users'] = []
        for user,passwd in self.openshift_user_dict.items():
            self.report['3. OpenShift Users'].append({'Login':user, 'Password':passwd})
        # Create instances or get existing instances
        instance_list = []
        if self.config.instances == None:
            # self.config.ami_id can't possibly be None because it should be either provided or gotten from remote.
            # Get instance_tag
            if self.config.instance_tag == None:
                self.config.instance_tag = self.get_instance_tag(self.config.ami_id)
            # Create instances using ami_id
            for i in range(self.config.instance_count):
                instance_tag = '%s_%s' % (self.config.instance_tag, self.get_build_uuid(6))
                ip = self.create_instance(instance_tag, self.config.ami_id)
                if ip == None:
                    print 'Failed to create instance: %s(ami id: %s, ip: %s)' % (instance_tag, self.config.ami_id, ip)
                    sys.exit(3)
                if not self.add_instance(instance_tag, ip):
                    print 'Warning: Failed to add instance to MongoDB: %s(ami id: %s, ip: %s)' % (instance_tag, self.config.ami_id, ip)
                instance_list.append((instance_tag, ip))
            self.config.instances = "\n".join([instance[1] for instance in instance_list])
        else:
            for (i,ip) in enumerate(self.config.instances.splitlines()):
                instance_list.append((ip, ip))
                if not self.add_instance(ip, ip):
                    print 'Failed to add user provided instance(%s) to MongoDB' % (ip)
                    sys.exit(4)
        # Add instance count and job count to report
        self.report['4. Instance Count'] = self.config.instance_count
        self.report['5. Jenkins Build Count'] = self.config.job_count
        self.report['7. Instances'] = []
        # Now we have a test run and several instances. Time to trigger sub jenkins jobs.
        jobs_per_instance = self.config.job_count / self.config.instance_count
        remainder = self.config.job_count % self.config.instance_count
        user_iter = self.openshift_user_dict.iteritems()
        for i in range(self.config.instance_count):
            tmp = jobs_per_instance
            if remainder > 0:
                tmp += 1
                remainder -= 1
            if instance_list[i][0] == instance_list[i][1]:
                print 'Instance: %s' % (instance_list[i][1])
            else:
                print 'Instance: %s(%s)' % (instance_list[i][0], instance_list[i][1])
            # Add instance to report
            if instance_list[i][0] == instance_list[i][1]:
                self.report['7. Instances'].append({'Builds Count':tmp, 'IP':instance_list[i][1], 'Jenkins Builds':[]})
            else:
                self.report['7. Instances'].append({'Builds Count':tmp, 'Name':instance_list[i][0], 'IP':instance_list[i][1], 'Jenkins Builds':[]})
            # Trigger jenkins builds
            for j in range(tmp):
                build_uuid = self.get_build_uuid()
                try:
                    (user_email, user_passwd) = user_iter.next()
                except StopIteration:
                    print 'Strange...accounts should not be less than jobs. Please debug'
                    sys.exit(255)
                if self.config.rhc_version == None:
                    self.config.rhc_version = ''
                ret = self.trigger_job( INSTANCE_TAG=quote(instance_list[i][0]),
                                        INSTANCE_IP=quote(instance_list[i][1]),
                                        TESTRUN_ID=quote(self.config.testrun_id),
                                        OPENSHIFT_user_email=quote(user_email),
                                        OPENSHIFT_user_passwd=quote(user_passwd),
                                        BUILD_UUID=quote(build_uuid),
                                        TESTPLAN_ID=quote(PreTestingJob.TESTPLAN_ID),
                                        SHUTDOWN_INSTANCE=quote(self.config.shutdown_instance),
                                        UPDATE_CLIENT=quote(self.config.update_client),
                                        RHC_VERSION=quote(self.config.rhc_version),
                                        RHC_BRANCH=quote(self.config.rhc_branch),
                                        TCMS_USER=quote(self.config.tcms_user),
                                        TCMS_PASSWORD=quote(self.config.tcms_password),
                                        MONGO_CONN_URL=quote(os.environ['MONGO_CONN_URL']))
                # Add time interval to avoid concurrence problems
                print "Wait for 10 secs to avoid concurrence problems..."
                time.sleep(10)
                if ret != 0:
                    print 'Error: Failed to trigger sub jenkins jobs'
                    sys.exit(6)
                if not self.use_instance(build_uuid, instance_list[i][0], instance_list[i][1]):
                    print 'Error: Failed to add the user_count of instance %s(%s)' % (instance_list[i][0], instance_list[i][1])
                    sys.exit(7)
                # Add jenkins build to report
                self.report['7. Instances'][i]['Jenkins Builds'].append({'Build UUID':build_uuid, 'OpenShift User':{'Login':user_email, 'Password':user_passwd}})
        print '\n\nReport:'
        print yaml.dump(self.report, indent=8)
        sys.exit(0)


class UnitTest(PreTestingJob):
    def __init__(self):
        super(UnitTest, self).__init__()

    def create_testrun(self, testrun_tag, testcase_tags):
        random.seed()
        return str(random.randint(0, 9999999))

    def create_instance(self, instance_tag, ami_id):
        if not ami_id or not instance_tag:
            print 'Failed to create instance'
            return None
        random.seed()
        return '.'.join([str(random.randint(1, 255)) for i in range(4)])

    def get_ami_tags(self):
        return ('devenv_2061', 'acceptance,smoke')    

    def reset_testrun(self, testrun_id, *states):
        print 'Testrun: %s has been reset' % (testrun_id)
        return 0

    def trigger_job(self, **args):
        print 'trigger job'
        return 0

if __name__ == '__main__':
    job = PreTestingJob()
    job.start()
