#!/usr/bin/env python

import os
import common
import OSConf
import rhtest
import time
import re
import proc
import signal
import pexpect


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.app_name = common.getRandomString(10)
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = "jbossas"

        self.databases = {
            'postgresql': {'check':'psql --version',
                           'cmd': 'echo "*:PORT:DATABASE:USERNAME:PASSWORD">$HOME/.pgpass;chmod 0600 $HOME/.pgpass;echo "\d" | psql -w -h HOSTNAME --port PORT -U USERNAME DATABASE'},
            'mongodb': {'check':'mongo --version',
                        'cmd': 'echo "" | mongo HOSTNAME:PORT/DATABASE -u USERNAME -p PASSWORD'},
            'mysql': {'check':'mysql --version',
                      'cmd': 'echo "SHOW TABLES;" | mysql -h HOSTNAME -P PORT -u USERNAME -pPASSWORD DATABASE'}}

        self.info("Supported DB engines: %s"%self.databases.keys())
        try:
            self.db_variant = self.config.tcms_arguments['db_cartridge']
        except:
            self.db_variant = 'mysql'
            self.info("Not defined 'db_cartridge' in TCMS arguments, using `%s` as default." % (self.db_variant))
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        if self.scalable:
            self.scalable = True

        if not self.databases.has_key(self.db_variant):
            raise rhtest.TestIncompleteError("Unsupported db cartridge. Use: %s" % self.databases.keys())
        print "-"*80
        self.info("Variant: %s"%self.app_type)
        self.info("DB Cartridge variant: %s"%self.db_variant)
        self.info("SCALABLE : %s"%self.scalable)
        print "-"*80
        cmd = self.databases[self.db_variant]['check'] #check for dependencies
        if (common.command_get_status(cmd) != 0):
            raise rhtest.TestIncompleteError("The '%s' client program is missing needed for accessing remote server. Install particular RPM in order to proceed with this testcase."%cmd)
        common.env_setup()

