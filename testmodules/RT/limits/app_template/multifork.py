#!/usr/bin/python
"""
This is a template Python script.  It contains boiler-plate code to define and
handle values needed to run the script.  

Default values are defined in the dictionary "defaults". 
Options are defined in the list "test_options"


"""

# ==============================================================================
#
# MODULES - Libraries needed to perform the task
#
# ==============================================================================



# Prepare default output mechanism
import logging

# Access to getenv for default overrides
import os

# Allow exit control
import sys

# for sleep and debug reports
import time

# Objects for CLI argument processing
from optparse import OptionParser, Option

# =======================
# Add test specific modules here
# =======================

# send and recieve control signals
from signal import signal, alarm, SIG_IGN, SIG_DFL, SIGINT, SIGALRM, SIGTERM

# maxint on 64 bit is too big for sleep.
maxsleep = pow(2, 31) -1

# =============================================================================
#
# OPTIONS - initializing the script execution parameters
#
# =============================================================================

#
# Values to use if no explicit input is given
#
defaults = {
    'debug': False,
    'verbose': False,
    'duration': 5,
    'count': 1,
    'sleep': maxsleep,  # maxint on 64 bit is too big for sleep
    'daemon': False,
    'logfile': None,
    'pidfile': None,
    'format': "text"
}

# Check for default overrides from the environment.
# environment variable names are upper case versions of the default keys.
for key in defaults:
    value = os.getenv("MULTIFORK_" + key.upper())
    if value is not None:
        defaults[key] = value

# Options which all scripts must have.
# Defaults may be inserted from the defaults dictionary defined above.
default_options = (
    Option("-d", "--debug", action="store_true", default=defaults['debug'],
           help="enable debug logging"),
    Option("-v", "--verbose", action="store_true", default=defaults['verbose'],
           help="enable verbose logging"),
    Option("-n", "--dryrun", dest="liverun", action="store_false", 
           default=True,
           help="run logic only, no side effects"),
    Option("-D", "--duration", default=defaults['duration'], type="int",
           help="run for the specified time in seconds"),
    Option("-c", "--count", default=defaults['count'], type="int",
           help="run the number of processes requested"),
    Option("-s", "--sleep", default=defaults['sleep'], type="int",
           help="sleep time for child processes"),
    Option(None, "--daemon", default=defaults['daemon'], action="store_true",
           help="run in the background"),
    Option("-l", "--logfile", default=defaults['logfile'],
           help="where to place log output"),
    Option("-f", "--format", default=defaults['format'], type="choice",
           choices=['text', 'html', 'xml', 'json'],
           help="how to format logging output"),
    Option("-p", "--pidfile", default=defaults['pidfile'],
           help="location of a pid file if running in daemon mode")
)


# CLI arguments specifically for this test.  Add them as needed
test_options = (

)

all_options = default_options + test_options


#
# A header for each log output format
#
headerformat = {
    'text':
"""---- Multifork Report: PID %d----
-------------------------------------------------------------------------------
""",

    'html':
        """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
  <head>
    <title>Multifork Report</title>
    <style type="text/css">
    table { border-style : solid ; border-width : 2px ; }
    </style>
  </head>
  <body>
    <!-- PID = %d -->
    <h1>Multifork Report</h1>
""",

    'xml':
        """<runreport title="multifork" process="%d">
  <logentries>
""",

    'json':
        """{ "title": "multifork",
  "process": %d,
  "logs": [
"""
    }

# write the invocation/runtime parameters and run context information
introformat = {
    'text': 
    """Daemon:   %s
Duration: %d seconds
Count:    %d children
Sleep:    %d seconds
Log File: %s
PID File: %s
--------------------------------------------------------------------------------
""",

    'html':
       """<table class="summary">
  <caption>Invocation</caption>
  <tr><th>Name</th><th>Value</th></tr>
  <tr><td>Daemon</td><td>%s</td></tr>
  <tr><td>Duration (sec)</td><td>%d</td></tr>
  <tr><td>Count (procs)</td><td>%d</td></tr>
  <tr><td>Sleep (sec)</td><td>%d</td></tr>
  <tr><td>Log File</td><td>%s</td></tr>
  <tr><td>PID FIle</td><td>%s</td></tr>
</table>
<table class="logs">
  <caption>Event Log</caption>
  <tr>
    <th>PID</th>
    <th>Name</th>
    <th>Log Level</th>
    <th>Date/Time</th>
    <th>Message</th>
  </tr>
""",

    'xml':
       """<invocation daemon="%s" duration="%d" count="%d" sleep="%d" logfile="%s" pidfile="%s">
</invocation>
""",

    'json':
        """
[ "invocation" ]
""" 
    }

