#!/usr/bin/python
import os
import sys
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
sys.path.append(lib_path)
from helper import *



def main():
    usage = """
usage: %s -n instance_name
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.add_option("-n", "--instance_name", dest="instance_name", help="shut down specified instance")

    (options, args) = parser.parse_args()
    #print "-->", options
    #print "-->", args
    shutdown_node(options.instance_name)


if __name__ == "__main__":
    exit_code=main()
    sys.exit(exit_code)