class RhcPortForward(OpenShiftTest):
    def test_port_forward(self, new_syntax=True):
        self.services = []
        result = True
        db_info = OSConf.get_embed_info(self.app_name, common.cartridge_types[self.db_variant])
        self.info("db_cartridge info: %s"%db_info)
        if new_syntax:
            cmd = "rhc port-forward %s -l %s -p '%s' %s" % (self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        else:
            cmd = "rhc port-forward -a %s -l %s -p '%s' %s" % (self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, common.RHTEST_RHC_CLIENT_OPTIONS)
        self.debug("Command: %s" % (cmd))
        proc = pexpect.spawn(cmd)
        # expand the timeout from 20 to 40 to avoid slow response
        proc.expect('--', timeout=40)
        line = proc.readline()
        while 'terminate' not in line:
            line = proc.readline()
            self.info(line)
            #match = re.search(r'(\w+)\s+[\d.:]+\s+=>\s+((\d+\.){3}\d+):(\d+)', line)
            #match = re.search(r'(\w+)\s+((\d+\.){3}\d+):(\d+)+\s+=>\s+[\w\.\:\-\d]+', line)
            match = re.search(r'(\w+)\s+((\d+\.){3}\d+):(\d+)+\s+=>[\w\s\.\:]*', line)
            self.info(line)
            print match
            if match:
                serv = match.group(1)
                host = match.group(2)
                port = match.group(4)
                print serv
                self.services.append(serv)
                ret = self.check_port(serv, host, port)
                if ret != 0:
                    result = False
                    self.debug("Check failed: %s %s:%s" % (serv, host, port))
            #line = proc.readline()
        self.info(self.services)
        proc.terminate()
        return result

    def check_port(self, serv, host, port):
        self.info("Checking service %s at %s:%s" % (serv, host, port))
        if serv in ('haproxy'):
            return common.grep_web_page("%s:%s" % (host, port), "(openshift)|(Statistics Report)")
        elif serv in ['mysqld', 'mysql']:
            db_info = OSConf.get_embed_info(self.app_name, common.cartridge_types['mysql'])
            cmd = "echo 'show databases;' | mysql -h %s -P %s -u %s -p%s %s" % (host, port, db_info['username'], db_info['password'], self.app_name)
        elif serv in ['postgres', 'postgresql']:
            db_info = OSConf.get_embed_info(self.app_name, common.cartridge_types['postgresql'])
            cmd = 'echo "%s:%s:%s:%s:%s" > $HOME/.pgpass ; chmod 0600 $HOME/.pgpass ; echo "\d" | psql -w -h %s --port %s -U %s %s' % (host, port, self.app_name, db_info['username'], db_info['password'], host, port, db_info['username'], self.app_name)
        elif serv in ['mongod', 'mongodb']:
            db_info = OSConf.get_embed_info(self.app_name, common.cartridge_types['mongodb'])
            cmd = 'echo "show collections;" | mongo -u %s -p %s %s:%s/%s' % (db_info['username'], db_info['password'], host, port, self.app_name)
        elif port == '8080':
            return common.grep_web_page("%s:%s" % (host, port), "(openshift)|(Statistics Report)")
        else:
            self.info("No check for service: %s %s:%s" % (serv, host, port))
            return 0
        return common.command_get_status(cmd)

    def test_method(self):
        self.info("[US1491][rhc-client] Run 'rhc port-forward' with various arguments")
        self.debug("1. Create an app")
        status = common.create_app(self.app_name,
                                       common.app_types[self.app_type],
                                       self.config.OPENSHIFT_user_email,
                                       self.config.OPENSHIFT_user_passwd,
                                       False, "./", self.scalable)
        self.assert_equal(status, 0, "%s application should be created."%self.app_type)

        if self.scalable:
            self.info("Embed all the database cartridges to the scalable app")
            ret = common.embed(self.app_name,
                           'add-%s'%common.cartridge_types['mysql'],
                           self.config.OPENSHIFT_user_email,
                           self.config.OPENSHIFT_user_passwd)
            self.assert_equal(ret, 0, "Embeding of mysql should pass.")

            ret = common.embed(self.app_name,
                           'add-%s'%common.cartridge_types['postgresql'],
                           self.config.OPENSHIFT_user_email,
                           self.config.OPENSHIFT_user_passwd)
            self.assert_equal(ret, 0, "Embeding of postgresql should pass.")

            #ret = common.embed(self.app_name,
            #               'add-%s'%common.cartridge_types['mongodb'],
            #               self.config.OPENSHIFT_user_email,
            #               self.config.OPENSHIFT_user_passwd)
            #self.assert_equal(ret, 0, "Embeding of mongodb should pass.")

            ret = common.scale_up(self.app_name)
            self.assert_equal(ret, 0, "The app should be scaled up")
        else:
            self.info("Embed %s to the app" % (self.db_variant))
            ret = common.embed(self.app_name,
                           'add-%s'%common.cartridge_types[self.db_variant],
                           self.config.OPENSHIFT_user_email,
                           self.config.OPENSHIFT_user_passwd)
            self.assert_equal(ret, 0, "Embeding of %s should pass."%self.db_variant)

        ret = self.test_port_forward(True)
        self.assert_equal(ret, True, "Failed to forward ports(new rhc syntax)")
        ret = self.test_port_forward(False)
        self.assert_equal(ret, True, "Failed to forward ports(old rhc syntax)")
        if self.scalable:
            #self.assert_true(('mysql' in self.services), "mysql ports of scalable apps should be forwarded")
            #self.assert_true(('postgresql' in self.services), "postgresql ports of scalable apps should be forwarded")
            #self.assert_true(('mongodb' in self.services), "mongo ports of scalable apps should be forwarded")
            self.assert_true(('mysql' in self.services) or ('mysqld' in self.services), "mysql ports of scalable apps should be forwarded")
            self.assert_true(('postgresql' in self.services) or ('postgres' in self.services), "postgresql ports of scalable apps should be forwarded")
            #self.assert_true(('mongodb' in self.services) or ('mongod' in self.services), "mongo ports of scalable apps should be forwarded")

        else:
            if self.db_variant == 'mysql':
                db_service = 'mysqld'
            elif self.db_variant == 'postgresql':
                db_service = 'postgres'
            elif self.db_variant == 'mongodb':
                db_service = 'mongod'
            else:
                self.info("Invalid database")
            self.assert_true((db_service in self.services) or (self.db_variant in self.services), "%s ports haven't been forwarded" % (self.db_variant))

        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(RhcPortForward)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
