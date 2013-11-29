#!/usr/bin/env python
"""
Jiangtao Zhao
jizhao@redhat.com
2012-08-07

[US2103][RT]Alter domain for a scaling python app which having mongodb added
https://tcms.engineering.redhat.com/case/167687/
[US2103][RT]Alter domain for a scaling jboss app which having mongodb added
https://tcms.engineering.redhat.com/case/167691/
[US2103][RT]Alter domain for a scaling nodejs app which having mongodb added
https://tcms.engineering.redhat.com/case/167692/
[US2103][RT]Alter domain for a scaling perl app which having mongodb added
https://tcms.engineering.redhat.com/case/167693/
[US2103][RT]Alter domain for a scaling ruby app which having mongodb added
https://tcms.engineering.redhat.com/case/167694/
[US2103][RT]Alter domain for a scaling php app which having mongodb added
https://tcms.engineering.redhat.com/case/167695/
[US2123][US2103][RT]Alter domain for a scaling ruby-1.9 app which having mongodb added
https://tcms.engineering.redhat.com/case/174257/
"""
import os
import re
import common
import OSConf
import rhtest
import time


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False      # define to True if your test is interactive (takes user input).
    ITEST = ['DEV', 'INT', 'STG']   #this will be checked by framework
    WORK_DIR = os.path.dirname(os.path.abspath(__file__))

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.info("WARN: Missing variant, used `php` as default")
            self.test_variant = 'jbossas'
        self.summary = "[US2103][RT]Alter domain for a scaling app which having mongodb added"
        self.app_name = "mongo" + common.getRandomString(8)
        self.app_type = common.app_types[self.test_variant]
        self.git_repo = "./%s" % (self.app_name)
        self.domain_name = common.get_domain_name()
        self.new_domain_name = common.getRandomString(9)
        self.record_count = 30
        common.env_setup()

    def finalize(self):
        common.alter_domain(self.domain_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)


