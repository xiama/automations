#!/usr/bin/python
import os
import sys
file_path = os.path.dirname(os.path.realpath(__file__))
lib_path = os.path.abspath(file_path + "/../lib")
sys.path.append(lib_path)
from helper import *


def main():
    usage = """
usage: %s -m devenv_xxx [-n QE_devenv_xxx] [-z xxx]
""" %(os.path.basename(__file__))

    from optparse import OptionParser
    parser = OptionParser(usage=usage)
    parser.add_option("-m", "--ami", dest="ami", help="Instance Arguments: Launch openshift instance from this ami.")
    parser.add_option("-n", "--instance_tag", dest="instance_tag", help="Instance Arguments: Instance tag for the newly launched instance")
    parser.add_option("-z", "--image_size", dest="image_size", default='m1.medium', help="Instance Arguments: Specify size for launching instance. By default it is m1.medium")

    (options, args) = parser.parse_args()
    #print "-->", options
    #print "-->", args
    create_node(options.instance_tag, options.ami, options.image_size)



if __name__ == "__main__":
    exit_code=main()
    sys.exit(exit_code)
