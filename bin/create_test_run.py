#!/usr/bin/python
import os
import sys
import time
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
sys.path.append(lib_path)
from tcms import TCMS, TCMSException


tcmsobj = None

	


def create_test_run(testrun_tag, tc_id_list, testplan_id):
    """
    Create TCMS.TestRun according to tc_id_list.
    """
    timestamp = time.strftime("%Y_%m_%d-%H:%M:%S", time.localtime())
    test_run_summary = "Openshift-%s-%s" %(testrun_tag, timestamp)
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



def main():
    global tcmsobj

    usage = """
usage: %s -t new_run_tag (-c 'n, ..., m')|(-g 'xxx, ..., zzz') [-p xxx]
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--testrun_tag", dest="testrun_tag", help="TCMS Arguments: Create new test run with this tag")
    parser.add_option("-i", "--testrun_id", dest="testrun_id", type=int, help="TCMS Arguments: Using this existing test run that you want to run.")
    parser.add_option("-c", "--testcase_ids", dest="testcase_ids", help="TCMS Arguments: A list of test case ids that you want to execute")
    parser.add_option("-g", "--testcase_tags", dest="testcase_tags", help="TCMS Arguments: A list of test case tags that you want to execute")
    parser.add_option("-p", "--testplan_id", dest="testplan_id", default=4962, type=int, help="TCMS Arguments: All test cases are selected from this test plan for creating/updating test run. By default it is 4962 - https://tcms.engineering.redhat.com/plan/4962/")

    (options, args) = parser.parse_args()
    #print "-->", options
    #print "-->", args


    testplan_id=options.testplan_id
    

    #Do TCMS authentication only once
    tcmsobj = TCMS()

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



    # Priority for test case filter arguments: -c -> -g
    if options.testrun_tag != None:                        
        if len(tc_id_list) != 0:
            test_run_id = create_test_run(options.testrun_tag, tc_id_list, testplan_id)
            print "test_run_id=%s" %(test_run_id)
        elif len(tc_tag_list) != 0:
            tc_id_list = tcmsobj.get_testcase_id_list_by_tag(tc_tag_list, testplan_id)
            test_run_id = create_test_run(options.testrun_tag, tc_id_list, testplan_id)
            print "test_run_id=%s" %(test_run_id)
        else:
            print usage
            raise Exception("Entry test case id list using option '-c' or test case tag list using option '-g'")
    else:
        print usage
        raise Exception("Create new TCMS test run using option '-t'")

    return test_run_id


def error(msg):
    print >> sys.stderr,"ERROR: ",msg

def info(msg):
    print >> sys.stderr,"INFO: ",msg

def debug(msg):
    print >> sys.stderr,"DEBUG: ",msg

def debug2(msg):
    print >> sys.stderr,"DEBUG: ",msg

if __name__ == "__main__":
    main()
