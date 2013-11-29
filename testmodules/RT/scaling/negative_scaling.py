#!/usr/bin/env python
import os
import OSConf
import common
import rhtest
import time
# user defined packages
import fileinput, re


class OpenShiftTest(rhtest.Test):
    INTERACTIVE = False

    def initialize(self):
        self.info("[US1463][BusinessIntegration] Scale-up / Scale down an non-scalable application ")
        try:
            self.test_variant = self.get_variant()
        except Exception as e:
            self.info("Warning: no test_variant defined, used `php` as default")
            self.test_variant = "ruby-1.8"
            #self.test_variant = "php"
        self.info("VARIANT: %s"%self.test_variant)
        self.user_email = self.config.OPENSHIFT_user_email
        self.user_passwd = self.config.OPENSHIFT_user_passwd
        self.app_type = common.app_types[self.test_variant]
        self.app_name = common.getRandomString(10)
        self.domain_name = common.get_domain_name()
        self.git_repo = './' + self.app_name
        common.env_setup()

    def finalize(self):
        pass
        

class NegativeScaling(OpenShiftTest):
    def configure_scale_up_test_application(self, git_repo):
        if self.test_variant == 'php':
            txt = "<?php header('Content-Type: text/plain'); echo $_ENV['OPENSHIFT_GEAR_DNS']; ?>"
            f_path = "php/gear.php"
        if self.test_variant == 'perl':
            txt = "#!/usr/bin/perl\n print 'Content-type: text/html\r\n\r\n';\n print $ENV{'OPENSHIFT_GEAR_DNS'};"
            f_path = "perl/gear.pl"
            cmd= "touch %s" % os.path.join(git_repo, f_path)
            os.system(cmd)
        if self.test_variant in ("ruby", "ruby-1.9"):
            f_path = "config.ru"
            try:
                for line in fileinput.input(git_repo + "/config.ru", inplace = 1):
                    if re.search("map '/health' do", line):
                        print "map '/gear.rb' do"
                        print "  gear_dns = proc do |env|"
                        print "    [ 200, { 'Content-Type' => 'text/plain'}, ENV['OPENSHIFT_GEAR_DNS'] ]"
                        print "  end"
                        print "  run gear_dns"
                        print "end"
                        print
                    print line
            except Exception as e:
                fileinput.close()
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()
        if self.test_variant == "python":
            f_path = "wsgi/application"
            try:
                for line in fileinput.input(git_repo + "/wsgi/application", inplace = 1):
                    if re.search("PATH_INFO.+/env", line):
                        print "    elif environ['PATH_INFO'] == '/gear.py':"
                        print "        response_body = os.environ['OPENSHIFT_GEAR_DNS']"
                    print line,
            except Exception as e:
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()

        if self.test_variant in ('jbossas', 'jbosseap', 'jbossews', 'jbossews2'):
            f_path = 'src/main/webapp/gear.jsp'
            gear_file = open(git_repo + "/src/main/webapp/gear.jsp", "w")
            gear_file.write("<%@ page contentType=\"text/plain\" language=\"java\" import=\"java.sql.*\" %>\n")
            gear_file.write("<%@ page import=\"javax.naming.*\" %>\n")
            gear_file.write("<%@ page import=\"java.util.*\" %>\n")
            gear_file.write("<%@ page trimDirectiveWhitespaces=\"true\" %>\n")
            gear_file.write("<%\n")
            gear_file.write("Map map = System.getenv();\n")
            gear_file.write("out.print(map.get(\"OPENSHIFT_GEAR_DNS\"));\n")
            gear_file.write("%>\n")
            gear_file.close()  

        if self.test_variant == "nodejs":
            f_path = "server.js"
            try:
                for line in fileinput.input(git_repo + "/server.js", inplace = 1):
                    if re.search("Handler for GET /health", line):
                        print "app.get('/gear.js', function(req, res){"
                        print "    result = process.env.OPENSHIFT_GEAR_DNS;"
                        print "    res.send(result, {'Content-Type': 'text/plain'});"
                        print "});"
                    print line,
            except Exception as e:
                fileinput.close()
                print type(e)
                print e.args
                return 1
            finally:
                fileinput.close()
        
        if self.test_variant in ("php", "perl"):
            f = open(os.path.join(git_repo, f_path), 'w')
            f.write(txt)
            f.close()

        configuration_steps = [
            "cd %s" % git_repo, 
            "git add %s" % (f_path),
            "git commit -a -m %s" % (f_path),
            "git push"
        ]

        return common.command_get_status(" && ".join(configuration_steps))

    def number_of_gears(self):
        app_url = OSConf.get_app_url(self.app_name)
        gears = list()

        # Checking the output of gear dns script more times
        for i in range(1, 20):
            if self.test_variant == 'php':
                gear = common.fetch_page(str(app_url) + "/gear.php")
            if self.test_variant == 'perl':
                gear = common.fetch_page(str(app_url) + "/gear.pl")
            if self.test_variant in ('ruby', 'ruby-1.9'):
                gear = common.fetch_page(str(app_url) + "/gear.rb")
            if self.test_variant == 'python':
                gear = common.fetch_page(str(app_url) + "/gear.py")
            if self.test_variant in ('jbosseap', 'jbossas', 'jbossews', 'jbossews2'):
                if i==1:    time.sleep(60)
                gear = common.fetch_page(str(app_url) + "/gear.jsp")
            if self.test_variant == 'nodejs':
                gear = common.fetch_page(str(app_url) + "/gear.js")
            if gear not in gears:
                gears.append(gear)
        print "GEARS", gears
        return len(gears)

    def test_method(self):
        self.add_step(
            "Creating a non scalable %s application"%self.test_variant,
            common.create_app,
            function_parameters = [ self.app_name, 
                                    self.app_type, 
                                    self.user_email, 
                                    self.user_passwd, 
                                    True, 
                                    self.git_repo],
            expect_description = "The application must be created successfully",
            expect_return = 0)

        '''  
        self.add_step(
            "Scaling up via REST API",
            self.config.rest_api.app_scale_up,
            function_parameters = [ self.app_name ],
            expect_description = "The application must not scale-up successfully",
            expect_return = 'unprocessable_entity')
        '''

        self.add_step("Scaling up via REST API",
            common.scale_up,
            function_parameters = [self.app_name, self.domain_name],
            expect_description = "The application must not scale-up successfully",
            expect_return = 2)        

        '''
        self.add_step("Scaling up via REST API",
            self.config.rest_api.app_scale_up,
            function_parameters = [ self.app_name ],
            expect_description = "The application must not scale-up successfully",
            expect_return = 'unprocessable_entity')
        '''

        self.add_step("Scaling up via REST API",
            common.scale_up,
            function_parameters = [self.app_name, self.domain_name],
            expect_description = "The application must not scale-up successfully",
            expect_return = 2)
        '''
        self.add_step("Scaling down via REST API",
            self.config.rest_api.app_scale_down,
            function_parameters = [ self.app_name ],
            expect_description = "The application must not scale-down successfully",
            expect_return = 'unprocessable_entity')
        '''
        self.add_step("Scaling down via REST API",
            common.scale_down,
            function_parameters = [self.app_name, self.domain_name],
            expect_description = "The application must not scale-up successfully",
            expect_return = 2)
        '''
        self.add_step(
            "Embed with mysql",
            common.embed,
            function_parameters = [ self.app_name, 'add-%s'%common.cartridge_types['mysql']],
            expect_description = "The mysql must be embeded successfully",
            expect_return = 0)
        '''
        '''
        self.add_step(
            "Scaling up via REST API",
            self.config.rest_api.app_scale_up,
            function_parameters = [ self.app_name ],
            expect_description = "The application must not scale-up successfully",
            expect_return = 'unprocessable_entity')
        '''
        self.add_step("Scaling up via REST API",
            common.scale_up,
            function_parameters = [self.app_name, self.domain_name],
            expect_description = "The application must not scale-up successfully",
            expect_return = 2)


        # Checking web-page availability with refreshing
        for i in range(1,6):
            self.add_step("Checking web-page #%d" % ( i ),
                common.check_web_page_output,
                function_parameters = [ self.app_name ],
                expect_description = "The application must be available in the browser",
                expect_return = 0)

        self.add_step("Configuring the test application",
            #self.configure_scale_up_test_application,
            common.inject_app_index_with_env,
            function_parameters = [ self.git_repo, self.app_type],
            expect_description = "The application must be configured successfully",
            expect_return = 0)

        self.add_step("Checking the number of gears (REST API)",
            common.get_consumed_gears,
            expect_description = "The number of gears must be '1'",
            expect_return = 1)

        self.add_step("Checking the number of gears",
            common.get_num_of_gears_by_web,
            function_parameters = [self.app_name, self.app_type],
            expect_description = "The number of gears must be '1'",
            expect_return = 1)
        
        '''
        self.add_step("Scaling down via REST API",
            self.config.rest_api.app_scale_down,
            function_parameters = [ self.app_name ],
            expect_description = "The application must not scale-down successfully",
            expect_return = 'Unprocessable Entity')
        '''

        # Checking web-page availability with refreshing
        for i in range(1,6):
            self.add_step("Checking web-page #%d" % ( i ),
                common.check_web_page_output,
                function_parameters = [ self.app_name ],
                expect_description = "The application must be available in the browser",
                expect_return = 0)
        
        self.run_steps()
        return self.passed("%s passed" % self.__class__.__name__)


class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(NegativeScaling)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
