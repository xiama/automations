#!/usr/bin/env python

"""
"""
import rhtest
import tcms_base

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED


class OpenShiftTest(rhtest.Test):

    def initialize(self):
        pass

    def finalize(self):
        pass

class RunTests(OpenShiftTest):
    def test_method(self):
        return self.passed("test passed.")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    if conf.options.TCMS:
        tests = conf.tcms_obj.get_testscripts_by_tag(conf.tcms_tag)
    else:
        # user specified the tag file from a json file
        tests = rhtest.extract_tests_from_json_file(conf.options.json_file)
        #tests, variant_map  = rhtest.extract_tests_from_json_file(conf.options.json_file)
        #conf['testcase_variants_map'] = variant_map
    suite.add_test(RunTests)
    i = 0
    for test, args in tests:
        i += 1
        try:
            klass = rhtest.convert_script_to_cls(test)
            print "KLASS: %s" % klass
            suite.add_test(klass, args)
        except:
            print "Failed to import test '%s'" % test
            pass
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
