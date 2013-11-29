#!/usr/bin/env python

import sys, os
import time
import storage
from optparse import OptionParser
import database
import commands
import random
import platform
import socket 

#### homegrown python modules
import timelib
import tcms_base
#from tcms_base import *
import pscp
import aws_console
import shutil
import tcms
import openshift
import rhtest
from helper import cmd_get_status_output

def config_parser():
    """ parses options and such  """
    parser = OptionParser()
    parser.set_defaults(VERBOSE=True)
    parser.set_defaults(DEBUG=False)
    parser.set_defaults(RECORD=True)
    parser.set_defaults(GLOBAL_RECORD=True)
    parser.set_defaults(TCMS=False)
    parser.add_option("-a", "--ami_id", help="ami_id or devenv label as base of instance to be created")
    parser.add_option("-b", "--instance_name", default=None, help="new instance's name")
    parser.add_option("-i", "--instance_ip", help="dev instance IP")
    parser.add_option("-j", "--json_file", help="path to the json formated file that contains the script name")
    parser.add_option("-l", "--tag", help="TCMS testcase tags to run")
    parser.add_option("-m", "--run_mode", default='DEV', help="PROD|STG|DEV")
    parser.add_option("-n", "--notes", default=None, help="User notes about this run")
    parser.add_option("-x", "--tcms_run_details", default=None, help="TCMS test run details taken from launcher.py")
    # useful options for development
    parser.add_option("-d", action="store_true", dest="DEBUG", help="enable DEBUG (default true)")
    parser.add_option('-R', action="store_false", dest="RECORD", help="Enable storing to results database")
    parser.add_option('-G', action="store_false", dest="GLOBAL_RECORD", help="Enable storing to global storage (default True)")
    parser.add_option("-T", action="store_true", dest="TCMS", help="Enable storing to TCMS database")
    parser.add_option("-s", action="store_true", dest="START_SERVER", help="start an devenv instance automatically by default")
    parser.add_option("-t", dest="testcase_id", help="Test Case ID")
    (options, args) = parser.parse_args()
    
    
    print "*"*80
    print args
    print "*"*80
    return (options, args)


