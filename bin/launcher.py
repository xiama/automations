#!/usr/bin/python
import os
import sys
import time
import platform
import socket
import shutil
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
testmodules_path = os.path.abspath(file_path + "/../testmodules")
sys.path.append(lib_path)
sys.path.append(lib_path + "/supports")
sys.path.append(testmodules_path)
from tcms import TCMS, TCMSException
from helper import *
import clog
import random
import database
import json
import OSConf

tcmsobj = None
DEBUG = True 
FROM_DB = False
RUNDIR = "%s/../workspace"%file_path
(OshiftUser, OshiftPasswd) = get_default_rhlogin()

def run_tests(testrun_id, tc_id_list=None, skip_tag_ids=None):
    final_testrun_cases = []
    if not FROM_DB:
        testrun_cases = tcmsobj.get_testcase_by_run_id(testrun_id)

        #get all testcaseruns for save time
        log.debug("Getting all case runs...")
        testcaserun_hash = dict()
        for caserun in tcmsobj.server.TestRun.get_test_case_runs(testrun_id):
            testcaserun_hash[caserun['case_id']] = caserun
        log.debug("Filtering Test Case ...")
        for i in testrun_cases:
            #case_run = tcmsobj.get_testcaserun(i['case_id'], testrun_id)
            if testcaserun_hash.has_key(i['case_id']):
                i['case_run_id'] = testcaserun_hash[i['case_id']]['case_run_id']
                i['case_run_status'] = testcaserun_hash[i['case_id']]['case_run_status']
            else:
                log.warning("SKIP: Unable to find case_run for case[%s]"%i['case_id'])
                continue

            if i['case_status'] != 'CONFIRMED' or int(i['is_automated']) != 1 or i['case_run_status'] != 'IDLE': 
                log.info("SKIP: Case %s in this run is not CONFIRMED, or AUTOMATED, or its status is not IDLE" %(i['case_id']))
            else:
                if tc_id_list != None and i['case_id'] not in tc_id_list:
                    log.info("SKIP: Case %s in not in your specified list - %s" %(i['case_id'], tc_id_list))
                else:
                    final_testrun_cases.append(i)

        if len(final_testrun_cases) == 0:
            log.info("No suitable test for testing!")
            return 0
        manual_run_tag_id = tcmsobj.get_tag_id('manual_run')
    else:
        ### HERE if we are using MySQL to get the testcases
        final_testrun_cases = []
        for tc_id in tc_id_list:
            testcase = database.get_testcase_by_id(tc_id)
            final_testrun_cases.append(testcase)
    # XXX put back in later
    debug("=" * 80)
    # First of all, will run 142463 case
    log.info("Job starts - Creating domain")
    debug("=" * 80)
    ret = exec_testmodule("RT.job_related.create_domain", rhtest_args=' -R -G ')
    if (ret != 0):
        log.error("Unable to create a domain - HALT.")
        sys.exit(254)
    #do random shuffle sort to avoid parallel conflicts
    random.shuffle(final_testrun_cases)
    if not FROM_DB:
        for tc in final_testrun_cases:
            debug("\n\n")
            debug("-" * 80)
            log.info("Running case#%s [%s...]" %(tc['case_id'], tc['summary'][:40]))
            debug("-" * 80)
            try:
                json_data = json.loads(tc['script'])
                script = json_data['python'].strip().split(".py")[0]
            except:
                print "Can't find script...trying again with .py format"
                print "Keep this case IDLE"
                #script = tc['script'].strip().split(".py")[0]
                continue

            cf_path = "%s/%s.%s" %(testmodules_path, script + ".conf", OshiftUser)
            module_name = ".".join(script.split("/"))
            if len(script.strip()) == 0 or len(module_name) == 0:
                log.info("WARNING: Undefined script in TCMS")
                continue
            if tc['arguments'] == '':
                tc['arguments'] = None

            content = """
tcms_arguments = %s
script = '%s'
tcms_testcase_id = %s
tcms_testrun_id = %s
tcms_testcaserun_id = %s
tcms_testrun_environment = '%s' 
""" %(tc['arguments'], tc['script'], tc['case_id'], testrun_id, tc['case_run_id'], '___TBD___')
            # Before running, check status again, set it for RUNNING status, also for parallel funcationaliy
            case_run = tcmsobj.get_testcaserun_by_id(tc['case_run_id'])
            if case_run['case_run_status'] == 'IDLE':
                #if a job needs to be run manually, because of e.g. long execution 
                #time or requires some user interaction, we will mark this case as 
                #PAUSED and it will be up to user to accomplish such task
                #https://hosted.englab.nay.redhat.com/issues/10569
                if manual_run_tag_id in tc['tag']:
                    tcmsobj.update_testcaserun_status(tc['case_run_id'], 'PAUSED')
                    continue
                to_skip = False
                for stag in skip_tag_ids:
                    if stag in tc['tag']:
                        to_skip = True
                        break
                if to_skip:
                    #tcmsobj.update_testcaserun_comments(tc['case_run_id'], 'SKIPPED/IGNORED by launcher.py --skip_tags ... or has "need_update_auto" tag')
                    tcmsobj.update_testcaserun_status(tc['case_run_id'], 'WAIVED')
                    continue

                tcmsobj.update_testcaserun_status(tc['case_run_id'], 'RUNNING')
                write_file(cf_path, content)
                exec_testmodule(module_name, tc, testrun_id)
            else:
                log.debug("Testcaserun - %s status is not IDLE now, skip it." %(tc['case_run_id']))
    else:
        ## user running w/o TCMS should always be creating new entry into DB and not reuse
        for tc in final_testrun_cases:
            debug("\n\n")
            debug("-" * 80)
            log.info("Running case#%s [%s...]" %(tc['case_id'], tc['summary'][:40]))
            debug("-" * 80)
            try:
                json_data = json.loads(tc['script'])
                script = json_data['python'].strip().split(".py")[0]
            except:
                print "Can't find script...trying again with .py format"
                print "Keep this case IDLE"
                #script = tc['script'].strip().split(".py")[0]
                continue

            cf_path = "%s/%s.%s" %(testmodules_path, script + ".conf", OshiftUser)
            module_name = ".".join(script.split("/"))
            if len(script.strip()) == 0 or len(module_name) == 0:
                log.info("WARNING: Undefined script in TCMS")
                continue
            if tc['arguments'] == '':
                tc['arguments'] = None

            content = """
tcms_arguments = %s
script = '%s'
mysql_db_testrun_id = '%s'
tcms_testcase_id = %s
tcms_testrun_environment = '%s' 
""" %(tc['arguments'], tc['script'], testrun_id, tc['case_id'], '___TBD___')
            # udpate testcase_run table
            caserun_res = database.update_testcaserun_status(testrun_id, tc['case_id'], 'RUNNING')
            write_file(cf_path, content)
            exec_testmodule(module_name, testrun_id)
            test_res = database.get_latest_test_result()
            if test_res.PassFail =='P':
                caserun_res = database.update_testcaserun_status(testrun_id, tc['case_id'], 'PASSED')
            elif test_res.PassFail =='F':
                caserun_res = database.update_testcaserun_status(testrun_id, tc['case_id'], 'FAILED')
            #caserun_res.status = test_case_status 
            print caserun_res[0]
  
    # XXX put this back later. 
    # In the end, will run 146352
    debug("=" * 80)
    log.debug("Job ends - Cleaning domain and app")
    debug("=" * 80)
    exec_testmodule("RT.job_related.apps_clean_up", rhtest_args=' -R -G ')
    if not FROM_DB:
        # Update the test run status to FINISHED        
        tcmsobj.update_testrun(testrun_id, {'status' : 1})
    else:
        # udpate the mysqld db for the testrun_tag
        database.update_testrun(testrun_id, {'status' :1})


