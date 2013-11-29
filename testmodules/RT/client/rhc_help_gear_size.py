import common
import rhtest
import sys
import re


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        #self.info("[US2001][Runtime][rhc-node] check help page and man page for the gear sizes")
        self.testcase_summary = "[US2001][Runtime][rhc-node] check help page and man page for the gear sizes"
        common.env_setup()

    def finalize(self):
        pass


class RhcHelpGearSize(OpenShiftTest):
    def log_message(self, pattern, status):
        self.info("Pattern '%s'... %s" % ( pattern, status ))
    
    def test_method(self):
        
        self.command = "rhc app create"
        self.pattern_list = ['-g', '--gear-size', "Geari\s+size\s+controls\s+how\s+much\s+memory\s+and\s+CPU\s+your\s+cartridges\s+can\s+use."]
        
        ( ret_code, output ) = common.command_getstatusoutput('rhc help app create')
        
        # Checking patterns in the output
        missing_patterns = [ ]
        for pattern in self.pattern_list:
            result = "OK"
            match = re.search(pattern, output)
            if not match:
                result = "FAIL"
                missing_patterns.append(pattern)
            self.log_message(pattern, result)

        # Assertion
        self.info('Asserting that the number of missing patterns is 0')
        self.assert_equal(len(missing_patterns), 0)

        # Everythng is OK
        return self.passed(" - ".join([ self.testcase_summary, self.command ]))

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcHelpGearSize)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
