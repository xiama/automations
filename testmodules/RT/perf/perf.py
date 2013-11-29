#!/usr/bin/env python

"""
"""
import rhtest
import database
import time
import random
# user defined packages
import openshift
import uuid


PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.instance_ip = self.config.instance_info['ip']
        self.rest = openshift.Openshift(host=self.instance_ip)
        self.perf_results = {}
    
    def finalize(self):
        pass
    
    def record_results(self, resid):
        for k, v in self.perf_results.items():
            print "K: %s, V: %s" % (k,v)
            #action = database.get_perf_action_id(k)
            res  = database.PerfResults(TestResultsID=resid, ActionID=k, 
                                        ActionTime=v[0], GearSize=v[1])
            print res.id


class Performance(OpenShiftTest):
    def test_method(self):
        errorCount = 0
        li = self.rest
        #self.info("xxx", 1)
        #perf_results = {}
        # setup a valid domain first
        #print "###########################"
        self.info("Domain performance")
        domain_name = "test%s" % uuid.uuid1().hex[:6]
        action = 'domain_create'
        method_call = getattr(li, action)
        manifest_id = database.get_perf_action_id(action, None)
        status, res = method_call(domain_name)
        self.perf_results[manifest_id] = res

        app_params_dict = self.config.app_params
        app_params = openshift.sortedDict(app_params_dict)
        for cart in self.config.cart_types:
            for action in app_params:
                manifest_id = database.get_perf_action_id(action['name'], cart)
                #perf_results[mainfest_id] = None
                method_call = getattr(li, action['name'])
                k, v = action['params'].items()[0]
                if action['name'] == 'app_create':
                    status, res = method_call(v, cart)
                elif action['name'] == 'app_create_scale':
                    status, res = method_call(v, cart, 'true')
                else:
                    status, res = method_call(v)
                # finally get the gear information
                try:
                    gear_info, gear_size = li.get_gears(v)
                except:
                    gear_size = 1
                self.perf_results[manifest_id] = [res, gear_size]
        #self.info("xx", 1)
        """
        action = 'domain_delete'
        method_call = getattr(li, action)
        manifest_id = database.get_perf_action_id(action, None)
        status, res = method_call(domain_name)
        self.perf_results[manifest_id] = res
         
        """

        if errorCount:
            return self.failed("Performance test failed.")
        else:
            return self.passed("Performance test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(Performance)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