def exec_testmodule(testname, tc_obj=None, testrun_id=None, rhtest_args=''):
    if tc_obj:
        tcms_run_details = ""
        case_run_id = tc_obj['case_run_id']
        case_id = tc_obj['case_id']
        tcms_run_details = ",".join([str(testrun_id), str(case_run_id), str(case_id)])
    else:
        case_run_id = None
        tcms_run_details = None

    instance_ip = get_instance_ip()
    log_file = "%s/curr_tc_log.%s"%(get_tmp_dir(), case_run_id)
    if os.getenv('RHTEST_ARGS'):
        rhtest_args += " "+os.getenv('RHTEST_ARGS')+" "
    if DEBUG:
        rhtest_args += " -d "
    shell_options=""
    if os.getenv("SHELL") == "/bin/bash":
        if platform.dist()[0] == 'Ubuntu':
            shell_options = " bash -c 'set -o pipefail';"
        else:
            shell_options = " set -o pipefail;"
    else:
        log.warning("Non BASH shell(%s). If possible use /bin/bash instead."%os.getenv("SHELL"))
    prev_dir = os.getcwd()
    os.chdir(RUNDIR)
    cmd = "%s %s/rhtest -i %s -x %s  %s %s 2>&1 | tee %s 2>&1;"%(shell_options,
                                                                 file_path, 
                                                                 instance_ip,
                                                                 tcms_run_details,
                                                                 rhtest_args,
                                                                 testname,
                                                                 log_file)
    log.debug(cmd)
    print "CMD: %s" % cmd
    try:
        ret = os.system(cmd)
    finally:
        os.chdir(prev_dir)
    #this is strange (probably because of pipefail)
    if (ret>255):
        ret = ret/256

    return ret


