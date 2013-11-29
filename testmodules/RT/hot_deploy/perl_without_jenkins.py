#!/usr/bin/python

"""
Attila Nagy
Sept 26, 2012


"""
import rhtest
import common
from hot_deploy_test import HotDeployTest

class PerlHotDeployWithoutJenkins(HotDeployTest):
    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_name = common.getRandomString()
        self.config.application_type = common.app_types['perl']
        self.config.scalable = False
        self.config.jenkins_is_needed = False
        self.config.summary = "[US2309] Hot deployment support for non-scaling Perl app - without Jenkins"
        
    def configuration(self):
        self.log_info("Creating the application to check PID")
        self.config.file_name = "pid.pl"
        self.info("Editing file '%s'..." % self.config.file_name)
        perl_file = open("./%s/perl/%s" % (self.config.application_name, self.config.file_name), "w")
        perl_file.write('#!/usr/bin/perl\n')
        perl_file.write('print "Content-type: text/plain\\r\\n\\r\\n";\n')
        perl_file.write('open FILE, "<" . $ENV{"OPENSHIFT_HOMEDIR"} . "/%s/run/httpd.pid" or die "Cannot open the file";\n' % self.config.application_type)
        perl_file.write('while ( <FILE> ) { print };')
        perl_file.close()
        self.deploy()
        
class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(PerlHotDeployWithoutJenkins)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