class TestRunner(object):
    def __init__(self, config):
        self._config = config
        self.lasturl = None
        rdb = config.get("resultsdirbase", "/var/tmp")
        config.resultsdir = rdb # default when not running a test.

    def get_config(self):
        return self._config
    
    def initialize(self):
        runtime_config(self._config)
        self._config.resultsfiles = []


    def __call__(self, argv):
        """
        this function is called whenever an instance object is called.
        ex. tr = TestRunner(cf); 
        """
        cf = self._config
        self.initialize()
        (options, args) = config_parser()
        cf['options'] = options
        cf['args'] = args
        
        if options.tag:
            cf['tcms_tag'] = options.tag

        # XXX perhaps save the arguemnts for future use??
        
        # get the os.envirn variables and save it into cf 
        cf.OPENSHIFT_http_proxy = os.getenv('OPENSHIFT_http_proxy')
        cf.OPENSHIFT_user_email = os.getenv('OPENSHIFT_user_email')
        cf.OPENSHIFT_user_passwd =  os.getenv('OPENSHIFT_user_passwd')
        cf.argv = args
        cf.arguments = [os.path.basename(argv[0])] + argv[1:]
        return self.run_modules(cf.argv)

    def get_module(self, name):
        if sys.modules.has_key(name):
            return sys.modules[name]
        mod = __import__(name)

        try:
            mod = __import__(name)
            components = name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
        except ImportError:
            print >>sys.stderr, "*** Import error in test module %s " % (name,)
            return None
        else:
            return mod
       
    def run_module(self, mod):
  
        cf = self._config
        userinterface = storage.get_ui(cf)
        cf['userinterface'] = userinterface

        # ui = self._config.userinterface
        user_name = commands.getoutput('whoami')
        cf['user'] = user_name
        output = commands.getoutput("groups %s" % user_name)
        user_group = output.split(':')[0].strip()
        cf.USERGROUP = user_group
        if type(mod) is str:
            mod = self.get_module(mod)
            # find out what type of test this is.  if UI, then we need to instantiate
            # a AutoWeb instance
            cf['mod_type'] = mod.__name__.split('.')[0]

        if cf.options.tag:
            # user wants to run a collection of test (a testsuite, instantiate 
            # a TCMS object, which will be used to add_test()
            cf['tcms_obj'] = tcms_base.TCMS()

        if mod:
            cf.reportbasename = mod.__name__.replace(".", "_")
            cf.logbasename = "%s.log" % (cf.reportbasename,)
            cf['logfile'] = storage.get_logfile(cf)
            # merge any test-module specific configuration files
            modconf = os.path.join(os.path.dirname(mod.__file__), "%s.conf" % (mod.__name__.split(".")[-1],))
            user_modconf = modconf + "." + cf.OPENSHIFT_user_email
            if os.path.exists(user_modconf):
                execfile(user_modconf, cf.__dict__)
            elif os.path.exists(modconf):
                execfile(modconf, cf.__dict__)


            try:
                print "tcms_testcaserun_id: %s" %(cf.tcms_testcaserun_id)
                if os.environ.has_key("OPENSHIFT_tcms_testcaserun_id"):
                    cf.tcms_testcaserun_id = os.environ['OPENSHIFT_tcms_testcaserun_id']
            except:
                 #if rhtest is run manually from command line without launcher, which should put this into the .conf file
                cf.tcms_testcaserun_id = None
                #print "WARN: None tcms_testcaserun_id info!!!"


            if cf.tcms_testcaserun_id != None:
                import tcms
                cf['tcms_obj'] = tcms.TCMS()
            else:
                cf['tcms_obj'] = None


            starttime = timelib.now()
            cf.results_year_month_dir = os.path.join(cf.resultsdirbase, "%s" % (timelib.strftime("%Y%m/%d/")))
            # first make the YYYYMM top directory
            try:
                os.system("sudo mkdir -p %s" % (cf.results_year_month_dir))
                os.system("sudo find %s -type d -exec chmod 777 {} \;" % (cf.resultsdirbase))
            except OSError, errno:
                if errno[0] == EEXIST:
                    pass
                else:
                    raise

            rand_num = random.randint(0, 5000)
            # now make the actual test directory, added rand_num to make it more unique
            cf.resultsdir = os.path.join(
                 cf.results_year_month_dir,
                 "%s-%s-%s" % (cf.reportbasename, rand_num, timelib.strftime("%Y%m%d%H%M%S", timelib.localtime(starttime)))
            )
            try:
                os.system("sudo mkdir -p %s" % (cf.resultsdir))
                os.system("sudo find %s -type d -exec chmod 777 {} \;" % (cf.resultsdirbase))
            except OSError, errno:
                if errno[0] == EEXIST:
                    pass
                else:
                    raise

            rpt = storage.get_report(cf)
            cf['report'] = rpt
            cf['logfilename'] = storage.get_logfilename(cf)
            cf.reportfilenames = rpt.filenames # Report file's names. save for future use.
            rpt.initialize()
            rpt.logfile(cf.logfilename)
            rpt.add_title("Test Results for module %r." % (mod.__name__, ))
            rpt.add_message("ARGUMENTS", " ".join(cf.arguments))
            # get the build version  XXX git of the test itself or the dev
            # number?
            version_file = None #build_version
            self.rpt = rpt # new report object.
            try:
                vf = open(version_file)
                build_info = vf.readlines()[0].strip()  # Should be the first line
                rpt.add_message("BUILD_INFO", build_info)
            except:
                #self.info("Error: Can't open %s!" % version_file)
                pass
            # insert the _ID if it exists.
            try:    
                rpt.add_message("File ID", mod._ID)
            except:
                rpt.add_message("File ID", 'Missing')

            rpt.add_message("Platform", " ".join(platform.uname()))
            try:
                rpt.add_message("Host", socket.gethostbyname(socket.gethostname()))
            except:
                rpt.add_message("Host", socket.gethostname())
            rpt.add_message("RHC client version", cmd_get_status_output("rhc --version", quiet=True)[1])
            rpt.add_message("Python version", cmd_get_status_output("python --version", quiet=True)[1])
            rpt.add_message("Ruby version", cmd_get_status_output("ruby --version", quiet=True)[1])


            note = cf.options.notes
            if note:
                rpt.add_message("NOTE", note)
                self._config.comment = note
            else:
                self._config.comment = None
            self.lasturl = url = self._reporturl(rpt)
            self._config['results_url'] = url
            rpt.add_message("MODULESTART", timelib.strftime("%a, %d %b %Y %H:%M:%S %Z", timelib.localtime(starttime)))

            suite = mod.get_suite(cf)
            self.test_name = self._config.test_name
            ui = cf.userinterface
            aws = aws_console.AWS_Console()
            ami_info = None
            # get ami, and image label information
            if not cf.options.instance_ip:
                ui.info("No instance IP specified, starting new DEV instance...")
                image_dict = aws.get_all_devenv_images()
                target_image = image_dict[max(sorted(image_dict))]
                image_name = target_image.name.split('/')[1]

                ui.info("User did not specify an ami or devenv name, using the latest '%s':'%s'" % (image_name, target_image.id))
                rpt.info("User did not specify an ami or devenv name, using the latest '%s':'%s'" % (image_name, target_image.id))
                if cf.options.instance_name is None:
                    import uuid
                    cf.options.instance_name = "QE_%s_%s" %(image_name, uuid.uuid1().hex[:6])
                
                node =aws.create_node(cf.options.instance_name, target_image, 'm1.medium')
                cf['node'] = node  # save it for later reference if need be.
                instance_ip = node.public_ip[0]
                ami_id = node.extra['imageId']
            else:
                instance_ip = cf.options.instance_ip
                """
                if (instance_ip == 'localhost') or (instance_ip == '127.0.0.1'):
                    ### live CD 
                    cf['live_cd'] = True
                    build_info = 'live_cd'
                    ami_id = build_info
                    build_version = build_info

                else:
                    cf['live_cd'] = False
                    ui.info("Getting ami id for '%s'" % instance_ip)
                    if instance_ip == 'stg.openshift.redhat.com':
                        ami_info = database.get_stg_ami()
                        ami_id = ami_info.ami_id
                        build_version = ami_info.build_version
                    else:
                        ami_id = aws_console.get_ami(instance_ip)
                """
            """
            #ami_id = 'ami-1ef82a77'
            ami_info = None
            if ami_info is None:
                try:
                    # first query to db to find the build information.
                    ami_info = database.get_ami_info(ami_id)
                    build_version = ami_info.build_version
                    ui.info("Found AMI information '%s' matching '%s'" % (ami_id, build_version))
                except:
                    try:
                        ui.error("Can't find AMI information from mysql database, trying aws console...")
                        image = aws.get_image(ami_id)
                        build_version = image.name.split('/')[1]
                    except:
                        build_version = 'Unknown'
                        ui.error("Can't find AMI information, putting in '%s'" % build_version)
            """
            ami_id = 'Unknown'
            build_version = 'Unknown'
            instance_info = {}
            instance_info['ami_id'] = ami_id
            try:
                rpt.add_message("AMI ID", aws_console.get_ami(instance_ip))
            except:
                rpt.add_message("AMI ID", ami_id)
            instance_info['build_version'] = build_version
            instance_info['ip'] = instance_ip
            cf['instance_info'] = instance_info
            cf['logger'] = rhtest.RhTestLogger(cf.userinterface, cf.report)
            rest = openshift.Openshift(host=instance_ip,
                    user=cf.OPENSHIFT_user_email,
                    passwd=cf.OPENSHIFT_user_passwd,
                    logger=cf.logger)
            cf['rest_api'] = rest  # get a rest handle for the instance

            if cf.mod_type == 'UI':
                import autoweb
                cf['web'] = autoweb.AutoWeb(ip=cf.instance_info['ip'], proxy=cf.proxy, config=cf)
            # user sepecified to record result into TCMS
            if cf.options.TCMS:
                if not cf.has_key('tcms_obj'):
                    tcms = tcms_base.TCMS()
                    cf['tcms_obj'] = tcms
                else:
                    if cf.tcms_obj is None:
                        cf.tcms_obj = tcms_base.TCMS()
                        tcms = cf.tcms_obj            
                tcms = cf.tcms_obj
                # get the build id from TCMS
                build_version = cf.instance_info['build_version']
                if cf.options.notes:
                    summary = cf.options.notes
                else:
                    timestamp = time.strftime("%Y_%m_%d-%H:%M:%S", time.localtime())
                    if cf.options.tag:
                        run_tag = cf.options.tag
                    else:
                        run_tag = cf.test_name

                    summary = "_".join([timestamp, run_tag])
                #tcms.check_and_insert_build(cf.instance_info['build_version'])
                #res = tcms.get_testcase_id_by_script_name(mod.__name__)
                tests = suite.get_tests()
 
                if tests[0].inst.__module__ == 'Collections.RunTests':
                    # If the module is called Collections.RunTests, then skip it
                    # because that is just a 
                    tests = tests[1:]
                
                testcase_ids, testcases_dict = tcms.get_testcase_ids(tests)
                cf.testcases = testcases_dict  # save it for reference later
                # create testcases_variants dictionary
                cf.testcase_variants_map = tcms.get_variants_mapping(testcase_ids) 
                #self.info("xxx", 1)
                res = tcms.create_testrun(testcase_ids, build_version, summary)
                    #res = tcms.create_testrun_from_script(mod.__name__,
                    #        build_version)
                    # XXX hardcode this during developement 
                    #res = [{'case': 'demo-1', 'build_id': 1770, 'tested_by_id': None, 'environment_id': 0, 'run': 'TestRun create via XML-RPC', 'run_id': 33116, 'notes': '', 'sortkey': None, 'running_date': None, 'assignee': None, 'build': 'unspecified', 'case_id': 128833, 'is_current': False, 'case_run_status': 'IDLE', 'assignee_id': None, 'case_run_id': 849475, 'tested_by': None, 'case_text_version': 1, 'case_run_status_id': 1, 'close_date': None}]
                cf['testrun_res'] = res
                ui.info("TCMS testrun created, case_id: %s, run_id: %s"  % (res[0]['case_run_id'], res[0]['run_id']))
                ui.info("Running a total of %s tests"  % (len(testcase_ids)))
                rpt.info("TCMS testrun created, case_id: %s, run_id: %s"  % (res[0]['case_run_id'], res[0]['run_id']))
                rpt.info("Running a total of %s tests"  % (len(testcase_ids)))
                # get the testcase id from TCMS based on the script name.

            rv = suite()  # just run instance of the suite
            suite_total_run_time = "%.2f seconds" % cf.total_time
            rpt.add_message("SUITETIME", suite_total_run_time)
            rpt.add_message("MODULEEND", timelib.localtimestamp())
            rpt.finalize()

            # lastly, run the module-level finalize function.
            if hasattr(mod, "finalize") and callable(mod.finalize):
                if cf.options.DEBUG:
                    try:
                        mod.finalize(cf)
                    except:
                        ex, val, tb = sys.exc_info()
                        import debugger
                        debugger.post_mortem(ex, val, tb)
                else:
                    mod.finalize(cf)
            if cf.has_key('node'):
                ui.info("Terminating node...")
                aws.stop_node(cf.node.name)

            #close browser window
            if cf.mod_type == 'UI':
                try:
                    cf['web'].driver.close()
                except:
                    pass

            # force close of report and logfile between modules
            lfname = cf.logfile.name
            cf.logfile.flush()
            cf.logfile.close()
            del cf.report ; del cf.logfile
            # 
            if cf.options.RECORD:
                # scp the log directory to the master central machine
                myscp = pscp.Pscp(host=cf.HOST, user='root')
                src = cf.resultsdir
                dst = os.path.dirname(cf.resultsdir)
                myscp.copy_to(src, dst)
                # the results are then cp over to the mount drive, so now we have two copies of the HTML log
                if cf.options.GLOBAL_RECORD:
                    remote_dst = os.path.dirname(cf.global_logs_basepath + src.split('/var/www/html')[1])
                    #print '##############'
                    #print "SRC: %s" % src
                    #print "DST: %s" % remote_dst
                    myscp.copy_to_global_location(src, remote_dst)
                    #myscp.copy_to_global_location(src, remote_dst+'/')

            else:
                print "Log files not copied to remote host to save disk space!"

            if (cf.options.DEBUG and cf.options.VERBOSE):
                # now put log file in results dir
                shutil.copy(lfname, cf.resultsdir)


            # tell user where to look for files
            ui = cf.userinterface
            if cf.options.RECORD:
                ui.Print("Results location: %s" % (url,))
                if cf.options.GLOBAL_RECORD:
                    global_results_url = cf.global_logs_baseurl + src.split('/var/www/html')[1]
                    ui.Print("Results location: %s" % (global_results_url,))
            else:
                ui.Print("Results location: %s" % (cf.resultsdir))

            #if (cf.options.TCMS):
            #self.update_loglink(cf.resultsdir, cf.options.testcase_id) #always do update

            # Adding comments to TCMS in the end of testing
            if cf.tcms_testcaserun_id != None:
                if cf.options.RECORD:
                    if cf.options.GLOBAL_RECORD:
                        comments = global_results_url
                    else:
                        comments = url
                    try:
                        cf['tcms_obj'].update_testcaserun_comments(cf.tcms_testcaserun_id, comments)
                        cf['tcms_obj'].update_testcaserun_testlog(cf.tcms_testcaserun_id, "Logs", comments)
                    except Exception as e:
                        print "ERROR: Unable to update comments: %s"%str(e)
                else:
                    print "No log file is saved"

            """
            if cf.flags.has_key('EMAIL'):
                # email the results back to whomever started the test.
                if cf.get('cc'):
                    recipients = cf.cc.split(",")
                else:
                    recipients = None
                print "cc: %s " % recipients
                e_rpt = reports.Email.EmailReport("text/plain", recipients)
                e_rpt.initialize()
                e_rpt.add_title("Test result notification")
                e_rpt.info(url)
                e_rpt.finalize()
            else:
                print ("Results not emailed out") 
            """
            return rv

    def update_loglink(self, loglink, testcase_id):
        ### HARDCODED  - THIS IS TEMPORARY - 
        loglink = '/'.join(["http://10.14.16.138",  loglink.split("/var/www/html/")[1]])
        case_run_id = self._config.tcms_testcaserun_id
        if case_run_id is None:
            print "ERROR: Missing tcms_testrun_id for updating testcaserun"
            return
        try:
            #if os.getenv('OPENSHIFT_variant_testcase') == "True":
            #    loglink = os.environ['OPENSHIFT_test_name'] + "-: " + loglink
            tcms_object = tcms.TCMS()
            #testrun_id = os.environ['OPENSHIFT_tcms_testrun_id']
            #testcaserun = tcms_object.get_testcaserun(testcase_id, testrun_id)
            #testcaserun = os.environ['OPENSHIFT_tcms_testcaserun_id']]
            
            #old_loglinks = testcaserun['notes']
            #if old_loglinks:
            #    loglink += "  %s" % old_loglinks
            tcms_object.update_testcaserun(case_run_id, {'notes':loglink})
        except Exception as e:
            print "ERROR: Failed to update log link for test case run:%s"%(str(e))

    def _reporturl(self, rpt):
        cf = self._config
        baseurl = cf.get("baseurl")
        documentroot = cf.get("documentroot")
        resultsdir = cf.resultsdir
        if baseurl and documentroot:
            url = baseurl+resultsdir[len(documentroot):]
            rpt.add_url("TESTRESULTS", url)
            return url
        else:
            rpt.add_message("RESULTSDIR", resultsdir)
            return resultsdir


    def run_modules(self, modlist):
        """run_modules(modlist)
    Runs the run_module() function on the supplied list of modules (or module
    names).  
        """
        self._config['modlist'] = modlist
        rv =0
        for mod in modlist:
            rv += self.run_module(mod)
            # give things time to "settle" from previous suite. Some spawned
            # processes may delay exiting and hold open TCP ports, etc.
            time.sleep(2) 
        return rv
        
def runtime_config(cf):
    """
    connects to the database based on cf.DBURI, if the option --dburi is given
    then try to connect to the database specified by that command line option.
    Otherwise, use the default setting, which is 'localhost'
   
    """
    if 'DBURI' in os.environ.keys():
        cf.DBURI = os.environ['DBURI']
    hostname = cf.get('DBURI')
    ##### 
    if hostname is not None:
        dburi = 'mysql://ruser:lab@%s/%s' % (hostname, cf.TESTRESULTS_DBURI)
        cf.DBURI = dburi
    database.connect2db(cf.DBURI)


def get_testrunner(argv=None):
    global __testrunner
    #if __testrunner:
    __testrunner = TestRunner(argv or sys.argv)
    return __testrunner

def delete_testrunner():
    global __testrunner
    __testrunner = None

def runtest(argv):
    cf = storage.get_config()
    tr = TestRunner(cf)
    return tr(argv)


if __name__ == '__main__':
    runtest(sys.argv)

