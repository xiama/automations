#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-11-09

[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support
https://tcms.engineering.redhat.com/case/138803/
"""
import os
import common
import OSConf
import rhtest
import time
import pexpect

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `python` as default")
            self.test_variant = 'jbosseap'
        try:
            self.scalable = self.config.tcms_arguments['scalable']
        except:
            self.scalable = False
        self.summary = "[US926][Runtime][rhc-cartridge]MySQL Admin(phpmyadmin) support"
        self.app_name = "envvar" + common.getRandomString(6)
        self.app_type = common.app_types[self.test_variant]
        self.cart = common.type_to_cart(self.app_type)
        self.git_repo = "./%s" % (self.app_name)

        common.env_setup()

    def finalize(self):
        pass


class NamespacedEnvVars(OpenShiftTest):
    def get_env_list(self, main_cart, *cart_list):
        env_list = { "GLOBAL" : [   ("removed", "OPENSHIFT_GEAR_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_GEAR_DIR"),
                                    ("removed", "OPENSHIFT_GEAR_TYPE"),
                                    ("removed", "OPENSHIFT_APP_DIR"),
                                    ("removed", "OPENSHIFT_APP_TYPE"),
                                    ("unchanged", "OPENSHIFT_GEAR_NAME"),
                                    ("translated", "OPENSHIFT_RUNTIME_DIR", ""),
                                    ("translated", "OPENSHIFT_LOG_DIR", "OPENSHIFT_%s_LOG_DIR" % (main_cart)),
                                    ("translated", "OPENSHIFT_RUN_DIR", ""),
                                    ("new", "OPENSHIFT_%s_IP" % (main_cart)),
                                    ("special", "OPENSHIFT_%s_PORT" % (main_cart)),
                                    ("unchanged", "OPENSHIFT_APP_DNS"),
                                    ("unchanged", "OPENSHIFT_APP_NAME"),
                                    ("unchanged", "OPENSHIFT_APP_UUID"),
                                    ("unchanged", "OPENSHIFT_DATA_DIR"),
                                    ("unchanged", "OPENSHIFT_GEAR_DNS"),
                                    ("unchanged", "OPENSHIFT_GEAR_UUID"),
                                    ("unchanged", "OPENSHIFT_HOMEDIR"),
                                    ("unchanged", "OPENSHIFT_REPO_DIR"),
                                    ("unchanged", "OPENSHIFT_TMP_DIR")],
                    "JBOSSAS":[     ("translated", "OPENSHIFT_JBOSS_CLUSTER", "OPENSHIFT_JBOSSAS_CLUSTER"),
                                    ("translated", "OPENSHIFT_JBOSS_CLUSTER_PORT", "OPENSHIFT_JBOSSAS_CLUSTER_PORT"),
                                    ("translated", "OPENSHIFT_JBOSS_CLUSTER_PROXY_PORT", "OPENSHIFT_JBOSSAS_CLUSTER_PROXY_PORT"),
                                    ("translated", "OPENSHIFT_JBOSS_MESSAGING_PORT", "OPENSHIFT_JBOSSAS_MESSAGING_PORT"),
                                    ("translated", "OPENSHIFT_JBOSS_MESSAGING_THROUGHPUT_PORT", "OPENSHIFT_JBOSSAS_MESSAGING_THROUGHPUT_PORT"),
                                    ("translated", "OPENSHIFT_JBOSS_REMOTING_PORT", "OPENSHIFT_JBOSSAS_REMOTING_PORT")],
                    "JENKINS":[     ("unchanged", "JENKINS_USERNAME"),
                                    ("unchanged", "JENKINS_PASSWORD"),
                                    ("unchanged", "JENKINS_URL")],
                    "JENKINSCLIENT":[("unchanged", "JENKINS_USERNAME"),
                                    ("unchanged", "JENKINS_PASSWORD"),
                                    ("unchanged", "JENKINS_URL"),
                                    ("new", "OPENSHIFT_JENKINS_CLIENT_DIR"),
                                    ("new", "OPENSHIFT_JENKINS_CLIENT_IDENT")],
                    "HAPROXY":[     ("new", "OPENSHIFT_HAPROXY_INTERNAL_IP"),
                                    ("new", "OPENSHIFT_HAPROXY_STATUS_IP")],
                    "MYSQL" : [     ("removed", "OPENSHIFT_DB_CTL_ONGEAR_SCRIPT"),
                                    ("removed", "OPENSHIFT_DB_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_DB_MYSQL_51_DUMP"),
                                    ("removed", "OPENSHIFT_DB_MYSQL_51_DUMP_CLEANUP"),
                                    ("removed", "OPENSHIFT_DB_MYSQL_51_PROFILE"),
                                    ("removed", "OPENSHIFT_DB_MYSQL_51_RESTORE"),
                                    ("removed", "OPENSHIFT_DB_TYPE"),
                                    ("translated", "OPENSHIFT_DB_HOST", "OPENSHIFT_MYSQL_DB_HOST"),
                                    ("translated", "OPENSHIFT_DB_PORT", "OPENSHIFT_MYSQL_DB_PORT"),
                                    ("translated", "OPENSHIFT_DB_USERNAME", "OPENSHIFT_MYSQL_DB_USERNAME"),
                                    ("translated", "OPENSHIFT_DB_PASSWORD", "OPENSHIFT_MYSQL_DB_PASSWORD"),
                                    ("translated", "OPENSHIFT_DB_SOCKET", "OPENSHIFT_MYSQL_DB_SOCKET"),
                                    ("translated", "OPENSHIFT_DB_URL", "OPENSHIFT_MYSQL_DB_URL"),
                                    ("new", "OPENSHIFT_MYSQL_DB_LOG_DIR")],
                    "POSTGRESQL":[  ("removed", "OPENSHIFT_DB_POSTGRESQL_84_DUMP"),
                                    ("removed", "OPENSHIFT_DB_POSTGRESQL_84_DUMP_CLEANUP"),
                                    ("removed", "OPENSHIFT_DB_POSTGRESQL_84_EMBEDDED_TYPE"),
                                    ("removed", "OPENSHIFT_DB_POSTGRESQL_84_RESTORE"),
                                    ("removed", "OPENSHIFT_DB_TYPE"),
                                    ("translated", "OPENSHIFT_DB_HOST", "OPENSHIFT_POSTGRESQL_DB_HOST"),
                                    ("translated", "OPENSHIFT_DB_PORT", "OPENSHIFT_POSTGRESQL_DB_PORT"),
                                    ("translated", "OPENSHIFT_DB_USERNAME", "OPENSHIFT_POSTGRESQL_DB_USERNAME"),
                                    ("translated", "OPENSHIFT_DB_PASSWORD", "OPENSHIFT_POSTGRESQL_DB_PASSWORD"),
                                    ("translated", "OPENSHIFT_DB_SOCKET", "OPENSHIFT_POSTGRESQL_DB_SOCKET"),
                                    ("translated", "OPENSHIFT_DB_URL", "OPENSHIFT_POSTGRESQL_DB_URL"),
                                    ("new", "OPENSHIFT_POSTGRESQL_DB_LOG_DIR")],
                    "MONGODB":[     ("removed", "OPENSHIFT_NOSQL_DB_CTL_ONGEAR_SCRIPT"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_MONGODB_22_DUMP"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_MONGODB_22_DUMP_CLEANUP"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_MONGODB_22_EMBEDDED_TYPE"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_MONGODB_22_RESTORE"),
                                    ("removed", "OPENSHIFT_NOSQL_DB_TYPE"),
                                    ("translated", "OPENSHIFT_NOSQL_DB_HOST", "OPENSHIFT_MONGODB_DB_HOST"),
                                    ("translated", "OPENSHIFT_NOSQL_DB_PASSWORD", "OPENSHIFT_MONGODB_DB_PASSWORD"),
                                    ("translated", "OPENSHIFT_NOSQL_DB_PORT", "OPENSHIFT_MONGODB_DB_PORT"),
                                    ("translated", "OPENSHIFT_NOSQL_DB_URL", "OPENSHIFT_MONGODB_DB_URL"),
                                    ("translated", "OPENSHIFT_NOSQL_DB_USERNAME", "OPENSHIFT_MONGODB_DB_USERNAME"),
                                    ("new", "OPENSHIFT_MONGODB_DB_LOG_DIR")],
                    "PHPMYADMIN":[  ("new", "OPENSHIFT_PHPMYADMIN_IP"),
                                    ("new", "OPENSHIFT_PHPMYADMIN_PORT"),
                                    ("new", "OPENSHIFT_PHPMYADMIN_LOG_DIR"),
                                    ("removed", "OPENSHIFT_PHPMYADMIN_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_PHPMYADMIN_GEAR_DIR")],
                    "ROCKMONGO":[   ("new", "OPENSHIFT_ROCKMONGO_LOG_DIR"),
                                    ("new", "OPENSHIFT_ROCKMONGO_IP"),
                                    ("new", "OPENSHIFT_ROCKMONGO_PORT"),
                                    ("removed", "OPENSHIFT_ROCKMONGO_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_ROCKMONGO_GEAR_DIR")],
                    "10GENMMSAGENT":[("removed", "OPENSHIFT_10GEN_MMS_AGENT_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_10GEN_MMS_AGENT_GEAR_DIR"),
                                    ("new", "OPENSHIFT_10GENMMSAGENT_IDENT"),
                                    ("new", "OPENSHIFT_10GENMMSAGENT_DIR")],
                    "CRON":     [   ("removed", "OPENSHIFT_BATCH_CRON_14_EMBEDDED_TYPE"),
                                    ("removed", "OPENSHIFT_BATCH_CTL_SCRIPT"),
                                    ("removed", "OPENSHIFT_BATCH_TYPE")],
        }
        expected_list = []
        unexpected_list = []
        special = ['OPENSHIFT_JBOSSAS_PORT','OPENSHIFT_JBOSSEAP_PORT','OPENSHIFT_JBOSSEWS_PORT']
        cart_list = list(cart_list)
        cart_list.append("GLOBAL")
        for cart in cart_list:
            for i in env_list.get(cart, []):
                if i[0] == "unchanged":
                    expected_list.append(i[1])
                elif i[0] == "translated":
                    expected_list.append(i[2])
                    unexpected_list.append(i[1])
                elif i[0] == "removed":
                    unexpected_list.append(i[1])
                elif i[0] == "new":
                    expected_list.append(i[1])
                elif i[0] == "special":
                    if i[1] not in special:
                        expected_list.append(i[1])
        expected_list = list(set(expected_list))
        unexpected_list = list(set(unexpected_list))
        return (expected_list, unexpected_list)

    def check_env_var(self, output, expected_list, unexpected_list):
        missing_list = []
        existing_list = []
        for i in expected_list:
            if output.find(i) == -1:
                missing_list.append(i)
        for i in unexpected_list:
            if output.find(i) != -1:
                existing_list.append(i)
        return (missing_list, existing_list)

    def check_jenkins_app(self, app_name):
        ssh_url = OSConf.get_ssh_url(app_name)
        print "ssh url: %s" % (ssh_url)
        self.ssh_proc = pexpect.spawn("ssh -o StrictHostKeyChecking=no -o ConnectTimeout=20 %s 'env'" % (ssh_url))
        output = self.ssh_proc.read()
        print "Output: %s" % (output)
        self.ssh_proc.close()
        expected_list, unexpected_list = self.get_env_list(common.type_to_cart(common.app_types["jenkins"]), common.type_to_cart(common.app_types["jenkins"]))
        print "Cartridge: %s" % (common.app_types["jenkins"])
        print "Expected env var list: %s" % (','.join(expected_list))
        print "Unexpected env var list: %s" % (','.join(unexpected_list))
        missing_list, existing_list = self.check_env_var(output, expected_list, unexpected_list)
        flag = True
        if missing_list != []:
            print "The following env vars are missing:"
            print ', '.join(missing_list)
            flag = False
        if existing_list != []:
            print "The following env vars,which should be removed, still exist:"
            print ', '.join(existing_list)
            flag = False
        return flag

    def check_app(self, app_name, *cart_list):
        app_url = OSConf.get_app_url(app_name)
        common.stop_app(app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        common.start_app(app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        url_postfix_dict = {    "jbossas"   :   "/universal.jsp?group=env",
                                "php"       :   "/universal.php?group=env",
                                "ruby"      :   "/env",
                                "python"    :   "/env",
                                "perl"      :   "/universal.pl?group=env",
                                "nodejs"    :   "/env",
                            }
        url_postfix_dict["jbosseap"] = url_postfix_dict["jbossas"]
        url_postfix_dict["jbossews"] = url_postfix_dict["jbossas"]
        url_postfix_dict["jbossews-2.0"] = url_postfix_dict["jbossas"]
        url_postfix_dict["python-2.7"] = url_postfix_dict["python"]
        url_postfix_dict["python-3.3"] = url_postfix_dict["python"]
        url_postfix_dict["zend"] = url_postfix_dict["php"]
        url_postfix_dict["ruby-1.9"] = url_postfix_dict["ruby"]
        # Wait for the app to start
        common.grep_web_page(app_url + url_postfix_dict[self.test_variant], "OPENSHIFT_APP_DNS")
        content = common.fetch_page(app_url + url_postfix_dict[self.test_variant])
        expected_list, unexpected_list = self.get_env_list(self.cart, *cart_list)
        print "Cartridge list: %s" % (','.join(cart_list))
        print "Expected env var list: %s" % (','.join(expected_list))
        print "Unexpected env var list: %s" % (','.join(unexpected_list))
        missing_list, existing_list = self.check_env_var(content, expected_list, unexpected_list)
        flag = True
        if missing_list != []:
            print "The following env vars are missing:"
            print ', '.join(missing_list)
            flag = False
        if existing_list != []:
            print "The following env vars,which should be removed, still exist:"
            print ', '.join(existing_list)
            flag = False
        return flag

    def test_method(self):
        # Create app
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App creation failed")

        src_path_dict = {   "jbossas"   :   "%s/app_template/universal/jbossas/universal.jsp" % (WORK_DIR),
                            "php"       :   "%s/app_template/universal/php/universal.php" % (WORK_DIR),
                            "ruby"      :   "%s/app_template/universal/ruby/config.ru" % (WORK_DIR),
                            "python"    :   "%s/app_template/universal/python/application" % (WORK_DIR),
                            "python-2.7"  :   "%s/app_template/universal/python-2.7/application" % (WORK_DIR),
                            "perl"      :   "%s/app_template/universal/perl/universal.pl" % (WORK_DIR),
                            "nodejs"    :   "%s/app_template/universal/nodejs/server.js" % (WORK_DIR),
                        }
        src_path_dict["jbosseap"] = src_path_dict["jbossas"]
        src_path_dict["jbossews"] = src_path_dict["jbossas"]
        src_path_dict["jbossews-2.0"] = src_path_dict["jbossas"]
        src_path_dict["ruby-1.9"] = src_path_dict["ruby"]
        src_path_dict["zend"] = src_path_dict["php"]
        src_path_dict["python-3.3"] = src_path_dict["python"]
        dst_path_dict = {   "jbossas"   :   "%s/src/main/webapp/" % (self.app_name),
                            "php"       :   "%s/php/" % (self.app_name),
                            "ruby"      :   "%s/" % (self.app_name),
                            "python"    :   "%s/wsgi/" % (self.app_name),
                            "perl"      :   "%s/perl/" % (self.app_name),
                            "nodejs"    :   "%s/" % (self.app_name),
                        }
        dst_path_dict["jbosseap"] = dst_path_dict["jbossas"]
        dst_path_dict["jbossews"] = dst_path_dict["jbossas"]
        dst_path_dict["jbossews-2.0"] = dst_path_dict["jbossas"]
        dst_path_dict["ruby-1.9"] = dst_path_dict["ruby"]
        dst_path_dict["zend"] = dst_path_dict["php"]
        dst_path_dict["python-2.7"] = dst_path_dict["python"]
        dst_path_dict["python-3.3"] = dst_path_dict["python"]
        ret, output = common.command_getstatusoutput('cp -f %s %s && cd %s && git add . && git commit -amt && git push' % (src_path_dict[self.test_variant], dst_path_dict[self.test_variant], self.app_name))
        self.assert_equal(ret, 0, output)

        ret = self.check_app(self.app_name, self.cart)
        self.assert_equal(ret, True, "Env var check failed")

        # Add mysql to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mysql"])
        self.assert_equal(ret, 0, "Failed to add mysql to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mysql"]))
        self.assert_equal(ret, True, "mysql env var check failed")

        # Add phpmyadmin to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["phpmyadmin"])
        self.assert_equal(ret, 0, "Failed to add phpmyadmin to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mysql"]), common.type_to_cart(common.cartridge_types["phpmyadmin"]))
        self.assert_equal(ret, True, "phpmyadmin env var check failed")

        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["phpmyadmin"])
        self.assert_equal(ret, 0, "Failed to remove phpmyadmin to app")

        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["mysql"])
        self.assert_equal(ret, 0, "Failed to remove mysql to app")

        # Add postgresql to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["postgresql"])
        self.assert_equal(ret, 0, "Failed to add postgresql to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["postgresql"]))
        self.assert_equal(ret, True, "postgresql env var check failed")

        ret = common.embed(self.app_name, "remove-" + common.cartridge_types["postgresql"])
        self.assert_equal(ret, 0, "Failed to remove postgresql to app")

        # Add mongodb to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mongodb"])
        self.assert_equal(ret, 0, "Failed to add mongodb to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mongodb"]))
        self.assert_equal(ret, True, "mongodb env var check failed")

        # Add rockmongo to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["rockmongo"])
        self.assert_equal(ret, 0, "Failed to add mongodb to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mongodb"]), common.type_to_cart(common.cartridge_types["rockmongo"]))
        self.assert_equal(ret, True, "rockmongo env var check failed")

        # Copy settings.py to app repo
        ret, output = common.command_getstatusoutput('mkdir -p %s/.openshift/mms/ && cp -f %s/app_template/settings.py %s/.openshift/mms && cd %s && git add . && git commit -amt && git push' % (self.app_name, WORK_DIR, self.app_name, self.app_name))
        self.assert_equal(ret, 0, output)

        # Add 10gen-mms-agent to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["10gen"])
        self.assert_equal(ret, 0, "Failed to add 10gen-mms-agent to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mongodb"]), common.type_to_cart(common.cartridge_types["rockmongo"]), common.type_to_cart(common.cartridge_types["10gen"]))
        self.assert_equal(ret, True, "10gen-mms-agent env var check failed")

        # Add cron to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["cron"])
        self.assert_equal(ret, 0, "Failed to add mongodb to app")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mongodb"]), common.type_to_cart(common.cartridge_types["rockmongo"]), common.type_to_cart(common.cartridge_types["cron"]))
        self.assert_equal(ret, True, "cron env var check failed")

        # Create a jenkins app
        ret = common.create_app("server", common.app_types["jenkins"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "App creation failed")

        # Check the jenkins server app
        ret = self.check_jenkins_app("server")
        self.assert_equal(ret, True, "jenkins server app env var check failed")

        # Add jenkins client to app
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["jenkins"])
        if ret != 0:
            ret = common.embed(self.app_name, "add-" + common.cartridge_types["jenkins"])
        self.assert_equal(ret, 0, "Failed to add mongodb to app")

        # Git push the app
        ret = common.trigger_jenkins_build(self.git_repo)
        self.assert_equal(ret, True, "Failed to trigger jenkins build")

        ret = self.check_app(self.app_name, self.cart, common.type_to_cart(common.cartridge_types["mongodb"]), common.type_to_cart(common.cartridge_types["rockmongo"]), common.type_to_cart(common.cartridge_types["cron"]), common.type_to_cart(common.cartridge_types["jenkins"]))
        self.assert_equal(ret, True, "cron env var check failed")

        return self.passed("%s passed" % self.__class__.__name__)



class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NamespacedEnvVars)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
