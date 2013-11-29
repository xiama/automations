import os

import common
import OSConf
import rhtest

WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        try:
            self.test_variant = self.get_variant()
        except:
            self.test_variant = 'perl'
        if not common.app_types.has_key(self.test_variant):
            raise Exception("Invalid/Unknown variable: OPENSHIFT_test_name")

        self.info("VARIANT: %s"%self.test_variant)
        self.app_name = common.getRandomString(10)
        self.app_type = common.app_types[self.test_variant]

        common.env_setup()

        # print test case summary
        self.info("""
[US561][rhc-cartridge] PHP: Pear pre-processing
[US561][rhc-cartridge] Perl: Cpan pre-processing
[US561][rhc-cartridge] Python: Easy_install pre-processing
[US561][rhc-cartridge] Ruby: Gem pre-processing
[US561][rhc-cartridge] Jboss: Maven pre-processing
[US1107][rhc-cartridge] PHP app libraries cleanup using force_clean_build marker
[US1107][rhc-cartridge] PERL app libraries cleanup using force_clean_build marker
[US1107][rhc-cartridge] WSGI app libraries cleanup using force_clean_build marker
[US1107][rhc-cartridge] RACK app libraries cleanup using force_clean_build marker
[US1107][rhc-cartridge] JBOSSAS app libraries cleanup using force_clean_build marker
[US590][Runtime][rhc-cartridge]nodejs app modules cleanup using force_clean_build marker""")

    def finalize(self):
        pass
    
