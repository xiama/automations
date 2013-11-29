#
#  File name: subaccount_delete.py
#  Date:      2012/10/02 16:08
#  Author:    mzimen@redhat.com
#

import common
import rhtest
import brokerdb


class OpenShiftTest(rhtest.Test):
    #ITEST = ["INT", "STG"]

    def initialize(self):
        self.info("subaccount_delete")
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'php'
        self.info("VARIANT: %s"%self.test_variant)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.get_random_string(10)
        self.app_type = common.app_types[self.test_variant]
        self.subdomain = common.get_random_string(10)
        self.subaccount = common.get_random_string(10)
        self.gear_profile = 'small'
        common.env_setup()


    def finalize(self):
        pass


class SubaccountDelete(OpenShiftTest):
    def test_method(self):
        common_options = ' -d nolinks=1 -s -k -H "Accept:application/json" -H "X-Impersonate-User:%s" -u %s:%s '%(self.subaccount, self.user_email, self.user_passwd)

        self.step("1. Create sub domain as sub account")
        cmd = 'curl -X POST %s -d id=%s  https://%s/broker/rest/domains'%(common_options, self.subdomain, self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("2. Add ssh key for sub account")
        cmd = 'curl %s -X POST --data-urlencode name=default -d type=%s --data-urlencode content=%s https://%s/broker/rest/user/keys'%(
                common_options,
                common.get_public_key_type(),
                common.dump_public_key(),
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('created', output)

        self.step("3. Create app with  sub account")
        cmd = 'curl %s -X POST -d name=%s -d cartridge=%s -d gear_profile=%s https://%s/broker/rest/domains/%s/applications'%(
                common_options,
                self.app_name,
                self.app_type,
                self.gear_profile,
                self.config.instance_info['ip'],
                self.subdomain)
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('was created', output)

        self.step("4. Try to delete this sub account when there is still some app belong this sub account existing.")
        cmd = 'curl %s -X POST https://%s/broker/rest/user -X DELETE'%(
                common_options, 
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('has valid domain', output)
        self.assert_match('unprocessable_entity', output)

        self.step("5. Destroy app as sub account")
        cmd = 'curl %s -X DELETE https://%s/broker/rest/domains/%s/applications/%s'%(
                common_options, 
                self.config.instance_info['ip'], 
                self.subdomain, 
                self.app_name)
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("6. Try to delete this sub account when there is still domain belong this sub account existing.")
        cmd = 'curl %s -X POST https://%s/broker/rest/user -X DELETE'%(
                common_options, 
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('has valid domain', output)
        self.assert_match('unprocessable_entity', output)

        self.step("7. Force clean sub domain as sub account")
        cmd = 'curl %s -X DELETE -d force=true https://%s/broker/rest/domains/%s'%(
                common_options,
                self.config.instance_info['ip'], 
                self.subdomain)
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("8. Delete this sub account.")
        cmd = 'curl %s -X POST https://%s/broker/rest/user -X DELETE'%(
                common_options, 
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("Log into instance, connect mongodb, run to following mongo shell to verify this sub account is indeed deleted.")
        self.verify_mongo()

        #9. Log into instance, connect mongodb, run to following mongo shell to verify this sub account is indeed deleted.

        '''
> db.user.findOne({"_id":"<sub_account>"})
        '''

        #("10. Repeat step 1~3, delete this subaccount with 'force' option when subaccount has domain and application associated.")
        self.step("10. Create sub domain as sub account")
        cmd = 'curl -X POST %s -d id=%s  https://%s/broker/rest/domains'%(common_options, self.subdomain, self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("11. Add ssh key for sub account")
        cmd = 'curl %s -X POST --data-urlencode name=default -d type=%s --data-urlencode content=%s https://%s/broker/rest/user/keys'%(
                common_options,
                common.get_public_key_type(),
                common.dump_public_key(),
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('created', output)

        self.step("12. Create app with sub account")
        cmd = 'curl %s -X POST -d name=%s -d cartridge=%s -d gear_profile=%s https://%s/broker/rest/domains/%s/applications'%(
                common_options,
                self.app_name,
                self.app_type,
                self.gear_profile,
                self.config.instance_info['ip'],
                self.subdomain)
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)
        self.assert_match('was created', output)

        self.step("13. DELETE with (brute) FORCE")
        cmd = 'curl %s -X POST https://%s/broker/rest/user -X DELETE -d force=true'%(
                common_options,
                self.config.instance_info['ip'])
        (ecode, output) = common.cmd_get_status_output(cmd)
        self.assert_equal(0, ecode)

        self.step("14. Log into instance, connect mongodb, run to following mongo shell to verify this sub account is indeed deleted.")
        self.verify_mongo()

        return self.passed("%s passed" % self.__class__.__name__)


    def verify_mongo(self):
        mongo = brokerdb.BrokerDB(collections=['user'], force_cache=True)
        users = mongo.get_collection('user')
        for u in users:
            if u.has_key('parent_user_login'):
                if u['parent_user_login'] == self.config.OPENSHIFT_user_email:
                    self.assert_not_match(str(u['_id']), self.subaccount,
                                          "Found subaccount entry in mongodb, which should had been deleted: %s"%u)
        '''
        > db.user.findOne({"_id":"<sub_account>"})
        > db.domains.find({_id:"<namespace>"})
        > db.applications.find({UUID::<UUID>",name:"<app_name>"})
        '''


class OpenShiftTestSuite(rhtest.TestSuite):
    pass


def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(SubaccountDelete)
    return suite


def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of subaccount_delete.py 
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