class ScalingMongoAfterAlterDomain(OpenShiftTest):

    def get_url_dict(self):
        app_url = OSConf.get_app_url(self.app_name)
        url_dict = {        "php"   :   {   "insert":   "%s/mongo.php?action=insert&size=%s" % (app_url, self.record_count),
                                            "delete":   "%s/mongo.php?action=delete" % (app_url),
                                            "show"  :   "%s/mongo.php?action=show" % (app_url)},
                            "jbossas":  {   "insert":   "%s/mongo.jsp?action=insert&size=%s" % (app_url, self.record_count),
                                            "delete":   "%s/mongo.jsp?action=delete" % (app_url),
                                            "show"  :   "%s/mongo.jsp?action=show" % (app_url)},
                            "perl"  :   {   "insert":   "%s/mongo.pl?action=insert&size=%s" % (app_url, self.record_count),
                                            "delete":   "%s/mongo.pl?action=delete" % (app_url),
                                            "show"  :   "%s/mongo.pl?action=show" % (app_url)},
                            "python":   {   "insert":   "%s/insert?size=%s" % (app_url, self.record_count),
                                            "delete":   "%s/delete" % (app_url),
                                            "show"  :   "%s/show" % (app_url)},
                            "ruby"  :   {   "insert":   "%s/mongo?action=insert&size=%s" % (app_url, self.record_count),
                                            "delete":   "%s/mongo?action=delete" % (app_url),
                                            "show"  :   "%s/mongo?action=show" % (app_url)},
        }
        url_dict["jbosseap"] = url_dict["jbossas"]
        url_dict["jbossews"] = url_dict["jbossas"]
        url_dict["jbossews2"] = url_dict["jbossas"]
        url_dict["ruby-1.9"] = url_dict["ruby"]
        url_dict["python-2.7"] = url_dict["python"]
        url_dict["python-3.3"] = url_dict["python"]
        return url_dict

    def test_method(self):
        self.step("Create scalable %s app: %s" % (self.app_type, self.app_name))
        ret = common.create_app(self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd, True, "./", True)
        self.assert_equal(ret, 0, "Failed to create scalable %s app: %s" % (self.app_type, self.app_name))

        self.url_dict = self.get_url_dict()

        self.step("Embed mongodb to the app")
        ret = common.embed(self.app_name, "add-" + common.cartridge_types["mongodb"], self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to embed mongodb to the app")

        self.step("Copy sample app to git repo and git push")
        self.mongo_user = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mongodb"]]["username"]
        self.mongo_passwd = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mongodb"]]["password"]
        self.mongo_dbname = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mongodb"]]["database"]
        self.mongo_host = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mongodb"]]["url"]
        self.mongo_port = OSConf.default.conf['apps'][self.app_name]['embed'][common.cartridge_types["mongodb"]]["port"]
        if self.test_variant in ("php"):
            cmd = " && ".join([ "cd %s/php/" % (self.git_repo),
                                "cp %s/../cartridge/app_template/mongodb/php/mongo.php ." % (OpenShiftTest.WORK_DIR),
                                ])
        elif self.test_variant in ("perl"):
            cmd = " && ".join([ "cd %s/perl/" % (self.git_repo),
                                "cp %s/../cartridge/app_template/mongodb/perl/mongo.pl ." % (OpenShiftTest.WORK_DIR),
                                "echo 'MongoDB' >> ../deplist.txt",
                                ])
        elif self.test_variant in ("jbossas", "jbosseap", "jbossews", "jbossews2"):
            cmd = " && ".join([ """sed -i '/<system-properties>/ a\\\n<property name="org.apache.catalina.session.StandardManager.MAX_ACTIVE_SESSIONS" value="-1"/>' %s/.openshift/config/standalone.xml""" % (self.git_repo),
                                "cd %s/src/main/webapp/" % (self.git_repo),
                                "mkdir -p WEB-INF/lib/",
                                "cp %s/../cartridge/app_template/mongodb/jbossas/mongo.jsp ." % (OpenShiftTest.WORK_DIR),
                                "cp %s/../cartridge/app_template/mongodb/jbossas/mongo-2.8.0.jar WEB-INF/lib/" % (OpenShiftTest.WORK_DIR),
                                ])
        elif self.test_variant in ("python"):
            cmd = " && ".join([ "cd %s/wsgi/" % (self.git_repo),
                                "cp %s/../cartridge/app_template/mongodb/python/application ." % (OpenShiftTest.WORK_DIR),
                                "sed -i -e \"s/^.*install_requires.*$/      install_requires=['pymongo'],/g\" ../setup.py",
                                ])
        elif self.test_variant in ("python-2.7"):
            cmd = " && ".join([ "cd %s/wsgi/" % (self.git_repo),
                                "cp %s/../cartridge/app_template/mongodb/python-2.7/application ." % (OpenShiftTest.WORK_DIR),
                                "cp -rf  %s/../client/data/snapshot_restore_mysql_data/setupmongo.py ../setup.py" % (OpenShiftTest.WORK_DIR),
                                "sed -i -e \"s/^.*install_requires.*$/      install_requires=['pymongo'],/g\" ../setup.py",
                                ])
        elif self.test_variant in ("python-3.3"):
            cmd = " && ".join([ "cd %s/wsgi/" % (self.git_repo),
                                "cp %s/../cartridge/app_template/mongodb/python-3.3/application ." % (OpenShiftTest.WORK_DIR),
                                "cp -rf  %s/../client/data/snapshot_restore_mysql_data/setupmongo3.py ../setup.py" % (OpenShiftTest.WORK_DIR),
                                #"sed -i -e \"s/^.*install_requires.*$/      install_requires=['pymongo3'],/g\" ../setup.py",
                                ])
        elif self.test_variant in ("ruby", "ruby-1.9"):
            cmd = " && ".join([ "cd %s" % (self.git_repo),
                                "cp -f %s/../cartridge/app_template/mongodb/ruby/* ." % (OpenShiftTest.WORK_DIR),
                                "bundle install",
                                ])
        cmd = " && ".join([cmd, "git add . && git commit -amt && git push"])
        (ret, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(ret, 0, "Failed to copy sample app to local git repo and git push")

        self.step("Wait for the app to become available")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, 'There is no record in database', "-H 'Pragma: no-cache' -L", 5, 6)
        self.assert_equal(ret, 0, "The app doesn't become available in reasonable time")

        self.step("Insert data into mongodb")
        time.sleep(30)
        url = self.url_dict[self.test_variant]["insert"]
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        (ret, output) = common.command_getstatusoutput(cmd)
        self.assert_equal(ret, 0, "Failed to insert data into mongodb")
        self.assert_match("%s records have been inserted into mongodb" % (self.record_count), output)

        self.step("Check mongodb data exists")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, ["There are %s records in database" % (self.record_count), "This is testing data for testing snapshoting and restoring big data in mongodb database"],
                                    "-H 'Pragma: no-cache' -L", 5, 6, True)
        self.assert_equal(ret, 0, "The mongodb data doesn't exist")

        self.step("Scale up the app")
        ret = common.scale_up(self.app_name)
        self.assert_equal(ret, 0, "Failed to scale up the app")

        self.step("Verify scale up")
        gear_lst = self.verify_scale_up(url)
        self.assert_equal(len(gear_lst), 2, "Failed to verify scale up. %d gears found" % (len(gear_lst)))

        self.step("Alter domain name")
        print self.new_domain_name
        ret = common.alter_domain(self.new_domain_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to alter domain")

        self.step("Stop the app")
        ret = common.stop_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to stop app")

        self.step("Start the app")
        ret = common.start_app(self.app_name, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd)
        self.assert_equal(ret, 0, "Failed to start app")

        time.sleep(10)
        self.step("Wait for the DNS to take effect")
        url = OSConf.get_app_url(self.app_name)
        ret = common.grep_web_page(url, 'Welcome to OpenShift')
        self.assert_equal(ret, 0, "The DNS doesn't take effect in reasonable time")

        self.url_dict = self.get_url_dict()
        url = self.url_dict[self.test_variant]["show"]

        self.step("Verify scale up")
        gear_lst = self.verify_scale_up(url)
        self.assert_equal(len(gear_lst), 2, "Failed to verify scale up. %d gears found" % (len(gear_lst)))

        self.step("Check mongodb data exists")
        url = self.url_dict[self.test_variant]["show"]
        ret = common.grep_web_page(url, ["There are %s records in database" % (self.record_count), "This is testing data for testing snapshoting and restoring big data in mongodb database"],
                                    "-H 'Pragma: no-cache' -L", 5, 6, True)
        self.assert_equal(ret, 0, "The mongodb data doesn't exist")

        return self.passed("%s passed" % self.__class__.__name__)

    def verify_scale_up(self, url, retry_times=10):
        gear_lst = []
        cmd = "curl -H 'Pragma: no-cache' -L '%s'" % (url)
        for i in range(retry_times):
            (ret, output) = common.command_getstatusoutput(cmd, quiet=True)
            if ret != 0:
                time.sleep(3)
            else:
                pattern = re.compile(r'(?<=Gear DNS: ).+com', re.M)
                match = pattern.search(output)
                if match == None:
                    time.sleep(3)
                elif match.group(0) not in gear_lst and output.find("There are %s records in database" % (self.record_count)) != -1:
                    gear_lst.append(match.group(0))
        self.debug("Gears found: " + ' '.join(gear_lst))
        return gear_lst

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ScalingMongoAfterAlterDomain)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
