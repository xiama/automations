#!/usr/bin/python
import os
import sys
import time
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
testmodules_path = os.path.abspath(file_path + "/../testmodules")
sys.path.append(lib_path)
sys.path.append(testmodules_path)
from tcms import TCMS
import common
import Queue

q = Queue.Queue()
q2 = Queue.Queue()

COUNTER=0
PARALLEL_MODE=False

tcmsobj = None

    
def run_tests(testrun_id, tc_id_list=None):
    testrun_cases = tcmsobj.get_testcase_from_run(testrun_id)
    final_testrun_cases = []

    print "Filtering Test Case ..."
    for i in testrun_cases:
        testcaserun = tcmsobj.get_testcaserun(i['case_id'],testrun_id)
        i['testcaserun_id'] = testcaserun['case_run_id']
        #print "-"*5
        #print i
        #print testcaserun
        #print "-"*5
        if i['case_status'] != 'CONFIRMED' or i['is_automated'] != 1 or testcaserun['case_run_status'] != 'IDLE': 
            print "Case %s in this test run is not confirmed, or automated, or its status is not idled, skipping it" %(i['case_id'])
        else:
            if tc_id_list != None and i['case_id'] not in tc_id_list:
                #print type(i['case_id'])
                print "Case %s in not in your specified list - %s, skipping it" %(i['case_id'], tc_id_list)
            else:
                final_testrun_cases.append(i)

    if len(final_testrun_cases) == 0:
        print "No suitable test for testing !!!"
        return

    # First of all, will run 142463 case
    #print "=" * 20
    #print "Job starts - Creating domain"
    #print "=" * 20
    queue_cmd("RT.job_related.create_domain")

    for tc in final_testrun_cases:
        print "-" * 10
        print "Enqueining test case - %s" %(tc['case_id'])
        print "-" * 10
        #print tc
        #print "-" * 5
        script = tc['script'].split(".py")[0]
        #print "----->", script
        cf_path = "%s/%s.%s" %(testmodules_path, script + ".conf", os.environ['OPENSHIFT_user_email'])
        #print "----->", cf_path
        module_name = ".".join(script.split("/"))
        if tc['arguments'] == '':
            tc['arguments'] = None
        content = """
tcms_arguments = %s
script = '%s'
tcms_testcase_id = %s
tcms_testrun_id = %s
tcms_testcaserun_id = %s
""" %(tc['arguments'], tc['script'], tc['case_id'], testrun_id, tc['testcaserun_id'])

        # Before running, check status again, set it for RUNNING status, also for parallel funcationaliy
        case_run = tcmsobj.get_testcaserun_by_id(tc['testcaserun_id'])
        if case_run['case_run_status'] == 'IDLE':
            #tcmsobj.update_testcaserun_status(tc['testcaserun_id'], 'RUNNING')
            common.write_file(cf_path, content)
            queue_cmd(module_name, {'testcaserun_id' : tc['testcaserun_id']})
        else:
            print "Testcaserun - %s status is not IDLE now, skip it." %(tc['testcaserun_id'])

    # In the end, will run 146352
    print "=" * 20
    print "Job ends - Cleaning domain and app"
    print "=" * 20
    queue_cmd("RT.job_related.apps_clean_up")
    queue_cmd("RT.job_related.apps_clean_up")   #we need this also for the second thread
    #
    # Let's run the queues
    #
    if PARALLEL_MODE == True:
        #we have to put the last to other queue for cleaning...
        run_queues_in_parallel()
    else:
        run_queues_in_sequence()

    # Update the test run status to FINISHED        
    tcmsobj.update_testrun(testrun_id, {'status' : 1})


def create_test_run(testrun_tag, tc_id_list):
    """
    Create TCMS.TestRun according to tc_id_list or tc_tag_list.
    """
    timestamp = time.strftime("%Y_%m_%d-%H:%M:%S", time.localtime())
    test_run_summary = "Openshift-%s-%s" %(testrun_tag, timestamp)
    testrun_id = tcmsobj.create_testrun(test_run_summary)['run_id']
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
    
    
 
