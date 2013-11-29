#!/usr/bin/env python

"""
file for getting config
"""
import database
import simplejson as json
import dictlib
import os
import commands
import sys
file_path = os.path.dirname(os.path.realpath(__file__))
work_dir = os.path.abspath(file_path + "/../")


def get_config():
    """
    return a dot accessible dictionary of default configurations.  Will try to
    read from a local storage (a json file) or from an extrenal db if nothing
    can be read from local
    """
    config = None
    
    try:
        fname = os.path.join(work_dir, "etc", "config.json")
        if os.environ.has_key("RHTEST_HOME"):
            fname = os.path.join(os.environ["RHTEST_HOME"], "etc", "config.json")
        config_json = open(fname, 'r')
        config_str = json.load(config_json)
        config = dictlib.AttrDictWrapper(config_str)
    except:
        print >>sys.stderr, "Error encountered reading from local, trying from remote DB..."
        config_dict = database.get_defaults()
        config = dictlib.AttrDictWrapper(config_dict)
    return config

def get_logfilename(cf):
    import logfile
    user_name = commands.getoutput('whoami')
    lfd = "/var/tmp/%s" % user_name
    if not os.path.isdir(lfd):
        os.mkdir(lfd)
    logfilename = os.path.join(os.path.expanduser(lfd), cf.logbasename)
    cf['logfilename'] = logfilename
    return logfilename

def get_logfile(cf):
    import logfile
    lfname = get_logfilename(cf)

    try:
        lf = logfile.ManagedLog(lfname, 1000000)
    except:
        ex, val, tb = sys.exc_info()
        print >>sys.stderr, "get_logfile: Could not open log file."
        print >>sys.stderr, ex, val
        return _StdErrLog()
    else:
        return lf
    
def get_report(cf):
    import reports
    # take out extension
    logname_without_extension = os.path.splitext(cf.logbasename)[0]
    log_path = os.path.join(cf.resultsdir, logname_without_extension)
    
    params = ('StandardReport', log_path ,'text/html')
    return reports.get_report(params)

def get_ui(cf):
    import CLI
    return CLI.get_terminal_ui(cf)
