#
#  File name: apps_when_libra_service_restart.py
#  Date:      2012/03/06 15:51
#  Author:    mzimen@redhat.com
#

import re
import rhtest
import common
import OSConf


class OpenShiftTest(rhtest.Test):
    ITEST="DEV"

    def initialize(self):
        self.info("[rhc-node] All created applications will restart when restart libra service as root")
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_name = common.getRandomString(7)
        self.num_apps = 2
        try:
            self.app_type = self.get_variant()
        except:
            self.app_type = 'php'
        common.env_setup()

    def finalize(self):
        #put back original init.d script"
        common.run_remote_cmd_as_root("mv -f /etc/init.d/libra.O /etc/init.d/libra" )


class AppsWhenLibraServiceRestart(OpenShiftTest):
    def test_method(self):

        for i in range(self.num_apps):
            self.add_step("Create an app#%s"%i,
                    common.create_app,
                    expect_description = "App should be created successfully.",
                    function_parameters=["%s%s"%(self.app_name,i), 
                                          common.app_types[self.app_type], 
                                          self.user_email, self.user_passwd, False],
                    expect_return=0)
   
        #modify /etc/init.d/libra to sleep 20 between stop and start
        self.add_step(
                "Edit /etc/init.d/libra to add 'sleep 20' between stopuser and startuser",
                self.modify_init_libra,
                expect_description = "Editation should be completed.",
                expect_return=0)

        self.add_step("Restart libra service",
                self.restart_libra,
                expect_description = "Restarting should work",
                expect_return=0)

        self.add_step("Check the number of restarting processes",
                self.check_res,
                expect_description = "There should be APPS=%s string found"%self.num_apps,
                expect_return=0)

        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


    def modify_init_libra(self):
        cmd = """rm -f /etc/init.d/libra.O; cp /etc/init.d/libra /etc/init.d/libra.O ; sed -i '
/restartuser)/ {
N
/stopuser/a sleep 10
}' /etc/init.d/libra && echo OK
"""
        (status, output) = common.run_remote_cmd(None, cmd, as_root=True)
        obj = re.search(r"OK", output)
        if status==0 and obj:
            return 0
        else:
            return 1 

    def restart_libra(self):
        cmd ='''
cat <<'EOF' >/root/restart_libra.sh &&
#!/bin/sh

#nohup just doesn't work...:(
#nice nohup /etc/init.d/libra restart </dev/null &
( /etc/init.d/libra restart >/tmp/LOG 2>&1 ) &


exit 0
EOF
chmod +x /root/restart_libra.sh; /root/restart_libra.sh 2>&1 & exit 0'''
        (status, output) = common.run_remote_cmd(None,cmd , True)
        return status

    def check_res(self):
        uuid = []
        for i in range(self.num_apps):
            uuid.append(OSConf.get_app_uuid("%s%s"%(self.app_name,i)))

        cmd = [
               "sleep 0.5",
               "ps -ef",
               "grep '/bin/bash /etc/init.d/libra restartuser'",
               "grep -v grep >>/tmp/.abc"]

        cmd2 = ["cat /tmp/.abc ",
                "egrep '%s'"%("|".join(uuid)),
                "sort -k 6",
                "uniq -f 6",
                """awk '{lines++}END{print "APPS=" lines}'"""]
        (status, output) = common.run_remote_cmd_as_root(
               "rm -rf /tmp/.abc "
               + " ; "
               + " for i in `seq 0 120`; do "+"|".join(cmd)+";done "
               + " ; "
               + "|".join(cmd2)
               + ";rm -f /tmp/.abc"
               )
        obj = re.search(r"APPS=%s"%self.num_apps, output)
        if status==0 and obj:
            return 0
        else: 
            return 1

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(AppsWhenLibraServiceRestart)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# end of apps_when_libra_service_restart.py
#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