#
# A log entry format for each output method
#
logformat = {
    'text': """%(levelname)s:%(name)s:%(process)s: %(message)s""",

    'html': 
"""<tr class="logentry">
  <td class="process">%(process)s</td>
  <td class="logname">%(name)s</td>
  <td class="loglevel">%(levelname)s</td>
  <td class="datetime">%(asctime)s</td>
  <td class="message">%(message)s</td>
</tr>""",

    'xml':  

"""<logentry pid='%(process)s' name='%(name)s' level='%(levelname)s' time='%(asctime)s' >
%(message)s
</logentry>""",

    'json':

"""{
  "pid":     "%(process)s",
  "level":   "%(levelname)s",
  "name":    "%(name)s",
  "time":    "%(asctime)s",
  "message": "%(message)s"
},"""
    }

summaryformat = {
    'text': 
    """--------------------------------------------------------------------------------
summary
""",

    'html':
        """    </table>
<table class="summary">
  <caption>Summary</caption>
  <tr><th>Name</th><th>Value</th></tr>
  <tr><td>Start Time</td><td>-</td></tr>
  <tr><td>End Time</td><td>-</td></tr>
  <tr><td>Duration</td><td>-</td></tr>
</table>

""",
    
    'xml': 
    """<summary>
</summary>
""",

    'json':
"""summary = [ 
],
"""

    }

#
# A footer format for each log output format
#
footerformat = {
    'text': 
    """--------------------------------------------------------------------------------
""",
    
    'html':
        """
  </body>
</html>
""",
    
    'xml':
        """  </logentries>
</runreport>
""",
    
    'json':
        """  ]
}
"""
    
    }




