#!/usr/bin/env python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import rhtest
import common
# user defined packages
from quick_start_test import QuickStartTest

class QuickStartMongoFlask(QuickStartTest):
    
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["python"]
        self.config.application_embedded_cartridges = [ common.cartridge_types['mongodb'] ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Mongo Flask"
        self.config.git_upstream_url = "git://github.com/openshift/openshift-mongo-flask-example.git"
        self.config.page = "ws/parks"
        self.config.page_pattern = "Aztec Ruins National Monument"

    def post_deployment_steps(self):
        common.run_remote_cmd(self.config.application_name, "mongoimport -d parks -c parkpoints --type json --file $OPENSHIFT_REPO_DIR/parkcoord.json  -h $OPENSHIFT_MONGODB_DB_HOST  -u admin -p $OPENSHIFT_MONGODB_DB_PASSWORD")
        

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartMongoFlask)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
