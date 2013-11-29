#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Sept 19, 2012
"""
import rhtest
import common
import database
#### test specific import


class OpenShiftTest(rhtest.Test):

    def initialize(self):
        self.summary = "[US2755] MongoDB 2.2"
	self.application_name = common.getRandomString()
	self.application_type = common.app_types["php"]
        pass

    def record_results(self, resid):
        pass

    def finalize(self):
        pass
    

class MongoDB22Test(OpenShiftTest):
    def test_method(self):
        self.info("=" * 80)
	self.info("Creating a PHP application")
        self.info("=" * 80)
	common.create_app(self.application_name, self.application_type, clone_repo = False)
	
        self.info("=" * 80)
	self.info("Embedding MongoDB cartridge")
        self.info("=" * 80)
	common.embed(self.application_name, "add-" + common.cartridge_types["mongodb"])

        self.info("=" * 80)
	self.info("Checking the version of MongoDB")
        self.info("=" * 80)
	( ret_code, ret_output ) = common.run_remote_cmd(self.application_name, "eval $(cat mongodb-2.2/pid/mongodb.pid  | xargs -I{} ps -p {} -o cmd= | cut -d' ' -f1) --version")
	self.assert_true(ret_output.find("db version v2.2") != -1, "MongoDB version must be in branch 2.2")

	# everything is OK
	return self.passed(self.summary)

	

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MongoDB22Test)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