#
# sample take from:
# http://www.noah.org/wiki/Daemonize_Python
#
def daemonize (stdin='/dev/null', stdout='/dev/null', stderr='/dev/null',
               pidfile=None):

    '''This forks the current process into a daemon. The stdin, stdout, and
    stderr arguments are file names that will be opened and be used to replace
    the standard file descriptors in sys.stdin, sys.stdout, and sys.stderr.
    These arguments are optional and default to /dev/null. Note that stderr is
    opened unbuffered, so if it shares a file with stdout then interleaved
    output may not appear in the order that you expect. '''

    # flush any pending output before forking
    sys.stdout.flush()
    sys.stderr.flush()

    # Do first fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e: 
        sys.stderr.write ("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Decouple from parent environment.
    os.chdir("/") 
    os.umask(0) 
    os.setsid() 


    # Do second fork.
    try: 
        pid = os.fork() 
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e: 
        sys.stderr.write ("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror) )
        sys.exit(1)

    # Now I am a daemon!
    logger.debug("I am a daemon")
    # if the caller asked for a pidfile, write it
    if pidfile:
        logger.debug("writing PID file %s" % pidfile)
        pf = file(pidfile, "w")
        pf.write("%d\n" % os.getpid())
        pf.close()

    # Redirect standard file descriptors.
    if stdin:
        si = file(stdin, 'r')
        os.dup2(si.fileno(), sys.stdin.fileno())
    
    if stdout:
        so = file(stdout, 'a+')
        os.dup2(so.fileno(), sys.stdout.fileno())

    if stderr:
        se = file(stderr, 'a+', 0)
        os.dup2(se.fileno(), sys.stderr.fileno())


# ===========================================================================
#
# Process functions
#
# ===========================================================================
class ProcessList(object):

    def __init__(self):
        self._complete = False
        self._processes = []
        self._duration = None
        self._count = None
        self._maxprocs = None
        self._child = False

    def activate(self, duration=10, count=0, sleep=maxsleep):

        logger = logging.getLogger(self.__class__.__name__ + ".activate")

        self._duration = duration
        self._count = count
        self._sleep = sleep
        self._maxprocs = self._count

        signal(SIGALRM, self.finish)
        signal(SIGINT, self.abort)
        signal(SIGTERM, self.abort)

        alarm(self._duration)

        loop = 0
        while not self._child and not self._complete:
            # create processes until you reach max
            while len(self._processes) < self._maxprocs and not self._child:
                self.spawn()

            # max processes reached: wait for one to end
            if len(self._processes) > 0:
                logger.info("%d processes running" % len(self._processes))
                try:
                    (cpid, cstatus, rusage) = os.wait3(0)
                    logger.debug("process %d completed with status %d" % (cpid, cstatus))
                except OSError, e:
                    if e.errno == 4:
                        # alarm went off
                        logger.debug("alarm woke me from wait")
                    else:
                        raise
                    
        # remove remaining processes
        self.shutdown()
        logger.info("run complete: procs requested: %d, max: %d" % (self._count, self._maxprocs))

    def spawn(self):
        # create more
        logger = logging.getLogger(self.__class__.__name__ + ".spawn")

        try:
            newpid = os.fork()
        except OSError, e:
            if e.errno == 11:
                # no more processes
                self._maxprocs = len(self._processes)
                logger.debug("Maximum processes reached: %d" % self._maxprocs)
                return
            else:
                # no one expects something else
                raise

        if newpid == 0:
            self.child()
            return
        
        logger.debug("new child #%d, pid = %d" % (len(self._processes), newpid))
        self._processes.append(newpid)

    def child(self):
        # a child: just go to sleep and exit when done
        # children should have no more child processes
        logger = logging.getLogger(self.__class__.__name__ + ".child")

        self._child = True
        signal(SIGALRM, SIG_IGN)
        self._processes = []
        self._complete = True
        logger.debug("sleeping %d sec" % self._sleep)
        time.sleep(self._sleep)
        logger.debug("exiting")
        sys.exit(0)

    def abort(self, signum, frame):
        if not self._child:
            logger.info("recieved external interrupt")
        self.finish(signum, frame)

    def finish(self, signum, frame):
        """Terminate all pending processes"""
        logger = logging.getLogger(self.__class__.__name__ + ".finish")
        logger.debug("caught signal %d" % signum)

        # ignore the timer
        signal(SIGALRM, SIG_IGN)        

        self._complete = True

    def shutdown(self):
        """Kill and reap all of the processes in the list"""
        # don't respond to children, we're going to wait for them explicitly
        logger = logging.getLogger(self.__class__.__name__ + ".shutdown")

        while len(self._processes) > 0:
            pid = self._processes[0]
            logger.debug("%d processes remaining" % len(self._processes))
            logger.debug("terminating process %d" % pid)

            # terminate the process
            try:
                os.kill(pid, SIGTERM)
            except OSError, e:
                print "Error killing process %d: %s" % (pid, e.message)
                

            # reap the process
            try:
                logger.debug("waiting for process %d" % pid)
                (cpid, cstatus, cresource) = os.wait3(0)
                if pid != cpid:
                    logger.warning("reaped process %d, expected %d" % (cpid, pid))
                # don't do anything with pid 0
                if cpid != 0:
                    # delete this child process from the active list
                    logger.debug("removing pid %d from process list" % cpid)
                    i = self._processes.index(cpid)
                    del self._processes[i]
                else:
                    logger.debug("process %d not waiting for reaping" % pid)
            except OSError, e:
                print "Error waiting for process %d: %s" % (pid, e.message)

# ============================================================================
#
# MAIN - Script Body
#
# ============================================================================

if __name__ == "__main__":


    # ======================================================================
    # Environment and Command Line Processing
    # ======================================================================

    # Process command line arguments
    (opt, args) = OptionParser(option_list=all_options).parse_args()

    if opt.daemon:
        logger.warning("daemonizing")
        daemonize("/dev/null", opt.logfile, opt.logfile, pidfile=opt.pidfile)

    if opt.logfile:
        # create a file handler with the requested file
        
        logging.basicConfig(
            level=logging.INFO, 
            format=logformat[opt.format], 
            datefmt="%Y%m%d-%H:%M:%S-%Z",
            filename=opt.logfile
            )
        f = file(opt.logfile, 'a')
        f.write(headerformat[opt.format] % os.getpid())
        f.write(introformat[opt.format] % (opt.daemon, opt.duration, opt.count, opt.sleep, opt.logfile, opt.pidfile))
        # be sure the output buffer is empty before forking or it prints twice
        f.flush()
        f.close()

    else:
        logging.basicConfig(level=logging.INFO,
                            format=logformat[opt.format], 
                            datefmt="%Y%m%d-%H:%M:%S-%Z",
                            stream=sys.stdout
                            )
        sys.stdout.write(headerformat[opt.format] % os.getpid())
        sys.stdout.write(introformat[opt.format] % (opt.daemon, opt.duration, opt.count, opt.sleep, opt.logfile, opt.pidfile))
        sys.stdout.flush()
        # be sure the output buffer is empty before forking or it prints twice

    # Define the main program logger
    logger = logging.getLogger("multifork")

    if opt.verbose:
        logging.root.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
        logger.info(" enabled verbose logging")

    # Enable debug output if the user has requested it
    if opt.debug:
        logging.root.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug(" enabled debug logging")

    # =======================================================================
    # Begin Task Logic
    # =======================================================================

    logger.debug("Forking %d times for %d seconds" %
                 (opt.count, opt.duration)
                 )

    plist = ProcessList()

    plist.activate(opt.duration, opt.count)

    if opt.logfile:
        f = file(opt.logfile, "a")
        f.write(summaryformat[opt.format])
        f.write(footerformat[opt.format])
        f.close()
    else:
        sys.stdout.write(summaryformat[opt.format])
        sys.stdout.write(footerformat[opt.format])

    if opt.daemon and opt.pidfile:
        os.unlink(opt.pidfile)
