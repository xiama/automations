#
#  File name: move_app_between_nodes_within_district.py
#  Date:      2012/08/31 16:17
#  Author:    mzimen@redhat.com
#

import common
import rhtest
import OSConf
import re


class OpenShiftTest(rhtest.Test):
    ITEST = ["DEV"]

    def initialize(self):
        self.info("[US2102] Move scalable application with postgresql embeded between nodes within one district")
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        try:
            self.db_variant = self.config.tcms_arguments['db_variant']
        except:
            self.db_variant = 'postgresql'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False

        self.info("VARIANT: %s"%self.test_variant)
        self.info("DB VARIANT: %s"%self.db_variant)
        self.info("SCALABLE: %s"%self.scalable)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types[self.test_variant]
        self.cart_type = common.cartridge_types[self.db_variant]
        self.district_name=common.getRandomString(10)
        self.district_created=False
        common.env_setup()


    def finalize(self):
        pass


class MoveAppBetweenNodesWithinDistrict(OpenShiftTest):
    def create_district(self):
        if self.district_created:
            return
        self.info("Create a district")
        (ret, output) = common.create_district(self.district_name)
        self.assert_equal(ret, 0, "Unable to create a district")
        self.district_created=True

    def test_method(self):
        msetup = common.setup_multi_node_env(self.district_name)

        self.assert_true((len(msetup['nodes'])>=2), "Missing multi node environment!")
        self.info("Found %s connected nodes"%len(msetup['nodes']))

        ret = common.set_max_gears(self.user_email, common.DEV_MAX_GEARS)
        #self.assert_equal(ret, 0, "Unable set max_gears")

        if self.scalable:
            ret = common.create_scalable_app(self.app_name, self.app_type, clone_repo=False)
        else:
            ret = common.create_app(self.app_name, self.app_type, clone_repo=False)
        self.assert_equal(ret, 0, "Unable to create the app")

        ret = common.embed(self.app_name, 'add-%s'%self.cart_type)
        self.assert_equal(ret, 0, "Unable to embed the app by %s"%self.db_variant)

        #app_uuid=OSConf.get_app_uuid(self.app_name)
        app_url=OSConf.get_app_url(self.app_name) #node
        (gear_groups, gear_count) = self.config.rest_api.get_gears(self.app_name)

        gear_to_move = None
        for gear_group in gear_groups:
            for cart in gear_group['cartridges']:
                if cart['name'].find('%s' % self.db_variant) != -1:
                    gear_to_move = gear_group['gears'][0]['id']
        self.assert_true((gear_to_move is not None), "Unable to find gear of %s"%self.db_variant)
        self.info("Gear of %s"%gear_to_move)
        district_of_moved_gear = common.get_district_of_gear(gear_to_move)
        node_of_moved_gear = common.get_node_of_gear(gear_to_move)
        self.assert_true((node_of_moved_gear is not None), "Unable to find server_identity per gear[%s]"%gear_to_move)
        self.info("Finding available nodes for possible move gear[%s] within district[%s]"%(gear_to_move, district_of_moved_gear))
        node_to_move = None

        for n in common.get_nodes_of_district(district_of_moved_gear):
            if n == node_of_moved_gear:
                continue
            else:
                node_to_move = n
                break

        app_url_private_ip = common.get_private_ip(app_url)
        self.info("app[%s] -> node[%s]"%(app_url,app_url_private_ip))
        self.info("Node to move: %s"%node_to_move)
        if node_to_move:
            ret = common.move_gear_between_nodes(gear_to_move, node_to_move)
            self.assert_equal(ret, 0, "Unable to move gear.")
        else:
            return self.abort("Unable to find a free node to move in withing district[%s]."%district_of_moved_gear)

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MoveAppBetweenNodesWithinDistrict)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of move_app_between_nodes_within_district.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
