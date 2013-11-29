#!/usr/bin/env python

'''
  File name: reset_testrun.py
  Date:      2012/06/08 11:43
  Author:    mzimen@redhat.com
'''

import sys
import os
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
testmodules_path = os.path.abspath(file_path + "/../testmodules")
sys.path.append(lib_path)
sys.path.append(lib_path + "/supports")
sys.path.append(testmodules_path)
from tcms import TCMS


def main():
    if (len(sys.argv)<2):
        print "ERROR: Usage python %s <TESTRUN_ID> [state1, state2, ...]"%sys.argv[0]
        sys.exit(2)

    sys.argv.pop(0)
    testrun_id=int(sys.argv.pop(0))
    state = sys.argv
    tcmsobj = TCMS()
    return tcmsobj.reset_testrun(testrun_id, state)


if __name__ == "__main__":
    main()

# end of reset_testrun.py 
