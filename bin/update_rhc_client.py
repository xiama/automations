#!/usr/bin/env python
#
# Helper script for updating RHC clients based on OS
#
# mzimen@redhat.com
#
import os
import sys
import fcntl
import setup_client
from optparse import OptionParser


if __name__ == "__main__":
    parser = OptionParser()
    parser.set_defaults(skip_create_repo=False)
    parser.add_option("-b", "--branch", dest="branch", help="What branch to use for installation. Options: [stage|candidate].")
    parser.add_option("-r", "--release", dest="release", help="What release of rhc client should be used to install. Default is the latest release.")
    parser.add_option("-k", action="store_true", dest="skip_create_repo", help="If skip creating yum repo. Default is False")
    (options, args) = parser.parse_args()

    if not options.branch:
        options.branch = 'candidate'

    if os.getuid() == 0:
        need_sudo = ""
    else:
        need_sudo = "sudo"
    os.system('%s touch /tmp/update_client.lock' % (need_sudo))
    lock_file = file("/tmp/update_client.lock", "r")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
    except IOError, e:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        print "Failed to get update client lock"
        sys.exit(1)
    ret = setup_client.do_setup(options.release, options.branch, options.skip_create_repo)
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
    sys.exit(ret)
