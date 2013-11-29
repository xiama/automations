"""
Linqing Lu
lilu@redhat.com
Jan 12, 2012

[US1350][Runtime][rhc-node]The mongoDB interactive shell
https://tcms.engineering.redhat.com/case/126302/
"""

import sys
import os

import rhtest
import testcase
import common
import OSConf
import pexpect

class OpenShiftTest(rhtest.Test):
    def initialize(self):
        self.summary = "[US1350][Runtime][rhc-node]The mongoDB interactive shell"
        self.app_name = 'php'
        self.app_type = common.app_types[self.app_name]
        self.steps_list = []
        common.env_setup()

    def finalize(self):
        os.system("rm -rf %s"%(self.app_name))

class MongodbViaRhcsh(OpenShiftTest):
    def test_method(self):
        self.steps_list.append(testcase.TestCaseStep(
            "Create an %s app: %s" % (self.app_type, self.app_name),
            common.create_app,
            function_parameters = [self.app_name, self.app_type, 
                    self.config.OPENSHIFT_user_email,
                    self.config.OPENSHIFT_user_passwd,
                    'False'],
            expect_description = "App should be created successfully",
            expect_return = 0))

        self.steps_list.append(testcase.TestCaseStep(
            "embed mongodb into app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "add-%s"%common.cartridge_types["mongodb"]],
            expect_return = 0))

        '''
        self.steps_list.append(testcase.TestCaseStep(
            "embed rockmongo into app %s"% self.app_name,
            common.embed,
            function_parameters = [self.app_name, "add-rockmongo-1.1"],
            expect_return = 0)
        '''

        self.steps_list.append(testcase.TestCaseStep(
            "run mongo shell via rhcsh with pexpect",
            self.mongo_shell_test,
            expect_return = 0))


        case = testcase.TestCase(self.summary, self.steps_list)
        try:
            case.run()
        except testcase.TestCaseStepFail:
            return self.failed("%s failed" % self.__class__.__name__)

        if case.testcase_status == 'PASSED':
            return self.passed("%s passed" % self.__class__.__name__)
        if case.testcase_status == 'FAILED':
            return self.failed("%s failed" % self.__class__.__name__)

    def mongo_shell_test(self):
        app_url = OSConf.get_app_url(self.app_name)
        ssh_url = OSConf.get_ssh_url(self.app_name)
        db_info = OSConf.get_embed_info(self.app_name, 'mongodb-2.2')
        p = pexpect.spawn('ssh %s'% ssh_url)
        p.logfile = sys.stdout
#    index = p.expect([OSConf.get_app_url(self.app_name), pexpect.EOF, pexpect.TIMEOUT])

        p.expect('Welcome to OpenShift shell')
        p.expect(app_url)
        p.sendline('help')
        p.expect('Help menu:')
        p.expect('interactive MongoDB shell')
        p.sendline('mongo')
        p.expect('MongoDB shell version:')
        p.expect('connecting to:')
        p.expect('>', timeout=20)
        #p.sendcontrol('c')
        p.sendline('exit')
        p.expect('bye', timeout=20)
        p.expect('.*')
        db_path = '%s:%s/%s'% (db_info['url'], db_info['port'], db_info['database'])
        self.info("db_path=%s"%db_path)
        p.sendline('mongo %s'% db_path)
        p.expect('MongoDB shell version:', timeout=30)
        p.expect('connecting to: %s'% db_path, timeout=30)
        p.expect('>')
        p.sendline('db.auth("%s","%s")'% (db_info['username'], db_info['password']))
        p.expect('1')
        p.expect('>')
        p.sendline('help')
        p.expect('help on db methods')
        p.expect('quit the mongo shell')
        p.expect('>')
        p.sendline('db')
        p.expect(db_info['database'])
        p.sendline('show collections')
        p.expect('system.users')
        p.sendline('db.createCollection("test")')
        p.expect('{ "ok" : 1 }')
        p.sendline('show collections')
        p.expect('test')
        p.sendline('db.test.save({"name":"lilu"})')
        p.sendline('db.test.find()')
        p.expect('"name" : "lilu"')
        p.sendline('person=db.test.findOne({ name : "lilu" } )')
        p.expect('"name" : "lilu"')
        p.sendline('person.name="newlilu"')
        p.expect('newlilu')
        p.sendline('db.test.save(person)')
        p.sendline('db.test.find()')
        p.expect('"name" : "newlilu"')
        p.sendline('db.test.save({"name":"lilu"})')
        p.sendline('db.test.find()')
        p.expect('"name" : "newlilu"')
        p.expect('"name" : "lilu"')
        p.sendline('db.test.remove({"name":"newlilu"})')
        p.sendline('db.test.find()')
        index = p.expect(['"name" : "newlilu"', '"name" : "lilu"', pexpect.TIMEOUT])
        if index == 0 or index == 2:
            return 1
        p.sendline('exit')
        p.expect('bye')
        p.sendline('exit')
        p.expect('Connection to %s closed.'% app_url)
        return 0

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(MongodbViaRhcsh)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