def create_test_run(testrun_tag, tc_id_list, testplan_id):
    """
    Create TCMS.TestRun according to tc_id_list.
    """
    timestamp = time.strftime("%Y_%m_%d-%H:%M:%S", time.localtime())
    test_run_summary = "%s [%s]" %(testrun_tag, timestamp)
    testrun_id = tcmsobj.create_testrun(test_run_summary, plan_id=testplan_id)['run_id']
    # create_domain - 142463; clean_up - 146352
    # This two cases must be added into new test run as the first one, and the last one.
    #update_test_run(testrun_id, [142463])
    update_test_run(testrun_id, tc_id_list) 
    #update_test_run(testrun_id, [146352])
    return testrun_id
    

def update_test_run(testrun_id, tc_id_list):
    """
    Update TCMS.TestRun according to tc_id_list.
    """
    if tc_id_list != None and isinstance(tc_id_list, list) and len(tc_id_list) != 0:
        tcmsobj.add_testcase_to_run(tc_id_list, testrun_id)
        return True
    else:
        print "only support list format for test cases"
        return False
    
def parse_cmdline():
    usage = """
usage: %s {Instance Arguments} {TCMS Arguments}
Instance Arguments: (-a ec2-xxx.compute-1.amazonaws.com) | ([-m devenv_xxx] [-n QE_devenv_xxx] [-z xxx])
TCMS     Arguments: (-t xxx (-c 'n, ..., m')|(-g 'xxx, ..., zzz') [-p xxx]) | (-i xxx [(-c 'n, ..., m')|(-g 'xxx, ..., zzz') -p xxx])
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.set_defaults(FROM_DB=False)
    parser.add_option("-d", "--debug", dest="DEBUG", action='store_true', help="Enable debug information")
    parser.add_option("-m", "--ami", dest="ami", help="Instance Arguments: Launch openshift instance from this ami.")
    parser.add_option("-n", "--instance_tag", dest="instance_tag", help="Instance Arguments: Instance tag for the newly launched instance")
    parser.add_option("-a", "--instance_ip", dest="instance_ip", help="Instance Arguments: Using this exsiting openshift instance for testing")
    parser.add_option("-A", "--instance_ip_by_tag", dest="instance_ip_by_tag", help="Instance Arguments: Using this existing openshift instance for testing defined by tag.")
    parser.add_option("-z", "--image_size", dest="image_size", default='m1.medium', help="Instance Arguments: Specify size for launching instance. By default it is m1.medium")
    parser.add_option("-t", "--testrun_tag", dest="testrun_tag", help="TCMS Arguments: Create new test run with this tag")
    parser.add_option("-i", "--testrun_id", dest="testrun_id", type=int, help="TCMS Arguments: Using this existing test run that you want to run.")
    parser.add_option("-c", "--testcase_ids", dest="testcase_ids", help="TCMS Arguments: A list of test case ids that you want to execute")
    parser.add_option("-g", "--testcase_tags", dest="testcase_tags", help="TCMS Arguments: A list of test case tags that you want to execute")
    parser.add_option("-p", "--testplan_id", dest="testplan_id", default=4962, type=int, help="TCMS Arguments: All test cases are selected from this test plan for creating/updating test run. By default it is 4962 - https://tcms.engineering.redhat.com/plan/4962/")
    parser.add_option("-s", "--skip_tags", dest="skip_tags", help="TCMS Arguments: A list of test case tags that you want to skip")
    parser.add_option("-r", "--client_version", dest="client_version", help="Arguments: version number of rhc client to use. If not defined, it will be used the last one")
    parser.add_option("-D", action="store_true", dest="FROM_DB", help="retrieve the testcase and tag information from MySQL database")

    return parser.parse_args()


def main():
    global tcmsobj
    global DEBUG

    (options, args) = parse_cmdline()

    try:
        os.makedirs(get_tmp_dir())
    #TODO: what about remove whole TMP_DIR?
    # it seems to be safe if it is within $HOME/tmp/
    except:
        pass
    
    shutil.rmtree(RUNDIR, True)
    os.makedirs(RUNDIR)
    try:
        # Remove OSConf cache
        os.remove(OSConf.get_cache_file())
        os.remove("%s/libra_server-%s"%(get_tmp_dir(), OshiftUser))
    except:
        pass
    '''
    if options.client_version:
        log.info("Setup rhc client to version: %s"%options.client_version)
        try:
            r = setup_rhc_client(options.client_version)
            #r = update_rhc_client(options.client_version)
            if r != 0:
                raise Exception("")
        except:
            log.error("Unable to setup RHC client to given version!")
            sys.exit(254)
    '''
    DEBUG = options.DEBUG
    if DEBUG:
        os.environ['RHTEST_DEBUG'] = '1'
    # Priority for Instance Arguments: -a -> -m
    if options.instance_ip != None:
        # This branch is when you want to use existing instance
        instance_ip = options.instance_ip
    elif options.instance_ip_by_tag is not None:
        # This branch is when you want to use previously 
        # launched/stopped instance
        try:
            if not options.instance_ip_by_tag.startswith('QE_'):
                log.warning("Appending QE_ prefix for given instance tag!")
                options.instance_ip_by_tag = 'QE_'+options.instance_ip_by_tag
            instance_ip = get_instance_ip_by_tag(options.instance_ip_by_tag)
            log.info("Found instance[%s] IP=%s"%(options.instance_ip_by_tag, instance_ip))
        except Exception as e:
            log.warning("Unable to get IP address from instance by tag: %s. (%s)"%
                        (options.instance_ip_by_tag, str(e)))
            log.warning("Instance doesn't exist!")
            log.warning("Therefoer a new instance is going to be launched.")
            try:
                instance_ip = create_node(options.instance_ip_by_tag, options.ami, options.image_size)
            except Exception as e:
                log.error("Unable to launch new instance with tag:%s. (%s)"%
                          (options.instance_ip_by_tag, str(e)))
                sys.exit(254)
    else:
        # This is when you want to launch new instance
        instance_ip = create_node(options.instance_tag, options.ami, options.image_size)

    testplan_id = options.testplan_id
    os.environ['OPENSHIFT_libra_server'] = instance_ip
    
    set_libra_server(instance_ip)
    #log.info("Platform: %s"%" ".join(platform.uname()))
    #log.info(cmd_get_status_output("rhc --version; python --version; ruby --version", quiet=True)[1])
    #log.info(aws_console.get_ami(get_instance_ip()))
    #try:
    #    log.info("Host: %s"%socket.gethostbyname(socket.gethostname()))
    #except:
    #    log.info("Host: %s"%socket.gethostname())
    #Do TCMS authentication only once

    tc_id_list = []
    tc_tag_list = []
    skip_tag_ids = []

    if not options.FROM_DB:
        tcmsobj = TCMS()
    else:
        global FROM_DB
        FROM_DB = options.FROM_DB

    if options.testcase_ids != None:
        tmp_list = options.testcase_ids.split(',')
        for i in tmp_list:
            tc_id_list.append(int(i.strip()))
    elif options.testcase_tags != None:
        tmp_list = options.testcase_tags.split(',')
        for i in tmp_list:
            tc_tag_list.append(i.strip())
            #print "--->", tc_tag_list

    # remove need_update_auto tag
    if options.skip_tags:
        options.skip_tags = "xxx,%s"%(options.skip_tags)
    else:
        options.skip_tags = "xxx"
    tags_to_skip = map(lambda x: x.strip(),options.skip_tags.split(','))
    log.debug("TAGS to skip:%s"%tags_to_skip)
    skip_tag_ids = tcmsobj.get_tag_id(tags_to_skip)


    # Priority for TCMS Arguments: -i -> -t
    # Priority for test case filter arguments: -c -> -g
    if options.testrun_id != None:
    # This branch is when you want to use existing test run
        test_run_id = options.testrun_id
        if not options.FROM_DB:
            log.info("Using existing TCMS Test Run - https://tcms.engineering.redhat.com/run/%s/" %(test_run_id))
        else:
            log.info("Not talking with TCMS...using MySQL db instead...")
        
        if len(tc_id_list) != 0:
            r = run_tests(test_run_id, tc_id_list, skip_tag_ids=skip_tag_ids)
        elif len(tc_tag_list) != 0:
            if not options.FROM_DB:
                tc_id_list = tcmsobj.get_testcase_id_list_by_tag(tc_tag_list, testplan_id)
            else:
                params = {'is_automated': 1, 'case_status': 'CONFIRMED'}
                tc_id_list = database.get_testcase_ids_by_tag(tc_tag_list, params)
            r = run_tests(test_run_id, tc_id_list, skip_tag_ids=skip_tag_ids)
        else:
            r = run_tests(test_run_id, skip_tag_ids=skip_tag_ids)
    elif options.testrun_tag != None:
    # This branch is when you want to create a new test run
        if len(tc_id_list) != 0:
            test_run_id = create_test_run(options.testrun_tag, tc_id_list, testplan_id)
            r = run_tests(test_run_id, skip_tag_ids=skip_tag_ids)
        elif len(tc_tag_list) != 0:
            if options.FROM_DB:
                # get tc_id_list from DB
                params = {'is_automated': 1, 'case_status': 'CONFIRMED'}
                # 1. create a testrun into row mysql db
                testrun_res = database.create_tcms_testrun()
                # 2. get test list from db
                tc_id_list = database.get_testcase_ids_by_tag(tc_tag_list, params)
                # 3. create testcase_run entries into db_res
                tc_run_id_list = []
                for tc_id in tc_id_list:
                    params = {'run': testrun_res.id, 'case_id': tc_id }
                    res = database.create_tcms_testcase_run(params)
                    tc_run_id_list.append(res.id) 

                # 4. update test_run db entry with the testcase list
                test_run_id = testrun_res.id 
                testrun_res.case_list = str(tc_run_id_list)
            else:
                tc_id_list = tcmsobj.get_testcase_id_list_by_tag(tc_tag_list, testplan_id)
                test_run_id = create_test_run(options.testrun_tag, tc_id_list, testplan_id)
            r = run_tests(test_run_id, tc_id_list, skip_tag_ids=skip_tag_ids)
        else:
            print usage
            raise Exception("Entry test case id list using option '-c' or test case tag list using option '-g'")
    else:
        print usage
        raise Exception("Enter existing TCMS test run id using option '-i' or create new TCMS test run using option '-t'")

    # Clean up everything under workspace/
    # we don't wanna clean it, because of later debugging 
    #os.system("rm -rf %s/../workspace/*" % (file_path))

    return r


def debug(msg):
    print >> sys.stderr, msg

if __name__ == "__main__":
    exit_code=main()
    sys.exit(exit_code)
