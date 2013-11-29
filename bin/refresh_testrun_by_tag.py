#!/usr/bin/env python

'''
  File name: refresh_testrun_by_tag.py
  Date:      2012/06/08 11:43
  Author:    mzimen@redhat.com

  Only CONFIRMED & Auto testcases will be fetched with given TAG
'''
import sys
import re
import os
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
sys.path.append(lib_path)
from tcms import TCMS

def main():
    if (len(sys.argv)<3):
        print "ERROR: Usage python %s <TESTRUN_ID> <TAG>"%sys.argv[0]
        sys.exit(2)

    sys.argv.pop(0)
    testrun_id = sys.argv.pop(0)
    tcmsobj = TCMS()
    #1. get current list of testcases...
    all_tcs = {}
    new_tcs = {}
    for tc in tcmsobj.server.TestRun.get_test_cases(testrun_id):
        all_tcs[tc['case_id']]=1

    for tag in sys.argv:
        print 'Appending tag: ', tag

        #2. get all automated+confirmed testcases per tag
        f = {'plan':4962, 
             'case_status':2, #confirmed
             'is_automated': 1,
             'tag__name': tag}
        testcases_by_tag = tcmsobj.server.TestCase.filter(f)

        #3. prepare list of testcases...
        for tc in testcases_by_tag:
            if all_tcs.has_key(tc['case_id']):
                all_tcs[tc['case_id']]='OK'
            else: #new one
                new_tcs[tc['case_id']]=2

    #4. remove all==1
    to_remove = []
    for tc in all_tcs.keys():
        if all_tcs[tc] == 1:  #to remove
            to_remove.append(tc)
            del all_tcs[tc]
        elif all_tcs[tc] == 'OK':  #skip existing
            del all_tcs[tc]

    if len(to_remove)>0:
        print "Removing %s testcases..."%len(to_remove)
        tcmsobj.server.TestRun.remove_cases(testrun_id, to_remove)

    #5. add them all to the given testrun
    try:
        print "Appending %s new testcases..."%len(new_tcs.keys())
        tcmsobj.server.TestRun.add_cases(testrun_id, new_tcs.keys())
    except Exception as e:
        print 'ERROR:', str(e)
        return 254

    return 0


if __name__ == "__main__":
    main()

# end of reset_testrun.py 
