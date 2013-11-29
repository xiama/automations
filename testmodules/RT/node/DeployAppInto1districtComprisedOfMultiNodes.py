#
#  File name: DeployAppInto1districtComprisedOfMultiNodes.py
#  Date:      2012/08/29 11:36
#  Author:    mzimen@redhat.com
#

import common
import rhtest
import OSConf
import brokerdb


class OpenShiftTest(rhtest.Test):
    ITEST = ["DEV"]

    def initialize(self):
        self.info("DeployAppInto1districtComprisedOfMultiNodes")
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        self.info("VARIANT: %s"%self.test_variant)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name1 = common.getRandomString(10)
        self.app_name2 = common.getRandomString(10)
        self.district_name = common.getRandomString(10)
        common.env_setup()


    def finalize(self):
        pass


class DeployAppInto1districtComprisedOfMultiNodes(OpenShiftTest):
    def test_method(self):
        self.info("Creating new district...")
        (ret, output) = common.create_district(self.district_name)
        self.assert_equal(0, ret, "Unable to create district:%s")

        nodes = common.get_nodes()
        pnodes=[]
        for node in nodes:
            pnodes.append(common.get_public_ip_from_private(node))
        self.assert_true((len(nodes)>=2), "There must be at least 2 ndoes...")
        for node in nodes:
            ret = common.add_node2district(self.district_name,node)
            self.assert_equal(0, ret, "Error during adding node into district")
        #Creating 1st app
        self.info("Creating app#1...")
        (ret, status) = self.config.rest_api.app_create(self.app_name1, 
                        common.app_types[self.test_variant])
        self.assert_equal('Created', ret, "Error during creating app#1 - %s"%self.app_name1)
        self.info("Waiting...")
        common.sleep(90)
        self.info("Creating app#2...")
        (ret,status) = self.config.rest_api.app_create(self.app_name2, 
                       common.app_types[self.test_variant])
        self.assert_equal('Created', ret, "Error during creating app#2 - %s"%self.app_name2)
        (gear_group1, gear_count) = self.config.rest_api.get_gears(self.app_name1)
        app1_gear=gear_group1[0]['gears'][0]['id']
        (gear_group2, gear_count) = self.config.rest_api.get_gears(self.app_name2)
        app2_gear=gear_group2[0]['gears'][0]['id']
        gears={}
        print "*"*80
        for node in pnodes:
            gears[node] = common.get_gears_per_node(node)
            if gears[node].has_key(app1_gear):
                print "\tApp1's gear[%s] is deployed on %s"%(app1_gear, node)
                app1_node=node
            if gears[node].has_key(app2_gear):
                print "\tApp2's gear[%s] is deployed on %s"%(app2_gear, node)
                app2_node=node
        print "*"*80
        self.assert_true((app1_node!=app2_node), "App1 should not reside on the same node as App2")
        '''
        db = brokerdb.BrokerDB(collections = ['district'])
        districts = db.get_collection('district')
        print "DISTRICTS: [UUID | NAME | NODES]"
        for district in districts:
            #print district.keys()
            print "\t",district['uuid'], district['name'], district['server_identities']
        print uuid1,uuid2
        '''
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(DeployAppInto1districtComprisedOfMultiNodes)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of DeployAppInto1districtComprisedOfMultiNodes.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
