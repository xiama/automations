#!/usr/bin/env python

import common
import rhtest
import random
import openshift

PASSED = rhtest.PASSED
FAILED = rhtest.FAILED

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("Check black list")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.domain_name = common.get_domain_name()
        self.blacklist = openshift.get_black_list(self.config.rest_api)
        self.app_type = common.app_types["jbossas"]
        #string = "amentra aop apiviz arquillian blacktie boxgrinder byteman cirras cloud cloudforms cygwin davcache dogtag drools ejb3 errai esb fedora freeipa gatein gfs gravel guvnor hibernate hornetq iiop infinispan ironjacamar javassist jbcaa jbcd jboss jbpm jdcom jgroups jmx jopr jrunit jsfunit kosmos liberation makara mass maven metajizer metamatrix mobicents modeshape mugshot netty openshift osgi overlord ovirt penrose picketbox picketlink portletbridge portletswap posse pressgang qumranet railo redhat resteasy rhca rhcds rhce rhcsa rhcss rhct rhcva rhel rhev rhq rhx richfaces riftsaw savara scribble seam shadowman shotoku shrinkwrap snowdrop solidice spacewalk spice steamcannon stormgrind switchyard tattletale teiid tohu torquebox weld wise xnio"
        #self.blacklist = string.split()
        self.test_count = 3
        common.env_setup()

    def finalize(self):
        common.alter_domain(self.domain_name, self.user_email, self.user_passwd)


class BlackList(OpenShiftTest):

    def select(self):
        result = []
        random.seed()
        for i in range(self.test_count):
            rand = int(random.random() * len(self.blacklist))
            result.append(self.blacklist[rand])
        return result

    def test_method(self):
        final_list = self.select()
        for name in final_list:
            self.add_step("Update an existing domain name to one in black list - %s" %(name),
                          "rhc domain update %s %s -l %s -p '%s' %s" %(    self.domain_name,
                                                                        name,
                                                                        self.user_email,
                                                                        self.user_passwd,
                                                                        common.RHTEST_RHC_CLIENT_OPTIONS),
                          expect_return="!0",
                          expect_str=["is not allowed"])

            self.add_step("Try to create app with name - %s"%(name),
                          "rhc app create %s %s -l %s -p '%s' --no-git %s"%(name,
                                                                        self.app_type,
                                                                        self.user_email,
                                                                        self.user_passwd,
                                                                        common.RHTEST_RHC_CLIENT_OPTIONS),
                          expect_return="!0",
                          expect_str=["is not allowed"])

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(BlackList)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