class ServerSideBundlingLibsAndForceCleanBuild(OpenShiftTest):
    def test_method(self):

        # 1.Create an app
        self.add_step("1. Create an %s app" % (self.test_variant),
                common.create_app,
                function_parameters=[self.app_name, self.app_type, self.config.OPENSHIFT_user_email, self.config.OPENSHIFT_user_passwd],
                expect_description="the app should be created successfully",
                expect_return=0)

        # 2.Customize this app
        if self.test_variant == "php":
            cmd = "echo 'channel://pear.php.net/Validate-0.8.4' >%s/deplist.txt && cp -f %s/app_template/php_pear.php %s/php/index.php" %(self.app_name, WORK_DIR, self.app_name)
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            cmd = """cd %s && echo "source 'http://rubygems.org'\ngem 'rack'\ngem 'pg'" > Gemfile && sed -i "/require 'thread-dump'/ d" config.ru && bundle install""" %(self.app_name)
        elif self.test_variant in ("python","wsgi"):
            cmd = "cd %s && sed -i '9s/^#//g' setup.py && cp %s/app_template/wsgi-test.tar.gz ./ && tar xzvf wsgi-test.tar.gz" %(self.app_name, WORK_DIR)
        elif self.test_variant == "perl":
            cmd = """cd %s && echo -e '#!/usr/bin/perl\nprint "Content-type: text/html\\r\\n\\r\\n";\nprint "Welcome to OpenShift\\n";' >perl/index.pl && echo YAML >>deplist.txt""" %(self.app_name)
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd = "cd %s && cp %s/app_template/helloworld.tar.gz ./ && tar zxf helloworld.tar.gz" %(self.app_name, WORK_DIR)
        elif self.test_variant in ("nodejs"):
            cmd = """cd %s && sed -i '{\n/dependencies/ a\\\n    "optimist": "0.3.4"\n}' package.json && sed -i "4 i var argv    = require('optimist').argv;" server.js""" % (self.app_name)
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        self.add_step("2.Customize this app",
                cmd,
                expect_description="the git repo should be modified successfully",
                expect_return=0)

        # 3.Git push all the changes
        if self.test_variant == "php":
            exp_str = "install ok: channel://pear.php.net/Validate-0.8.4"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            exp_str = "Installing pg"
        elif self.test_variant in ("python", "wsgi"):
            exp_str = "Adding Django [\d.]+ to easy-install.pth"
        elif self.test_variant == "perl":
            exp_str = "Successfully installed YAML"
        elif self.test_variant in ("jbossas", "jbosseap"):
            exp_str = "remote: Downloading: .*javax.*"
        elif self.test_variant in ("nodejs"):
            exp_str = "remote: npm info install optimist@0.3.4"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        self.add_step("3.Git push all the changes",
                "cd %s && touch x && git add . && git commit -am t && git push" %(self.app_name),
                expect_description="Git push should succeed",
                expect_return=0,
                expect_str=[exp_str])

        # 4. Generate test script
        if self.test_variant == "php":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/download/Validate-0.8.4.tgz && ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/php/Validate.php"
        elif self.test_variant in ("ruby", "rack"):
            cmd_str = "ls -la ${OPENSHIFT_REPO_DIR}vendor/bundle/ruby/1.8*/gems/pg*"
        elif self.test_variant in ("ruby-1.9"):
            cmd_str = "ls -la ${OPENSHIFT_REPO_DIR}vendor/bundle/ruby/1.9*/gems/pg*"
        elif self.test_variant in ("python", "wsgi"):
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}python/virtenv/lib/python2.6/site-packages/Django*"
        elif self.test_variant == "perl":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}perl/perl5lib/lib/perl5/YAML"
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}.m2/repository/javax"
        elif self.test_variant in ("nodejs"):
            cmd_str = "ls ${OPENSHIFT_REPO_DIR}node_modules/optimist/"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        shell_script = '''#!/bin/bash
command="%s"
echo "$command"
eval "$command"
test $? == 0 && echo "RESULT=0" || echo "RESULT=1"''' %(cmd_str)
        self.add_step("4.Write .openshift/action_hooks/deploy",
                "echo '%s' >%s/.openshift/action_hooks/deploy; \n chmod +x %s/.openshift/action_hooks/deploy" %(shell_script, self.app_name, self.app_name),
                expect_return=0)

        # 5.Check the dependencies are installed
        self.add_step("5.Check the dependencies are installed vir git hooks",
                "cd %s && touch xx && git add . && git commit -am t && git push" %(self.app_name),
                expect_description="Check should PASS",
                expect_return=0,
                expect_str=["RESULT=0"])

        # 6.Check app via browser
        def get_app_url(self, suffix=""):
            def closure():
                return OSConf.get_app_url(self.app_name)+suffix
            return closure

        url_suffix=""
        if self.test_variant == "php":
            test_html = "get_correct_number"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            test_html = "Welcome to OpenShift"
        elif self.test_variant in ("python", "wsgi"):
            test_html = "Congratulations on your first Django-powered page"
        elif self.test_variant == "perl":
            test_html = "Welcome to OpenShift"
        elif self.test_variant in ("jbossas", "jbosseap"):
            test_html = "Hello World!"
            url_suffix = "/HelloWorld/HelloWorld"
        elif self.test_variant in ("nodejs"):
            test_html = "Welcome to OpenShift"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)
        self.add_step("6.Check app via browser",
                common.grep_web_page,
                function_parameters=[get_app_url(self, url_suffix), test_html, "-H 'Pragma: no-cache' -L", 5, 9],
                expect_description="'%s' should be found in the web page" % (test_html),
                expect_return=0)

        # 7. Using the installed package
        if self.test_variant == "php":
            exp_str = ""
            unexp_str = "remote: downloading"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            exp_str = "remote: Using pg"
            unexp_str = "remote: Installing"
        elif self.test_variant in ("python", "wsgi"):
            exp_str = ""
            unexp_str = "remote: Downloading"
        elif self.test_variant == "perl":
            exp_str = ""
            unexp_str = "remote: Fetching"
        elif self.test_variant in ("jbossas", "jbosseap"):
            exp_str = ""
            unexp_str = "remote: Downloading"
        elif self.test_variant in ("nodejs"):
            exp_str = ""
            unexp_str = "remote: npm http GET.*optimist"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)
        self.add_step("7. Re-using the installed libs, no new installation",
                "cd %s && touch xxx && git add . && git commit -am t && git push" %(self.app_name),
                expect_description="Check should PASS",
                expect_return=0,
                expect_str=[exp_str],
                unexpect_str=[unexp_str])

        # 8. More test for rack app
        if self.test_variant in ( "rack","ruby", "ruby-1.9"):
            self.add_step(
                    "8. Edit Gemfile to add another gem we want to install,",
                    '''cd %s && echo "gem 'rhc'" >>Gemfile ; bundle check ; bundle install ; sed -i "s/rhc \(.*\)/rhc \(0.71.2\)/g" Gemfile.lock''' %(self.app_name),
                    expect_return=0)

            self.add_step(
                    "9. Re-using the installed libs, and install new libs",
                    "cd %s && git add . && git commit -am t && git push" %(self.app_name),
                    expect_return=0,
                    expect_str=["remote: Using pg", "remote: Installing rhc"])
        else:
            self.info("skip step 8")
            self.info("skip step 9")


        # 10. Touch a empty force_clean_build file in your local git repo
        self.add_step("10. Touch a empty force_clean_build file in your local git repo.",
                "touch %s/.openshift/markers/force_clean_build" %(self.app_name),
                expect_description="Successfully touched force_clean_build",
                expect_return=0)

        # 11. Remove libraries
        if self.test_variant == "php":
            cmd = "echo '' > %s/deplist.txt" %(self.app_name)
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd = "echo 'No denpendency need to be remove for jbossas app'"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            cmd = "cd %s && sed -i '$d' Gemfile && bundle check" %(self.app_name)
        elif self.test_variant in ("python", "wsgi"):
            cmd = "cd %s && sed -i '9s/^/#/g' setup.py" %(self.app_name)
        elif self.test_variant == "perl":
            cmd = "echo '' > %s/deplist.txt" %(self.app_name)
        elif self.test_variant in ("nodejs"):
            cmd = "cd %s && sed -i '{/optimist/ d}' package.json" % (self.app_name)
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)
        self.add_step("11. Remove libraries dependency",
                cmd,
                expect_description="Modification succeed",
                expect_return=0)

        # 12. re-write .openshift/action_hooks/deploy
        if self.test_variant == "php":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/download/Validate-0.8.4.tgz || ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/php/Validate.php"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant in ("ruby", "rack"):
            cmd_str = "ls ${OPENSHIFT_REPO_DIR}vendor/bundle/ruby/1.8*/gems/rhc*"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant in ("ruby-1.9"):
            cmd_str = "ls ${OPENSHIFT_REPO_DIR}vendor/bundle/ruby/1.9*/gems/rhc*"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant == "perl":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}perl/perl5lib/lib || ls ~/.cpanm/work"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant in ("python", "wsgi"):
            cmd = "echo 'No need to re-write for wsgi app'"
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd = "echo 'No need to re-write for jbossas app'"
        elif self.test_variant in ("nodejs"):
            cmd = "echo 'No need to re-write for jbossas app'"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        self.add_step("12. Re-write .openshift/action_hooks/deploy",
                cmd,
                expect_return=0)

        # 13. git push all the changes
        if self.test_variant in ("jbossas", "jbosseap"):
            str_list = [".openshift/markers/force_clean_build found", "remote: Downloading"]
            unexpect_str_list = []
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            str_list = ["remote: Installing pg", "ls: cannot access", "RESULT=1"]
            unexpect_str_list = ["remote: Installing rhc"]
        elif self.test_variant == "php":
            str_list = [".openshift/markers/force_clean_build found", "ls: cannot access", "RESULT=1"]
            unexpect_str_list = ["remote: downloading"]
        elif self.test_variant == "perl":
            str_list = [".openshift/markers/force_clean_build found", "ls: cannot access", "RESULT=1"]
            unexpect_str_list = ["remote: Fetching"]
        elif self.test_variant in ("python", "wsgi"):
            str_list = [".openshift/markers/force_clean_build found", "ls: cannot access", "RESULT=1"]
            unexpect_str_list = ["remote: Downloading"]
        elif self.test_variant in ("nodejs"):
            str_list = ["force_clean_build marker found!  Recreating npm modules", "ls: cannot access", "RESULT=1"]
            unexpect_str_list = []
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        self.add_step("13. git push all the changes",
                "cd %s && touch xxxx && git add . && git commit -am t && git push" 
                    %(self.app_name),
                expect_description="libraries are removed successfully",
                expect_return=0,
                expect_str=str_list,
                unexpect_str=unexpect_str_list)


        # 14.Check app via browser
        url_suffix=""
        if self.test_variant == "php":
            test_html = ""
            unexpect_test_html = "get_correct_number"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            test_html = "Welcome to OpenShift"
            unexpect_test_html = "NO_XX"
        elif self.test_variant in ("python","wsgi"):
            test_html = "Internal Server Error"
            unexpect_test_html = "Congratulations on your first Django-powered page"
        elif self.test_variant == "perl":
            test_html = "Welcome to OpenShift"
            unexpect_test_html = "NO_XX"
        elif self.test_variant in ("jbossas", "jbosseap"):
            test_html = "Hello World!"
            unexpect_test_html = "NO_XX"
            url_suffix = "/HelloWorld/HelloWorld"
        elif self.test_variant in ("nodejs"):
            test_html = "Service Temporarily Unavailable"
            unexpect_test_html = "Welcome to OpenShift"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)
        self.add_step(
                "14.Check app via browser, php/wsgi app should NOT availale Now, jbossas/perl/rack still working fine",
                "curl -L -H 'Pragma: no-cache' %s",
                string_parameters = [get_app_url(self, url_suffix)],
                expect_str=[test_html],
                unexpect_str=[unexpect_test_html],
                try_interval=9,
                try_count=6)

        # 15. Add libraries back
        if self.test_variant == "php":
            cmd = "echo 'channel://pear.php.net/Validate-0.8.4' > %s/deplist.txt" %(self.app_name)
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd = "echo 'No denpendency need to be remove for jbossas app'"
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            cmd = '''cd %s && echo "gem 'rhc'" >>Gemfile && bundle check && sed -i "s/rhc \(.*\)/rhc \(0.71.2\)/g" Gemfile.lock''' %(self.app_name)
        elif self.test_variant in ("python", "wsgi"):
            cmd = "cd %s && sed -i '9s/^#//g' setup.py" %(self.app_name)
        elif self.test_variant == "perl":
            cmd = "echo 'YAML' > %s/deplist.txt" %(self.app_name)
        elif self.test_variant in ("nodejs"):
            cmd = """cd %s && sed -i '{\n/dependencies/ a\\\n    "optimist": "0.3.4"\n}' package.json""" % (self.app_name)
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)
        if self.test_variant in ("jbossas", "jbosseap"):
            self.info("skip step 15 for jbossas app")
        else:
            self.add_step("15. Added libraries denpendency back",
                    cmd,
                    expect_return=0)

        # 16. re-write .openshift/action_hooks/deploy
        if self.test_variant == "php":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/download/Validate-0.8.4.tgz \&\& ls ${OPENSHIFT_HOMEDIR}php/phplib/pear/pear/php/Validate.php"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            cmd = "echo 'No need to re-write for rack app'"
        elif self.test_variant == "perl":
            cmd_str = "ls ${OPENSHIFT_HOMEDIR}perl/perl5lib/lib \&\& ls ~/.cpanm/work"
            cmd = """sed -i 's#command="ls.*"#command="%s"#g' %s/.openshift/action_hooks/deploy""" %(cmd_str, self.app_name)
        elif self.test_variant in ("python","wsgi"):
            cmd = "echo 'No need to re-write for wsgi app'"
        elif self.test_variant in ("jbossas", "jbosseap"):
            cmd = "echo 'No need to re-write for jbossas app'"
        elif self.test_variant in ("nodejs"):
            cmd = "echo 'No need to re-write for nodejs app'"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        if self.test_variant in ("jbossas", "jbosseap"):
            print "\nskip step 16 for jbossas app"
        else:
            self.add_step(
                    "16. Re-write .openshift/action_hooks/deploy",
                    cmd,
                    expect_return=0)

        # 17. git push all the changes
        if self.test_variant in ("jbossas", "jbosseap"):
            str_list = [".openshift/markers/force_clean_build found", "remote: Downloading"]
        elif self.test_variant in ("ruby", "rack", "ruby-1.9"):
            str_list = ["remote: Installing pg", "remote: Installing rhc", "RESULT=0"]
            unexpect_str_list = ["No such file or directory"]
        elif self.test_variant == "php":
            str_list = [".openshift/markers/force_clean_build found", "remote: downloading", "RESULT=0"]
            unexpect_str_list = ["No such file or directory"]
        elif self.test_variant == "perl":
            str_list = [".openshift/markers/force_clean_build found", "remote: Fetching", "RESULT=0"]
            unexpect_str_list = ["No such file or directory"]
        elif self.test_variant in ("python", "wsgi"):
            str_list = [".openshift/markers/force_clean_build found", "remote: Downloading", "RESULT=0"]
            unexpect_str_list = ["No such file or directory"]
        elif self.test_variant in ("nodejs"):
            str_list = ["RESULT=0"]
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        if self.test_variant in ("jbossas", "jbosseap"):
            self.info("skip step 17 for jbossas app")
        else:
            self.add_step("17. git push all the changes",
                    "cd %s && touch xxxxx && git add . && git commit -am t && git push" %(self.app_name),
                    expect_description="libraries are removed successfully",
                    expect_return=0,
                    expect_str=str_list,
                    unexpect_str=unexpect_str_list)

        # 18.Check app via browser
        if self.test_variant == "php":
            test_html = "get_correct_number"
        elif self.test_variant in ("rack","ruby", "ruby-1.9"):
            test_html = "Welcome to OpenShift"
        elif self.test_variant in ( "wsgi", "python") :
            test_html = "Congratulations on your first Django-powered page"
        elif self.test_variant == "perl":
            test_html = "Welcome to OpenShift"
        elif self.test_variant in ("jbossas", "jbosseap"):
            test_html = "Hello World!"
        elif self.test_variant in ("nodejs"):
            test_html = "Welcome to OpenShift"
        else:
            return self.failed("%s failed: Invalid test_variant" % self.__class__.__name__)

        if self.test_variant in ("jbossas", "jbosseap"):
            self.info("skip step 18 for jbossas app")
        else:
            self.add_step(
                    "18.Check app via browser, now all kinds of app should work fine",
                    "curl -H 'Pragma: no-cache' %s",
                    string_parameters = [get_app_url(self)],
                    expect_return=0,
                    expect_str=[test_html],
                    try_interval=9,
                    try_count=3)

        self.run_steps()

        return self.passed("%s passed" % self.__class__.__name__)

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(ServerSideBundlingLibsAndForceCleanBuild)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()

#
# vim: set tabstop=4:shiftwidth=4:expandtab: 
