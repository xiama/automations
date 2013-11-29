#!/usr/bin/env python
import os
import sys
import commands
import subprocess
import re
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


class PostTestingJob(object):
    KEY_PATH = os.path.join(SCRIPT_PATH, '..', 'etc', 'libra.pem')
    IP_ADDR = '184.73.182.48'
    TESTPLAN_ID = '4962'

    def __init__(self):
        # Change key file permission
        os.system("chmod 600 %s" % (PostTestingJob.KEY_PATH))
        # Setup environment variables
        os.environ['RHTEST_HOME'] = os.path.abspath(os.curdir)
        os.environ['PATH'] = os.path.expandvars(os.path.expanduser('${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PATH'))
        os.environ['PYTHONPATH'] = os.path.expandvars(os.path.expanduser('${RHTEST_HOME}/bin:${RHTEST_HOME}/lib:${RHTEST_HOME}/lib/supports:${RHTEST_HOME}/testmodules:$PYTHONPATH'))
        # Init kerberos
        cmd = 'cd bin/ && ./kinit.sh'
        if os.system(cmd) != 0:
            print 'Failed to init kerberos. Please check your TCMS_USER and TCMS_PASSWORD'
            sys.exit(255)
        # Init parameters
        self.init_params()
        if not self.preprocess():
            sys.exit(255)
        # Connect to local mongodb
        mongo_url = os.environ['MONGO_CONN_URL']
        try:
            self.conn = pymongo.Connection('mongodb://%s' % (mongo_url))
        except ConnectionFailure:
            print 'Error: Failed to connect to MongoDB at %s:%s. Please check your system configurations.' % (mongo_url)
            sys.exit(255)
        self.db = self.conn['devenv']
        # Remove inactive instances
        self.check_existing_instances()

    def __del__(self):
        # Disconnect from MongoDB
        if hasattr(self, 'conn'):
            self.conn.close()

    def init_params(self):
        self.config = DotDict()
        self.param_list = ['INSTANCE_TAG', 'INSTANCE_IP', 'BUILD_UUID', 'SHUTDOWN_INSTANCE', 'TCMS_USER', 'TCMS_PASSWORD']
        for param in self.param_list:
            setattr(self.config, param.lower(), os.environ.get(param))

    def strip_params(self):
        for parameter in self.param_list:
            value = getattr(self.config, parameter.lower())
            if value != None:
                value = value.strip()
                if value != '':
                    setattr(self.config, parameter.lower(), value)
                else:
                    setattr(self.config, parameter.lower(), None)
        return True

    def preprocess(self):
        if not self.strip_params():
            print 'Failed to strip parameters'
            return False
        if self.config.shutdown_instance == 'false':
            return True
        elif self.config.shutdown_instance == 'true':
            if self.config.instance_ip and self.config.instance_tag and self.config.build_uuid:
                return True
            else:
                print 'INSTANCE_IP, INSTANCE_TAG and BUILD_UUID are needed to shutdown instance'
                return False
        else:
            print 'SHUTDOWN_INSTANCE can only be one of true/false'
            return False

    def remove_instance(self, tag, ip):
        cursor = self.db.instances.find({'tag':tag, 'ip':ip})
        if cursor.count() <= 0:
            print 'Instance %s(%s) is not in MongoDB' % (tag, ip)
            return False
        elif cursor.count() > 1:
            print 'Error: Multiple instances with the same tag and ip found. Please debug.'
            return False
        instance = cursor[0]
        if instance['user_count'] > 0:
            print 'Instance %s(%s) is still being used by %d builds: %s' % (tag, ip, instance['user_count'], instance['users'])
            print 'No need to shutdown it'
            return True
        elif instance['user_count'] < 0:
            print 'Error: The user_count of instance is less than 0. Something wrong happened.'
            return False
        # Shutdown instance
        print 'Going to shutdown instance: %s(%s)' % (tag, ip)
        ret = 1
        for i in range(3):
            ret = self.shutdown_instance_by_ip(ip)
            if ret == 0:
                break
        if tag != ip and ret != 0:
            for i in range(3):
                ret = self.shutdown_instance_by_tag(tag)
                if ret == 0:
                    break
        if ret != 0:
            print 'Failed to shutdown instance %s(%s)' % (tag, ip)
            return False
        # Remove instance from MongoDB
        try:
            self.db.instances.remove({'tag' : tag, 'ip' : ip, 'user_count' : 0}, safe=True)
        except OperationFailure, e:
            print 'Error: Failed to remove instance from mongodb\n', e
            return False
        return True

    def disuse_instance(self, build_uuid, tag, ip, value=-1):
        cursor = self.db.instances.find({'tag':tag, 'ip':ip, 'users':build_uuid})
        if cursor.count() == 1:
            instance = cursor[0]
            if build_uuid not in instance['users']:
                print 'instance %s(%s) is not being used by user: %s' % (tag, ip, build_uuid)
                return True
            self.db.instances.update({'_id':ObjectId(instance['_id'])}, {'$inc' : {'user_count' : value}})
            self.db.instances.update({'_id':ObjectId(instance['_id'])}, {'$pull' : {'users' : build_uuid}})
            return True
        elif cursor.count() <= 0:
            print 'Error: No such instance found: %s(%s)' % (tag, ip)
            return False
        else:
            print 'Error: Multiple instances found: %s(%s). Please check.' % (tag, ip)
            return False

    def shutdown_instance_by_tag(self, tag):
        if tag in ['int.openshift.redhat.com', 'stg.openshift.redhat.com']:
            print "We can't shutdown stage or int instance"
            return 0
        cmd = "python bin/shutdown_instance.py -n '%s'" % (tag)
        return subprocess.call(cmd, shell=True)

    def shutdown_instance_by_ip(self, ip, timeout=10):
        if ip in ['int.openshift.redhat.com', 'stg.openshift.redhat.com']:
            print "We can't shutdown stage or int instance"
            return 0
        cmd = "ssh -t -t -i %s -o StrictHostKeyChecking=no -o ConnectTimeout=%d -t root@%s \"shutdown -h now\"" % (PostTestingJob.KEY_PATH, timeout, ip)
        return subprocess.call(cmd, shell=True)

    def check_instance(self, ip, retry=2, timeout=20):
        cmd = "ssh -t -t -i %s -o StrictHostKeyChecking=no -o ConnectTimeout=%d root@%s \"ls\"" % (PostTestingJob.KEY_PATH, timeout, ip)
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

    def start(self):
        if self.config.shutdown_instance == 'true':
            if not self.disuse_instance(self.config.build_uuid, self.config.instance_tag, self.config.instance_ip):
                sys.exit(1)
            if not self.remove_instance(self.config.instance_tag, self.config.instance_ip):
                sys.exit(2)
        sys.exit(0)


class UnitTest(PostTestingJob):
    def __init__(self):
        super(UnitTest, self).__init__()

    def shutdown_instance_by_tag(self, tag):
        print 'Instance(tag: %s) has been shutdown' % (tag)
        return 0

    def shutdown_instance_by_ip(self, ip):
        print 'Instance(ip: %s) has been shutdown' % (ip)
        return 0


if __name__ == '__main__':
    job = PostTestingJob()
    job.start()
