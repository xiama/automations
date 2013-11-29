import common
import OSConf
import rhtest
import re


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False
    ITEST = 'DEV'

    def initialize(self):
        self.info("[US1909][BI]Horizontal Scale: Expose/Conceal port hooks")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.domain_name = common.get_domain_name()
        self.key_filename = common.getRandomString(7)
        self.new_keyname = common.getRandomString(7)
        self.app_name = common.getRandomString(10)
        self.app_type = 'php'
        self.proxy_port = None
        self.proxy_host = None
        common.env_setup()

    def finalize(self):
        pass


class ExposeConcealPortHooks(OpenShiftTest):
    def test_method(self):

        self.add_step("Create an app",
                      common.create_app,
                      function_parameters=[self.app_name, 
                                           common.app_types[self.app_type], 
                                           self.user_email, 
                                           self.user_passwd, 
                                           True])

        self.add_step("Emebed mysql",
                      common.embed,
                      function_parameters=[self.app_name, 
                                           'add-%s'%common.cartridge_types['mysql'], 
                                           self.user_email, self.user_passwd],
                      expect_return=0)

        self.add_step("Run exposed hook directly from shell",
                      self.verify,
                      function_parameters=[self.app_name, 
                                           "expose-port", 
                                           "PROXY_PORT=\d+"],
                      expect_return=0)

        self.add_step("Run conceal hook directly from shell",
                      self.verify,
                      function_parameters=[self.app_name, 
                                           "conceal-port", 
                                           None, 0],
                      expect_return=0)

        self.add_step("Check MYSQL connection to PROXY_HOST:PROXY_PORT",
                      self.verify_proxy_port,
                      function_parameters=[self.app_name],
                      expect_description = "Mysql to proxy should fail",
                      expect_return="!0")

        self.add_step("Run show hook directly from shell",
                      self.verify,
                      function_parameters=[self.app_name, 
                                           "show-port", 
                                           r"CLIENT_RESULT: No proxy ports defined", 0],
                      expect_return=0)

        self.add_step("Run exposed hook directly from shell",
                      self.verify,
                      function_parameters=[self.app_name, 
                                           "expose-port", 
                                           "PROXY_PORT=\d+"],
                      expect_return=0)

        self.add_step("Run show hook directly from shell",
                      self.verify,
                      function_parameters=[self.app_name, 
                                           "show-port", 
                                           "PROXY_PORT=\d+"],
                      expect_return=0)

        self.add_step("Check MYSQL connection to PROXY_HOST:PROXY_PORT",
                      self.verify_proxy_port,
                      function_parameters=[self.app_name],
                      expect_description = "Mysql to proxy should pass",
                      expect_return=0)


        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)


    def verify_proxy_port(self, app_name):
        if (self.proxy_host==None or self.proxy_port==None):
            print "ERROR: Unable to capture PROXY_PORT/PROXY_HOST from rhc ctl app -c show-port output"
            return 1

        cart = OSConf.get_apps()[app_name]['embed'][common.cartridge_types['mysql']]
        cmd="echo 'SHOW TABLES' | mysql --host=%s --port=%s --user=%s --password=%s %s "%(self.proxy_host, self.proxy_port, cart['username'], cart['password'], cart['database'])
        (status, output) = common.run_remote_cmd(app_name, cmd)
        return status

    def verify(self, app_name, hook_name, expected_re=None, expected_return=None):
        uuid = OSConf.get_app_uuid(app_name)
        cmd = '''cd /usr/libexec/openshift/cartridges/embedded/%s/info/hooks && ./%s %s %s %s '''%(common.cartridge_types['mysql'], hook_name, app_name, self.domain_name, uuid)
        (status, output) = common.run_remote_cmd(None, cmd, as_root=True)
        #this is stronger condition
        if (expected_re!=None):
            obj = re.search(r"%s"%expected_re, output)
            if obj:
                if (hook_name=='expose-port'):
                    obj = re.search(r"PROXY_HOST=(.*)",output)
                    obj2 = re.search(r"PROXY_PORT=(.*)",output)
                    if (obj and obj2):
                        self.proxy_host = obj.group(1)
                        self.proxy_port = obj2.group(1)
                    else:
                        print "WARNING: Unable to capture PROXY_HOST from output..."
                return 0
            else:
                return 1

        if (expected_return!=None):
            if status==expected_return:
                return 0
            else:
                return 1
        print "WARNING: Nothing to verify?"
        return 1


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ExposeConcealPortHooks)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