def get_email(id=None):
    if id is None:
        return os.getenv("OPENSHIFT_user_email")

    if not os.environ.has_key("OPENSHIFT_user_email2"):
        print "WARN: Missing OPENSHIFT_user_email2, using generated one istead."
        return os.getenv("OPENSHIFT_user_email").replace('@','%s@'%str(id))
    else:
        os.getenv("OPENSHIFT_user_email2")

def main():
    global tcmsobj
    global PARALLEL_MODE

    usage = """
usage: %s {Instance Arguments} {TCMS Arguments}
Instance Arguments: (-a ec2-xxx.compute-1.amazonaws.com) | ([-m devenv_xxx] [-n QE_devenv_xxx] [-z xxx])
TCMS     Arguments: (-t xxx (-c 'n, ..., m')|(-g 'xxx, ..., zzz') [-p xxx]) | (-i xxx [(-c 'n, ..., m')|(-g 'xxx, ..., zzz') -p xxx])
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--ami", dest="ami", help="Instance Arguments: Launch openshift instance from this ami.")
    parser.add_option("-n", "--instance_tag", dest="instance_tag", help="Instance Arguments: Instance tag for the newly launched instance")
    parser.add_option("-a", "--instance_ip", dest="instance_ip", help="Instance Arguments: Using this exsiting openshift instance for testing")
    parser.add_option("-z", "--image_size", dest="image_size", default='m1.medium', help="Instance Arguments: Specify size for launching instance. By default it is m1.medium")
    parser.add_option("-t", "--testrun_tag", dest="testrun_tag", help="TCMS Arguments: Create new test run with this tag")
    parser.add_option("-i", "--testrun_id", dest="testrun_id", type=int, help="TCMS Arguments: Using this existing test run that you want to run.")
    parser.add_option("-c", "--testcase_ids", dest="testcase_ids", help="TCMS Arguments: A list of test case ids that you want to execute")
    parser.add_option("-g", "--testcase_tags", dest="testcase_tags", help="TCMS Arguments: A list of test case tags that you want to execute")
    parser.add_option("-p", "--testplan_id", dest="testplan_id", default=4962, type=int, help="TCMS Arguments: All test cases are selected from this test plan for creating/updating test run. By default it is 4962 - https://tcms.engineering.redhat.com/plan/4962/")
    parser.add_option("-P", "--parallel", dest="parallel", action="store_true", help="Run in parallel mode. (by two different users)")

    (options, args) = parser.parse_args()
    #print "-->", options
    #print "-->", args

    # Priority for Instance Arguments: -a -> -m
    if options.instance_ip != None:                       
    # This branch is when you want to use existing instance
        instance_ip = options.instance_ip
    elif options.ami != None:
    # This is when you want to launch new instance
        instance_ip = common.create_node(options.instance_tag, options.ami, options.image_size)
    else:
        print "Warnning: No specified ami, will launch the latest one"
        instance_ip = common.create_node(options.instance_tag, None, options.image_size)

    os.environ['OPENSHIFT_libra_server'] = instance_ip
    common.set_libra_server(instance_ip)


    #Do TCMS authentication only once
    tcmsobj = TCMS()
    #print tcmsobj.server.TestCase.get_tags(141096)
    tc_id_list = []
    tc_tag_list = []
    if options.testcase_ids != None:
        tmp_list = options.testcase_ids.split(',')
        for i in tmp_list:
            tc_id_list.append(int(i.strip()))
    elif options.testcase_tags != None:
        tmp_list = options.testcase_tags.split(',')
        for i in tmp_list:
            tc_tag_list.append(i.strip())
            #print "--->", tc_tag_list

    if options.parallel:
        print "INFO: Parallel mode...\n"
        PARALLEL_MODE = True
    else:
        print "INFO: Normal mode...\n"


    # Priority for TCMS Arguments: -i -> -t
    # Priority for test case filter arguments: -c -> -g
    if options.testrun_id != None:
    # This branch is when you want to use existing test run
        test_run_id = options.testrun_id
        print "Using existing TCMS Test Run - https://tcms.engineering.redhat.com/run/%s/" %(test_run_id)
        if len(tc_id_list) != 0:
            run_tests(test_run_id, tc_id_list)
        elif len(tc_tag_list) != 0:
            tc_id_list = tcmsobj.get_testcase_id_list_by_tag(tc_tag_lis)
            run_tests(test_run_id, tc_id_list)
        else:
            run_tests(test_run_id)
    elif options.testrun_tag != None:                        
    # This branch is when you want to create a new test run
        if len(tc_id_list) != 0:
            test_run_id = create_test_run(options.testrun_tag, tc_id_list)
            run_tests(test_run_id)
        elif len(tc_tag_list) != 0:
            tc_id_list = tcmsobj.get_testcase_id_list_by_tag(tc_tag_list)
            test_run_id = create_test_run(options.testrun_tag, tc_id_list)
            run_tests(test_run_id)
        else:
            print usage
            raise common.InputError("Entry test case id list using option '-c' or test case tag list using option '-g'")
    else:
        print usage
        raise common.InputError("Enter existing TCMS test run id using option '-i' or create new TCMS test run using option '-t'")


def run_queues_in_sequence():
    while not q.empty():
        (cmd, args) = q.get()
        tcmsobj.update_testcaserun_status(args['testcaserun_id'], 'RUNNING')
        os.system(cmd)
    
def run_queues_in_parallel():
    print "INFO: Time for lunch? Let's Fork()..."
    i=0 #counter
    #let's fork...
    child_pid = os.fork()
    os.system("rm -f Q*.log")
    if child_pid == 0:
        print "Child Process: PID# %s" % os.getpid()
        q2_account = get_email(2)
        log_file="/tmp/curr_tc_log-%s"%q2_account

        qsize=q2.qsize()
        domain=common.getRandomString(12)
        while not q2.empty():
            #update counter...
            i=i+1
            (cmd, args) = q2.get()
            tcmsobj.update_testcaserun_status(args['testcaserun_id'], 'RUNNING')
            print '\033[93m',"\n[%d/%d]*********************Q2************************\n"%(i, qsize), cmd, '\033[0m'

            os.environ['OPENSHIFT_user_email']=q2_account
            if os.environ.has_key('OPENSHIFT_user_passwd2'):  #let's change passwrd as well
                os.environ['OPENSHIFT_user_passwd'] = os.environ['OPENSHIFT_user_passwd2']

            cmd = "rm -rf Q2;mkdir -p Q2;cd Q2; " +cmd+ " 2>&1 | tee -a ../Q2.log"
            ret = os.system(cmd)

            #if (ret==255 and i==1):
            #    print "Aborted -- Initialization failed."
            #    sys.exit(ret)


        print '\033[93m',"\n*********************Q2's END************************\n", '\033[0m'

    else:
        print "Parent Process: PID# %s" % os.getpid()
        q1_account = get_email()
        log_file="/tmp/curr_tc_log-%s"%q1_account
        qsize=q.qsize()
        while not q.empty():
            #update counter...
            i=i+1
            (cmd, tc) = q.get()
            print '\033[94m',"\n[%d/%d]********************Q1****************************\n"%(i,qsize), cmd, '\033[0m'
 
            os.environ['OPENSHIFT_user_email']=q1_account
            cmd = "rm -rf Q1;mkdir -p Q1;cd Q1; " +cmd+" 2>&1  |tee -a ../Q1.log"
            ret = os.system(cmd)

            #if (ret==255 and i==0):
            #    print "Aborted -- Initialization failed."
            #    sys.exit(ret)


        print '\033[94m',"\n*********************Q1's END************************\n", 
        print "Waiting for child to end..."
        os.waitpid(child_pid, 0) # make sure the child process gets cleaned up
        print "Done. Updating testrun status to FINISHED..."
        # Update the test run status to FINISHED        
        tcmsobj.update_testrun(testrun_id, {'status' : 1})
        print "Done."
        print '\033[0m'


def queue_cmd(testname, args={}):
    global COUNTER
    instance_ip = common.get_instance_ip()

    cmd = "%s/rhtest --instance_ip=%s %s " % (file_path, instance_ip, testname)

    if (PARALLEL_MODE==True):
        if COUNTER==0:      #this is certainly INIT script, which we need in both queues
            q.put([cmd, args])
            q2.put([cmd, args])
        elif COUNTER%2==0:
            q.put([cmd, args])
        else:
            q2.put([cmd, args])

        COUNTER=COUNTER+1
    else:
        #simple queue
        q.put([cmd, args])


if __name__ == "__main__":
    main()
