"""
Michal Zimen mzimen@redhat.com
Helper file for reading the broker's main DB (mongo)
"""
import os
import json
import helper
import re
import cPickle as pickle


class BrokerDB(object):
    COLLECTIONS = ("district", "usages", "user", "template")
    EXPIRATION_PERIOD = 0.240  #15minutes?
    def __init__(self, dbs="openshift_broker_dev", collections=[], force_cache=False):
        self.dbs=dbs
        self.collections={}
        self.force_cache = force_cache
        if not collections:
            collections = self.COLLECTIONS
        else:
            if type(collections) == str:
                collections = [collections]
        for c in collections:
            if not self._valid_cache(c) or force_cache:
                self.collections[c] = self._init_collection(c)
                self._do_cache_collection(c)
            else:
                #use cached data
                try:
                    self.collections[c] = self._get_cache_collection(c)
                except:
                    del(self.collections[c])
                    self.collections[c] = self._init_collection(c)
                    self._do_cache_collection(c)


    def _valid_cache(self, cname):
        return helper.valid_cache(self._get_cache_file(cname), 
                                  self.EXPIRATION_PERIOD)

    def _get_cache_file(self, cname):
        return "/tmp/brokerdb.%s.dump"%cname

    def _do_cache_collection(self, cname):
        oldumask = os.umask(0000)
        filename=self._get_cache_file(cname)
        try:
            f = open(filename, 'wb')
            pickle.dump(self.collections[cname], f)
            f.close()
            os.umask(oldumask)
        except Exception as e:
            if os.path.exists(filename):
                os.unlink(filename)
            print "ERROR: Unable to store cache %s"%str(e)

    def _get_cache_collection(self, cname):
        filename=self._get_cache_file(cname)
        try:
            f = open(filename, 'rb')
            dump = pickle.load(f)
            f.close()
            if dump is None:
                raise Exception("None found in cache!")
            return dump
        except Exception as e:
            print "ERROR: Unable to load from cache %s"%str(e)
            #let's delete corrupetd file if exists
            if os.path.exists(filename):
                os.unlink(filename)
            return None

    def get_collection(self, collection):
        if (self.collections.has_key(collection)):
            return self.collections[collection]
        else:
            self.collections[collection] = self._init_collection(collection)
            self._do_cache_collection(collection)
            return self.collections[collection]

    def _init_collection(self, collection, filter=None):
        if filter:
            cmd = "db.%s.find(%s)"%(collection, filter)
        else:
            cmd = "db.%s.find()"%collection
        return self._mongo(cmd)

    def _mongo(self, cmd):
        """
        Returns json format of MONGO's output
        """
        cmd = """mongo --quiet %s <<EOF
    printjson(%s.toArray());
EOF"""%(self.dbs, cmd)
        (status, output) = helper.remote_batch(cmd)
        if status != 0:
            raise Exception("Unable to get mongo dump from broker.")
        #workaround because of bug in paramiko - slow transfer of large files

        try:
            output = output.strip()
            output = output.strip('bye')
            output = re.sub('^bye$','', output, re.MULTILINE)
            output = re.sub(r'ISODate\(("[^"]+")\)',r'\1', output)
            output = output.strip()
            return json.loads(output)
        except Exception as e:
            print "ERROR: %s"%str(e)
            print "OUTPUT:\n%s",output
            return None

    def get_nodes_per_district(self, district):
        l = {}
        for district in self.collection['district']:
            name = district['name']
            l[name] = self.collections['district']['server_identities']
        return l


