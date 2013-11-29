#
#  File name: US2105.py
#  Date:      2012/10/03 10:04
#  Author:    mzimen@redhat.com
#

import common
import rhtest


class OpenShiftTest(rhtest.Test):
    #ITEST = ["INT", "STG"]

    def initialize(self):
        self.info("US2105")
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        if common.app_types.has_key(self.test_variant):
            self.app_type = self.test_variant
            self.cart_variant = None
        else:
            self.app_type = 'php'
            self.cart_variant = self.test_variant
        self.info("VARIANT: %s"%self.test_variant)

        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(10)
        common.env_setup()


    def finalize(self):
        pass


class US2105(OpenShiftTest):
    def test_method(self):

        self.add_step("Create an app", 
                common.create_app,
                function_parameters=[self.app_name,
                        common.app_types[self.app_type],
                        self.user_email, 
                        self.user_passwd, 
                        False],
                        expect_return=0)

        if self.cart_variant is not None:
            if common.cartridge_deps.has_key(self.cart_variant):
                self.add_step("Embed a dep cartridge", 
                        common.embed,
                        function_parameters=[self.app_name,
                                "add-%s"%common.cartridge_types[common.cartridge_deps[self.cart_variant]], 
                                self.user_email, 
                                self.user_passwd],
                        expect_return=0)

            self.add_step("Embed a cartridge", 
                    common.embed,
                    function_parameters=[self.app_name,
                            "add-%s"%common.cartridge_types[self.cart_variant], 
                            self.user_email, 
                            self.user_passwd],
                    expect_return=0)

        self.add_step("Verify ENV", self.verify_env, expect_return = 0)
        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


    def verify_zend(self):
        present = ['OPENSHIFT_ZEND_IP',
                   'OPENSHIFT_ZEND_PORT',
                   'OPENSHIFT_ZEND_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_haproxy(self):
        present = ['OPENSHIFT_HAPROXY_INTERNAL_IP',
                   'OPENSHIFT_HAPROXY_STATUS_IP',
                   'OPENSHIFT_HAPROXY_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_metrics(self):
        present = ['OPENSHIFT_METRICS_IP',
                   'OPENSHIFT_METRICS_PORT',
                   'OPENSHIFT_METRICS_LOG_DIR']
        self.assert_match(present, self.env_output)
        removed = ['OPENSHIFT_METRICS_CTL_SCRIPT',
                   'OPENSHIFT_METRICS_GEAR_DIR']
        self.assert_not_match(removed, self.env_output)


    def verify_diy(self):
        present = ['OPENSHIFT_DIY_IP',
                   'OPENSHIFT_DIY_PORT']
        self.assert_match(present, self.env_output)


    def verify_jbossas(self):
        removed = ['OPENSHIFT_JBOSS_']
        self.assert_not_match(removed, self.env_output)

        present = ['OPENSHIFT_JBOSSAS_IP',
                   'OPENSHIFT_JBOSSAS_PORT',
                   'OPENSHIFT_JBOSSAS_CLUSTER',
                   'OPENSHIFT_JBOSSAS_CLUSTER_PORT',
                   'OPENSHIFT_JBOSSAS_CLUSTER_PROXY_PORT',
                   'OPENSHIFT_JBOSSAS_CLUSTER_REMOTING'
                   'OPENSHIFT_JBOSSAS_MESSAGING_PORT',
                   'OPENSHIFT_JBOSSAS_MESSAGING_THROUGHPUT_PORT',
                   'OPENSHIFT_JBOSSAS_REMOTING_PORT',
                   'OPENSHIFT_JBOSSAS_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_perl(self):
        present = ['OPENSHIFT_PERL_LOG_DIR']
        self.assert_match(present, self.env_output)

    def verify_mysql(self):
        removed = ['OPENSHIFT_DB_']
        self.assert_not_match(removed, self.env_output)

        present = ['OPENSHIFT_MYSQL_DB_GEAR_DNS',
                   'OPENSHIFT_MYSQL_DB_GEAR_UUID',
                   'OPENSHIFT_MYSQL_DB_HOST',
                   'OPENSHIFT_MYSQL_DB_USERNAME',
                   'OPENSHIFT_MYSQL_DB_PASSWORD',
                   'OPENSHIFT_MYSQL_DB_PORT',
                   'OPENSHIFT_MYSQL_DB_SOCKET',
                   'OPENSHIFT_MYSQL_DB_URL',
                   'OPENSHIFT_MYDQL_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_jbosseap(self):
        present = ['OPENSHIFT_JBOSSEAP_IP',
                   'OPENSHIFT_JBOSSEAP_PORT',
                   'OPENSHIFT_JBOSSEAP_CLUSTER',
                   'OPENSHIFT_JBOSSEAP_MESSAGING_THROUGHPUT_PORT',
                   'OPENSHIFT_JBOSSEAP_LOG_DIR',
                   'OPENSHIFT_JBOSSEAP_CLUSTER_PORT',
                   'OPENSHIFT_JBOSSEAP_CLUSTER_PROXY_PORT',
                   'OPENSHIFT_JBOSSEAP_CLUSTER_REMOTING',
                   'OPENSHIFT_JBOSSEAP_MESSAGING_PORT',
                   'OPENSHIFT_JBOSSEAP_REMOTING_PORT']
        self.assert_match(present, self.env_output)
        removed = ['OPENSHIFT_JBOSS_']
        self.assert_not_match(removed, self.env_output)


    def verify_jenkins(self):
        present = ['JENKINS_CLIENT_DIR',
                   'JENKINS_DNS_NAME',
                   'JENKINS_HOME',
                   'JENKINS_INSTANCE_DIR',
                   'OPENSHIFT_JENKINS_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_mongodb(self):
        removed = ['OPENSHIFT_NOSQL']
        self.assert_not_match(removed, self.env_output)
        present = ['OPENSHIFT_MONGODB_DB_GEAR_DNS',
                   'OPENSHIFT_MONGODB_DB_GEAR_UUID',
                   'OPENSHIFT_MONGODB_DB_HOST',
                   'OPENSHIFT_MONGODB_DB_PASSWORD',
                   'OPENSHIFT_MONGODB_DB_PORT',
                   'OPENSHIFT_MONGODB_SOCKET',
                   'OPENSHIFT_MONGODB_DB_URL',
                   'OPENSHIFT_MONGODB_DB_USERNAME']
        self.assert_match(present, self.env_output)


    def verify_rockmongo(self):
        present = ['OPENSHIFT_ROCKMONGO_IP',
                   'OPENSHIFT_ROCKMONGO_PORT',
                   'OPENSHIFT_ROCKMONGO_LOG_DIR']
        self.assert_match(present, self.env_output)
        removed = ['OPENSHIFT_ROCKMONGO_CTL_SCRIPT',
                   'OPENSHIFT_ROCKMONGO_GEAR_DIR']
        self.assert_not_match(removed, self.env_output)


    def verify_ruby(self):
        present = ['OPENSHIFT_RUBY_IP',
                   'OPENSHIFT_RUBY_PORT',
                   'OPENSHIFT_RUBY_LOG_DIR']
        self.assert_match(present, self.env_output)

    def verify_phpmyadmin(self):
        removed = ['OPENSHIFT_PHPMYADMIN_CTL_SCRIPT',
                   'OPENSHIFT_PHPMYADMIN_GEAR_DIR']
        self.assert_not_match(removed, self.env_output)

        present = ['OPENSHIFT_PHPMYADMIN_IP',
                   'OPENSHIFT_PHPMYADMIN_LOG_DIR',
                   'OPENSHIFT_PHPMYADMIN_PORT']
        self.assert_match(present, self.env_output)


    def verify_cron(self):
        removed = ['OPENSHIFT_BATCH_CRON_14_EMBEDDED_TYPE',
                   'OPENSHIFT_BATCH_CTL_SCRIPT', 
                   'OPENSHIFT_BATCH_TYPE']
        self.assert_not_match(removed, self.env_output)
        present = ['OPENSHIFT_CRON_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_python(self):
        present = ['OPENSHIFT_PYTHON_IP',
                   'OPENSHIFT_PYTHON_LOG_DIR',
                   'OPENSHIFT_PYTHON_PORT']
        self.assert_match(present, self.env_output)


    def verify_php(self):
        present = ['OPENSHIFT_PHP_IP',
                   'OPENSHIFT_PHP_LOG_DIR',
                   'OPENSHIFT_PHP_PORT']
        self.assert_match(present, self.env_output)


    def verify_nodejs(self):
        present = ['OPENSHIFT_NODEJS_IP',
                   'OPENSHIFT_NODEJS_PORT',
                   'OPENSHIFT_NODEJS_LOG_DIR']
        self.assert_match(present, self.env_output)


    def verify_postgresql(self):
        removed = ['OPENSHIFT_DB_']
        self.assert_not_match(removed, self.env_output)


    def verify_10gen(self):
        self.assert_match('', self.env_output)


    def verify_env(self):
        (status, self.env_output) = common.run_remote_cmd(self.app_name, "env|grep OPENSHIFT", quiet=True)
        self.assert_equal(status, 0, "Unable to get env from given app")
        eval("self.verify_%s()"%self.test_variant.split('-')[0])
        #common variables to be present/removed
        present = ['OPENSHIFT_APP_DNS',
                   'OPENSHIFT_APP_NAME',
                   'OPENSHIFT_APP_UUID',
                   'OPENSHIFT_DATA_DIR',
                   'OPENSHIFT_GEAR_NAME',
                   'OPENSHIFT_GEAR_DNS',
                   'OPENSHIFT_GEAR_UUID',
                   'OPENSHIFT_HOMEDIR',
                   'OPENSHIFT_INTERNAL_IP',
                   'OPENSHIFT_INTERNAL_PORT',
                   'OPENSHIFT_REPO_DIR',
                   'OPENSHIFT_TMP_DIR']
        self.assert_match(present, self.env_output)
        removed = ['OPENSHIFT_APP_DIR',
                   'OPENSHIFT_APP_TYPE',
                   'OPENSHIFT_GEAR_CTL_SCRIPT',
                   'OPENSHIFT_GEAR_DIR',
                   'OPENSHIFT_GEAR_TYPE',
                   'OPENSHIFT_RUNTIME_DIR',
                   'OPENSHIFT_PROXY_PORT',
                   'OPENSHIFT_RUN_DIR',
                   'OPENSHIFT_LOG_DIR']
        self.assert_not_match(removed, self.env_output)
        return 0


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(US2105)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of US2105.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
