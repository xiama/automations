#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Aug 2, 2012
"""

import rhtest
import common
import re


class ManPageTest(rhtest.Test):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.testcase_summary = '[rhc-client]man page and help check for all client commands'

    def finalize(self):
        pass

    def log_message(self, pattern, status):
        self.info("Pattern '%s'... %s" % ( pattern, status ))

    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput("man %s | col -b" % self.command)
        if ret_code == 0:
            return ret_output
        else:
            return None

    def test_method(self):
        # Gettng the man page
        output = self.get_output()

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
            

#class RhcTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'rhc'
#        self.pattern_list = [
#            'alias', 'cartridge', 'domain', 'app', 'sshkey', 
#            'port-forward', 'setup', 'server', 'snapshot', 'tail', 'threaddump'
#        ]

class RhcHelpTest(ManPageTest):

    def initialize(self):
        self.command = 'rhc'
        self.pattern_list = [
            'alias', 'cartridge', 'domain', 'app', 'sshkey', 
            'port-forward', 'setup', 'server', 'snapshot', 'tail', 'threaddump'
        ]


    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput('rhc help')
        return ret_output


#class RhcDomainTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'rhc-domain'
#        self.pattern_list = [
#            'create', 'update', 'show', 'status', 'delete',
#            '-l', '--rhlogin', '-p', '--password',  '-d', '--debug', '-h', '--help',
#            '--config', '--timeout',  '--noprompt', '-v', '--version'
#        ]

class RhcDomainHelpTest(ManPageTest):

    def initialize(self):
        self.command = 'rhc domain'
        self.pattern_list = [
            'create', 'update', 'show', 'status', 'delete',
            '-l', '--rhlogin', '-p', '--password',  '-d', '--debug', '-h', '--help',
            '--config', '--timeout',  '--noprompt', '-v', '--version'
        ]
        
    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput('rhc help domain')
        return ret_output

#class RhcAppTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'rhc-app'
#        self.pattern_list = [
#            'reload', 'tidy', 'git-clone', 'delete', 
#            'create', 'start', 'stop', 'restart',
#            'force-stop', 'status', 'show', '-l', '--rhlogin',
#            '-p', '--password', '-d', '--debug',
#            '--noprompt', '--config', '-h', '--help',
#            '-v', '--version', '--timeout'
#            ]

class RhcAppHelpTest(ManPageTest):

    def initialize(self):
        self.command = 'rhc app'
        self.pattern_list = [
            'reload', 'tidy', 'git-clone', 'delete', 
            'create', 'start', 'stop', 'restart',
            'force-stop', 'status', 'show', '-l', '--rhlogin',
            '-p', '--password', '-d', '--debug',
            '--noprompt', '--config', '-h', '--help',
            '-v', '--version', '--timeout'
            ]

    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput('rhc help app')
        return ret_output


#class RhcSshkeyTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'rhc-sshkey'
#        self.pattern_list = [
#            'list', 'add', 'show', 'remove', '-l', '-p',  '-d', '-h','-v',
#            '--config', '--timeout', '--noprompt'
#        ]

class RhcSshkeyHelpTest(ManPageTest):

    def initialize(self):
        self.command = 'rhc sshkey'
        self.pattern_list = [
            'list', 'add', 'show', 'remove', '-l', '-p',  '-d', '-h','-v',
            '--config', '--timeout', '--noprompt'
        ]
        
    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput('rhc help sshkey')
        return ret_output


#class RhcPortForwardTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'rhc port-forward'
#        self.pattern_list = [
#            '-l', '--rhlogin', '-p', '--password', '-a', '--app', '-d', 
#            '-h', '--help', '--config', '--timeout'
#        ]


class RhcPortForwardHelpTest(ManPageTest):
    def initialize(self):
        self.command = 'rhc port-forward'
        self.pattern_list = [
            '-l', '--rhlogin', '-p', '--password', '-a', '--app', '-d', 
            '-h', '--help', '--config', '--timeout'
        ]
        
    def get_output(self):
        ( ret_code, ret_output ) = common.command_getstatusoutput('rhc help port-forward')
        return ret_output


#class ExpressConfTest(ManPageTest):
#
#    def initialize(self):
#        self.command = 'express.conf'
#        self.pattern_list = [
#            'Search order', 'libra_server', 'ssh_key_file', 'debug', 'timeout', 'default_rhlogin'
#        ]

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    #suite.add_test(RhcTest)
    suite.add_test(RhcHelpTest)
    #suite.add_test(RhcDomainTest)
    suite.add_test(RhcDomainHelpTest)
    #suite.add_test(RhcAppTest)
    suite.add_test(RhcAppHelpTest)
    #suite.add_test(RhcSshkeyTest)
    suite.add_test(RhcSshkeyHelpTest)
    #suite.add_test(RhcPortForwardTest)
    suite.add_test(RhcPortForwardHelpTest)
    #suite.add_test(ExpressConfTest)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
