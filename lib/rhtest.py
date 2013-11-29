#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Forked from pyNMS qatest module.

"""
This module contains the test case and test suite classes used to control
the running of tests and provides a basic framework for automated testing.
It is the core part of automated testing.

This module defines a Test class, which is the base class for all test
case implementations. This class is not normally substantiated itself, but
a subclass is defined that defines a 'test_method()' method. 

To use the test case, instantiate your class and call it with test method
parameters. You can define two hook methods in the subclass: 'initialize'
and 'finalize'.  These are run at the beginning and end of the test,
respectively.


All test related errors are based on the 'TestError' exception. If a test
cannot be completed for some reason you may raise a 'TestIncompleteError'
exception.

Your 'test_method()' should return the value of the 'passed()' or
'failed()' method, as appropriate. You may also use assertions. The
standard Python 'assert' keyword may be used, or the assertion test
methods may be used.

Usually, a set of test cases is collected in a TestSuite object, and run
sequentially by calling the suite instance. 

"""

import sys, os
import shutil
import debugger
import datetime
import scheduler
import timelib
import signal
import database
import re
import traceback
import inspect
from helper import TimeoutError, cmd_get_status_output, get_tmp_dir
import time
import testcase
import tcms_base
import tcms

__all__ = [ 'Test', 'PreReq', 'TestSuite', 'repr_test', 'initialize', 'finalize']

# exception classes that may be raised by test methods.
class TestError(AssertionError):
    """TestError() Base class of testing errors."""
    pass

class TestIncompleteError(TestError):
    """Test case disposition could not be determined."""
    pass

class TestFailError(TestError):
    """Test case failed to meet the pass criteria."""
    pass

class TestSuiteAbort(RuntimeError):
    """Entire test suite must be aborted."""
    pass

class TestSuiteWaived(RuntimeError):
    """Entire test suite must be aborted."""
    pass

# "public" exceptions
add_exception(TestIncompleteError)
add_exception(TestFailError)
add_exception(TestSuiteAbort)


# One of the below values should be returned by test_method(). The usual
# method is to return the value of the method with the same name. E.g.
# 'return self.passed()'. The Test.passed() method adds a passed message
# to the report, and returns the PASSED value for the suite to check.

# for multiple UUTs we use this status to indicate whether or not the 
# test ran to completeion.
COMPLETED = Enum(2, "COMPLETED")

# test_method() passed, and the suite may continue.
PASSED = Enum(1, "PASSED")

# test_method() failed, but the suite can continue. You may also raise a
# TestFailError exception.
FAILED = Enum(0, "FAILED") 

# test_method() could not complete, and the pass/fail criteria could not be
# determined. but the suite may continue. You may also raise a TestIncompleteError
# exception.
INCOMPLETE = Enum(-1, "INCOMPLETE") 

# test_method() could not complete, and the suite cannot continue. Raising
# TestSuiteAbort is the same.
ABORT = Enum(-2, "ABORT") 

SKIP = Enum(-3, "SKIP") 

WAIVED = Enum(-4, "WAIVED") 

# default report message
NO_MESSAGE = "no message"



######################################################
# abstract base class of all tests
class Test(object):
    """Base class for all test cases. The test should be as atomic as possible.
    Multiple instances of these may be run in a TestSuite object.  Be sure to
    set the PREREQUISITES class-variable in the subclass if the test has a
    prerequisite test."""
    # prerequisite tests are static, defined in the class definition.
    # They are defined by the PreReq class. The PreReq class takes a name of a
    # test case (which is the name of the Test subclass) and any arguments that
    # the test requires. A unique test case is defined by the Test class and
    # its specific arguments. The PREREQUISITES class attribute is a list of
    # PreReq objects.
    # e.g. PREREQUISITES = [PreReq("MyPrereqTest", 1)]
    PREREQUISITES = []
    INTERACTIVE = False # define to True if your test is interactive (takes user input).
    ITEST = None      # type of test we are running 

    def __init__(self, config):
        self._tests = {}
        self._testname = self.__class__.__name__
        self._tests[self._testname] = self._testname
        self.config = config 
        self.config.test_name = self.__class__.__name__
        self.config.tests= self._tests
        self.config.total_time = 0
        self._report = config.report 
        self._ui = config.userinterface
        self._debug = config.options.DEBUG 
        self._verbose = config.options.VERBOSE
        self._tcms_stuff =  {
                'current_testcase_id': None, 
                'current_testcase_run_id': None, 
                'current_test_run_id': None }   # hold tcms stuff

        if self.config.__dict__.has_key("tcms_arguments") and isinstance(self.config.tcms_arguments, dict):
            if self.config.tcms_arguments.has_key("variants"):
                self.info("Warning: Obsolete format for test_variant in TCMS. Please use {'variant': 'php'} format instead.")
                if isinstance(self.config.tcms_arguments["variants"],list):
                    self.info("Warning: List in variants is not supported. Only the first item will be used.")
                    self.test_variant = self.config.tcms_arguments["variants"][0]
                    self.config.test_variant = self.config.tcms_arguments["variants"][0]
                else:
                    self.test_variant = self.config.tcms_arguments["variants"]
                    self.config.test_variant = self.config.tcms_arguments["variants"]
            elif self.config.tcms_arguments.has_key("variant"):
                if isinstance(self.config.tcms_arguments["variant"],list):
                    self.info("Warning: List in variant is not supported. Only the first item will be used.")
                    self.test_variant = self.config.tcms_arguments["variant"][0]
                    self.config.test_variant = self.config.tcms_arguments["variant"][0]
                else:
                    self.test_variant = self.config.tcms_arguments["variant"]
                    self.config.test_variant = self.config.tcms_arguments["variant"]
        
        #this is only for developing/debugging
        # - it's easier to just setup variable instead of .conf file
        if os.getenv("OPENSHIFT_test_variant"):
            self.test_variant = os.getenv("OPENSHIFT_test_variant")
            self.config.test_variant = self.test_variant

        self.tcms_testcaserun_id = self.config.tcms_testcaserun_id
        self.tcms_obj = self.config.tcms_obj
        #print "----->", self.config.tcms_obj


        # XXX: this flag attribute should be added with slstorage.
        if not config.has_key('NORECORD'):
            config['NORECORD'] = False
        self._norecord= config.NORECORD

        self.disposition = {}
        self.configfile = os.path.join(os.path.dirname(sys.modules[self.__module__].__file__), "%s.conf" % (self._tests[self._testname],))

        self._steps = []  #list of TestSteps
        self._steps_output = dict()  #list of TestSteps's outputs

    def __call__(self, *args, **kw):
        cf = self.config
        if os.path.isfile(self.configfile):
            execfile(self.configfile, cf.__dict__)
            #cf.mergefile(self.configfile)
            #self.info('xxx', 1)
            try:
                cf.config_ID = os.path.basename(cf.config_ID.split()[1])
            except AttributeError:
                cf.config_ID = None
            except IndexError:
                cf.config_ID = "<undefined>"
                print >>sys.stderr, 'Make sure your config file is type "ktext" in Perforce.'
        else:
            cf.config_ID = None
        # this heading displays the test name just as a PREREQUISITES entry needs.
        self._ui.add_heading(repr_test(self._testname, args, kw), 2)
        self._report.add_heading(repr_test(self._testname, args, kw), 2)
        
        if cf.config_ID:
            self.info("Configuration ID: %s" % (cf.config_ID,))
        self.starttime = timelib.now()
        self.info("STARTTIME: %s" % self.timestamp(self.starttime))
        rv = None # in case of exception
        try:
            rv = self._initialize(rv)
            if rv is not None: # an exception happened
                try:
                    self.update_testcaserun('ERROR')
                except:
                    print "ERROR: Unable to update TCMS status after _initialize() error: "
                return rv
        except Exception as e:
            #TODO: how to store results into TCMS?
            self.error("Test initialization failed - exiting")
            return 254
            #raise TestSuiteAbort("Unable to initialize testcase...")
        # test elapsed time does not include initializer time.
        teststarttime = timelib.now()
        # run test_method
        testloops = int(cf.get("testloops", 1))
        try:
            for l in xrange(testloops):
                rv = apply(self.test_method, args, kw)
        except KeyboardInterrupt:
            if self._debug:
                ex, val, tb = sys.exc_info()
                debugger.post_mortem(ex, val, tb)
            rv = self.abort("%s: aborted by user." % self._tests[self._testname])
            self._finalize(rv)
            raise
        except (TestFailError, testcase.TestCaseStepFail), errval:
            rv = self.failed("Caught Fail exception: %s" % (errval,))
        except (TestIncompleteError, TimeoutError), errval:
            rv = self.incomplete("Caught Incomplete exception: %s" % (errval,))
            self.debug("-"*80)
            traceback.print_exc(file=sys.stderr)
            self.debug("-"*80)
        except AssertionError, errval:
            rv = self.failed("failed assertion: %s" % (errval,))
        except TestSuiteAbort:
            ex, val, tb = sys.exc_info()
            if self._debug:
                debugger.post_mortem(ex, val, tb)
                tb = None
            rv = self.incomplete("%s: ### Abort Exception occured! (%s: %s)" % (self._tests[self._testname], ex, val))
            raise # pass this one up to suite

        self.endtime = timelib.now()
        minutes, seconds = divmod(self.endtime - teststarttime, 60.0)
        hours, minutes = divmod(minutes, 60.0)
        self._test_execution_time =  "%02.0f:%02.0f:%02.2f" % (hours, minutes, seconds)
        self.config.total_time += self.endtime - teststarttime
        self.info("Time elapsed: %s" % (self._test_execution_time))
        rv = self._finalize(rv)
        # if not specified in command line, then record the result by default
        #print "CF_OPTION_RECORD: %s" % cf.options.RECORD

        self.update_testcaserun()

        if not cf.options.TCMS:
            self.info("Records NOT written into TCMS...")
            #print "OP: %s" % cf.options.tcms_run_details
            try:
                run_id, case_run_id, testcase_id = cf.options.tcms_run_details.split(',')
                self._tcms_stuff['current_testcase_id'] = int(testcase_id)
                self._tcms_stuff['current_testcase_run_id'] = int(case_run_id)
                self._tcms_stuff['current_test_run_id'] = int(run_id)
            except:
                pass

        else:
            # put TCMS related stuff here.  XXX need to look for this option
            # earlier as well to start a testrun/testcaserun within TCMS, so
            # this function will just update the status.  By this time, the
            # testrun will be know (saved from earlier).  Update the
            # testcaserun as well if need be.
            testcase_id = self.config.tcms_obj.get_testcase_id_by_script_name(self.__module__)
            tcms_res = self.update_db_tcms(testcase_id)
            if tcms_res[1] is None:
                case_run_id = None
            else:
                case_run_id = tcms_res[1][0]['case_run_id']

            if tcms_res[1] is None:
                run_id = None
            else:
                run_id = tcms_res[1][0]['run_id']


            self._tcms_stuff['current_testcase_id'] = testcase_id
            self._tcms_stuff['current_testcase_run_id'] = case_run_id
            self._tcms_stuff['current_test_run_id'] = run_id
            self.info("Results written to TCMS...")

        if not cf.options.RECORD:
            self.info("Records NOT stored in database")
        else:
            self._record_results()
            self.info("Results written to SQL DB %s ..." % (cf.HOST))

        return rv

    def _initialize(self, rv):
        """ Test """
        self._report.add_heading("Test suite: %s" % self.__class__.__name__, 1)
        try:
            self.initialize()
        except:
            ex, val, tb = sys.exc_info()
            self.diagnostic("%s (%s)" % (ex, val))
            if self._debug:
                debugger.post_mortem(ex, val, tb)
            rv = self.abort("Test initialization failed!")
            self.debug("-"*80)
            traceback.print_exc(file=sys.stderr)
            self.debug("-"*80)
        return rv

    # run user's finalize() and catch exceptions. If an exception occurs
    # in the finalize() method (which is supposed to clean up from the
    # test and leave the UUT in the same condition as when it was entered)
    # then alter the return value to abort(). 
    def _finalize(self, rv):
        try:
            self.finalize()
        except:
            ex, val, tb = sys.exc_info()
            self.diagnostic("%s (%s)" % (ex, val))
            if self._debug:
                debugger.post_mortem(ex, val, tb)
            rv = self.abort("Test finalize failed!")
        return rv

    def get_instance_ip(self):
        return self.config.instance_info['ip']

    def get_run_mode(self):
        return self.config.options.run_mode

    def get_variant(self):
        """
        This function should be run inside try/except to handle cases 
        when no variant is defined.
        """
        return self.config.test_variant

    def timestamp(self, abstime):
        return timelib.strftime("%a, %d %b %Y %H:%M:%S %Z", timelib.localtime(abstime))

    def logfilename(self, ext="log"):
        """Return a standardized log file name with a timestamp that should be
        unique enough to not clash with other tests, and also able to correlate
        it later to the test report via the time stamp."""
        return "%s-%s.%s" % (self._tests[self._testname], timelib.strftime("%Y%m%d%H%M%S", timelib.localtime(self.starttime)), ext)

    def _record_results(self):
        """
        There are two types of records:
            1. TCMS
            2. mysql 
        """
        resid = self._update_db()
        #resid = None 
        if resid is None:
            pass
        else:
            self.info("TestResult ID is %s." % (resid,))
            try:
                self.record_results(resid)
            except:
                import traceback
                import string
                import sys
                print "An error was thrown: %s"\
                        %string.join(traceback.format_exception(*sys.exc_info()), '')
                pass

    def record_results(self, resid, testcase_id=None):
        """Override this if you need additional result records. This method is
        passed the TestResult tables result ID for this test run, to use as the
        foreign key."""
        pass

    def _update_db(self):
        ui = self.config.userinterface
        rdb = self.config.resultsdirbase
        burl = self.config.baseurl
        cf = self.config
        if self.config.comment is not None:
            if self.config.comment.startswith('='):
                self.config.comment = self.config.comment[1:]

            if self.config.comment.startswith('"') and self.config.comment.endswith('"'):
                # get rid of quotes
                self.config.comment = self.config.comment[1:-1]
        # use the hardcoded value if none is given.
        passfail = str(self.disposition[0])[0]
        build_version = cf.instance_info['build_version']
        ami_id = cf.instance_info['ami_id']
        instance_ip = cf.instance_info['ip']
        run_mode = self.config.options.run_mode

        database.connect2db(self.config.DBURI)
        if sys.platform.startswith('linux'):
            signal.signal(signal.SIGCHLD, signal.SIG_IGN)  #to avoid warning from pipe.close from commands.getoutput
        tr = database.TestResults(
                AmiID=ami_id,
                TestName=self._tests[self._testname],
                StartTime=datetime.datetime.fromtimestamp(self.starttime),
                EndTime=  datetime.datetime.fromtimestamp(self.endtime),
                TestbedID = instance_ip,
                TestScript = cf.test_name,
                ResultsDataFile = ",".join(map(lambda s: burl + "/testresults/" + s[len(rdb)+1:], map(str, self.config.reportfilenames))),
                User=str(self.config.user),
                Comments = self.config.options.notes,
                PassFail=passfail,
                BuildVersion =build_version,
                RunMode = run_mode,
                TcmsTag = cf.options.tag,
                TcmsTestCaseId = self._tcms_stuff['current_testcase_id'],
                TcmsTestCaseRunId = self._tcms_stuff['current_testcase_run_id'],
                TcmsTestRunId = self._tcms_stuff['current_test_run_id'],
                )
        self.diagnostic("ID: %s" % tr.id)
        return tr.id
    
    def update_db_tcms(self, testcaserun_id=None):
        """
        tcms_obj and testrun_res are the keys to be used.
        """

        status_lookup = {'PASSED': 2, 'FAILED': 3}
        tcms = self.config.tcms_obj
        testrun_id = None
        res = None
        for testrun_res in self.config.testrun_res:
            testrun_id = testrun_res['run_id']
            if testcaserun_id == testrun_res['case_id']:
                testrun_id = testrun_res['run_id']
                case_run_id = testrun_res['case_run_id']
                test_status = self.disposition[0].__str__()
                status_bit = status_lookup[test_status]
                params = {'case_run_status': status_bit, 'notes': self.config.results_url,
                        'estimated_time': self._test_execution_time}
                res = tcms.update_testcaserun(case_run_id, params)
        # update the test run status to FINISH if this is the only test in the
        # test run
        return (tcms.update_testrun(testrun_id, {'status': 0}), res)


    def save_fileobject(self, fo, name=None):
        """Save a file-like object to results directory. You must supply a file
        name if the file-like object does not have a name."""
        dst = self.get_pathname(name or fo.name)
        outf = file(dst, "w")
        shutil.copyfileobj(fo, outf)
        outf.close()

    def save_file(self, fname):
        """save your generated data file into the results directory."""
        shutil.copy(fname, os.path.expandvars(self.config.resultsdir))

    def save_object(self, obj, filename=None):
        """Save an object into the filename in the results directory."""
        if not filename:
            filename = "%s.txt" % (obj.__class__.__name__,)
        # kludge alert
        if filename.endswith(".xml"):
            self.config.resultsfilename = filename
        filename = self.get_pathname(filename)
        outf = file(filename, "w")
        try:
            outf.write(str(obj))
        finally:
            outf.close()
        return filename
    def get_pathname(self, filename):
        "Return full pathname to results directory with given filename."
        return os.path.join(os.path.expandvars(self.config.resultsdir), os.path.basename(filename))

    # Tests expose the scheduler interface also
    def sleep(self, secs):
        """Sleep method simply sleeps for specified number of seconds."""
        return scheduler.sleep(secs)

    def schedule(self, delay, cb):
        """Schedule a callback to run 'delay' seconds in the future."""
        return scheduler.add(delay, callback=cb)

    def timed(self, function, args=(), kwargs={}, timeout=30):
        """Call a method with a failsafe timeout value."""
        sched = scheduler.get_scheduler()
        return sched.timeout(function, args, kwargs, timeout)

    def timedio(self, function, args=(), kwargs={}, timeout=30):
        """Call a method with a failsafe timeout value."""
        sched = scheduler.get_scheduler()
        return sched.iotimeout(function, args, kwargs, timeout)

    def run_subtest(self, _testclass, *args, **kwargs):
        """Runs a test test class with the given arguments. """
        inst = _testclass(self.config)
        return apply(inst, args, kwargs)

    def debug(self):
        """Enter the debugger... at will."""
        debugger.set_trace()

    def set_debug(self, onoff=1):
        """Turn on or off the DEBUG flag."""
        ov = self._debug
        self._debug = self.config.flags.DEBUG = onoff
        return ov

    def set_verbose(self, onoff=1):
        """Turn on or off the VERBOSE flag."""
        ov = self._verbose
        self._verbose = self.config.flags.VERBOSE = onoff
        return ov

    def prerequisites(self):
        "Get the list of prerequisites, which could be empty."
        return getattr(self, "PREREQUISITES", [])

    # the overrideable methods
    def initialize(self):
        "Hook method to initialize a test. Override if necessary."
        pass

    def finalize(self):
        "Hook method when finalizing a test. Override if necessary."
        pass

    ### the primary test method that subclasses must define.
    def test_method(self, *args, **kw):
        """Overrided this method in a subclass to implement a specific test."""
        return self.failed('you must define a method named "test_method" in your subclass.')

    # result reporting methods
    def methodstring(self, meth, *args):
        """Return a string representation of a method object plus its arguments."""
        return "%s(%s)" % (meth.im_func.func_name, ", ".join(map(str, args)))

    def get_status(self, testcase_id=0):
        try:
            return self.disposition[testcase_id].__str__()
        except:
            # if no status has been assigned yet
            return None

    def update_testcaserun(self, set_status=None):
        if self.tcms_testcaserun_id != None:
            if (set_status == None):
                status = self.get_status()
                if status is None:
                    self.info("Unable to get result of testcase, ERROR used instead")
                    status = 'ERROR'
            else:
                status = set_status
            if status not in tcms.CASE_RUN_STATUS.keys():
                status = tcms.rhtest_disposition_to_tcms_mapping[status]

            params = dict()
            params['case_run_status'] = tcms.CASE_RUN_STATUS[status]
            try:
                params['estimated_time'] =  self._test_execution_time
            except:
                #case when aborted during suite initialization
                pass


            """
            if self.tcms_testcaserun_notes == None:
                params = {'case_run_status' : tcms.CASE_RUN_STATUS[status],
                          'estimated_time': self._test_execution_time}
            else:
                params = {'case_run_status' : tcms.CASE_RUN_STATUS[status],
                          'notes' : self.tcms_testcaserun_notes,
                          'estimated_time': self._test_execution_time}
            """
            try:
                self.info("Updating TCMS test case run [%s] ..."%status)
                self.tcms_obj.update_testcaserun(self.tcms_testcaserun_id, params)
                self.info("Done.")
            except Exception as e:
                self.error("ERROR: Unable to update TCMS for %s. %s"%(self.tcms_testcaserun_id, str(e)))
        else:
            self.info("Warning: tcms_testcaserun_id is not defined, TestCaseRun is NOT updated")


    def passed(self, msg=NO_MESSAGE, testcase_id=0):
        """Call this and return if the test_method() passed. If part of
        a suite, subsequent tests may continue."""
        self._ui.passed(msg)
        self._report.passed(msg)
        self.disposition[testcase_id] = PASSED
        return PASSED

    def failed(self, msg=NO_MESSAGE, testcase_id=0):
        """Call this and return if the test_method() failed, but can continue
        the next test."""
        self._ui.failed(msg)
        self._report.failed(msg)
        self.disposition[testcase_id] = FAILED
        return FAILED
    
    def skip(self, msg=NO_MESSAGE, testcase_id=0):
        #TODO:
        return SKIP

    def waived(self, msg=NO_MESSAGE, testcase_id=0):
        self._ui.abort(msg)
        self._report.abort(msg)
        self.disposition[testcase_id] = WAIVED
        return WAIVED

    def completed(self, msg=NO_MESSAGE):
        self._ui.completed(msg)
        self._report.completed(msg)
        return COMPLETED

    def incomplete(self, msg=NO_MESSAGE, testcase_id=0):
        """Test could not complete."""
        self._ui.incomplete(msg)
        self._report.incomplete(msg)
        self.disposition[testcase_id] = INCOMPLETE
        return INCOMPLETE

    def abort(self, msg=NO_MESSAGE):
        """Some drastic error occurred, or some condition is not met, and the suite cannot continue."""
        self._ui.abort(msg)
        self._report.abort(msg)
        #raise TestSuiteAbort
        return ABORT

    def debug(self, msg):
        """Call this to record non-critical information in the report object."""
        #print >> sys.stderr, "DEBUG:",msg   
        self._ui.info(msg)
        self._report.info(msg)

    def info(self, msg):
        """Call this to record non-critical information in the report object."""
        self._ui.info(msg)
        self._report.info(msg)

    def step(self, msg):
        """Call this to mark the beginning of one step"""
        self._ui.info(msg.center(60, '='))
        self._report.info(msg.center(60, '='))
    
    def verboseinfo(self, msg):
        """Call this to record really non-critical information in the report
        object that is only emitted when the VERBOSE flag is enabled in the
        configuration."""
        if self._verbose:
            self._ui.info(msg)
            self._report.info(msg)

    def diagnostic(self, msg):
        """Call this one or more times if a failed condition is detected, and
        you want to record in the report some pertinent diagnostic information.
        Then return with a FAIL message."""
        self._ui.diagnostic(msg)
        self._report.diagnostic(msg)

    def error(self, msg):
        """Call this to record errors the report object."""
        self._ui.error("ERROR: %s" % msg)
        self._report.add_message("ERROR", msg)

    # user input methods. May only be used for tests flagged as INTERACTIVE.
    def user_input(self, prompt=None):
        if self.INTERACTIVE:
            return self._ui.user_input(prompt)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def choose(self, somelist, defidx=0, prompt=None):
        if self.INTERACTIVE:
            return self._ui.choose(somelist, defidx, prompt)
        else:
            raise TestIncompleteError, "user input in non-interactive test."
    
    def get_text(self, msg=None):
        if self.INTERACTIVE:
            return self._ui.get_text(msg)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def get_value(self, prompt, default=None):
        if self.INTERACTIVE:
            return self._ui.get_input(prompt, default)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def yes_no(self, prompt, default=True):
        if self.INTERACTIVE:
            return self._ui.yes_no()
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def get_key(self, prompt=None, timeout=None, default=""):
        if self.INTERACTIVE:
            return self._ui.get_key(prompt, timeout, default)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def display(self, line):
        if self.INTERACTIVE:
            return self._ui.display(line)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    def Print(self, *args):
        if self.INTERACTIVE:
            return self._ui.Print(*args)
        else:
            raise TestIncompleteError, "user input in non-interactive test."

    # assertion methods make it convenient to check conditions.
    def assert_passed(self, arg, msg=None):
        if arg != PASSED:
            raise TestFailError, msg or "Did not pass test."

    def assert_completed(self, arg, msg=None):
        if arg != COMPLETED:
            raise TestFailError, msg or "Did not complete test."

    def assert_failed(self, arg, msg=None):
        if arg != FAILED:
            raise TestFailError, msg or "Did not pass test."

    def assert_equal(self, arg1, arg2, msg=None):
        if arg1 != arg2:
            raise TestFailError, msg or "%s != %s" % (arg1, arg2)

    def assert_not_equal(self, arg1, arg2, msg=None):
        if arg1 == arg2:
            raise TestFailError, msg or "%s == %s" % (arg1, arg2)
    assert_notequal = assert_not_equal # alias

    def assert_true(self, arg, msg=None):
        if not arg:
            raise TestFailError, msg or "%s not true." % (arg,)

    def assert_false(self, arg, msg=None):
        if arg:
            raise TestFailError, msg or "%s not false." % (arg,)

    def assert_approximately_equal(self, arg1, arg2, fudge=None, msg=None):
        if fudge is None:
            fudge = arg1*0.05 # default 5% of arg1
        if abs(arg1-arg2) > fudge:
            raise TestFailError, msg or "%s and %s not within %s units of each other." % (arg1, arg2, fudge)

    def assert_match(self, list_arg, arg, msg=None):
        if type(list_arg) == str:
            list_arg = [list_arg]
        for t in list_arg:
            if not re.search(r"%s"%t, arg):
                raise TestFailError, msg or "Failed to match '%s' in given output." % (t)

    def assert_not_match(self, list_arg, arg, msg=None):
        if type(list_arg) == str:
            list_arg = [list_arg]
        for t in list_arg:
            if re.search(r"%s"%t, arg):
                raise TestFailError, msg or "Should not match '%s' in given output." % (t)


    # some logical aliases
    fail_if_equal = assert_not_equal
    fail_if_not_equal = assert_equal
    assert_not_true = assert_false
    assert_not_false = assert_true

    def get_output_from_last_step(self):
        """
        Returns the output from the previous step if there is any. 
        """
        if self._steps_output.has_key(len(self._steps_output)):
            return self._steps_output[len(self._steps_output)]
        else:
            return None

    def run_steps(self):
        self.__OUTPUT__ = [None] # first item should be empty, cause we count steps from 1
        self.__PARSED_VARS__ = {}
        i=1
        for step in self._steps:
            self.debug("*"*80)
            self.debug("STEP[%s]: %s"%(i, step.description))
            step._run()   #in case of any problems it should raise exception 
                          #(e.g. TestFailError if fail) which will be handled by upper class (rhtest)
            step.step_id=i
            self.debug("STEP[%s] - DONE"%i)
            self.debug("*"*80)
            self._steps_output[i]=step.get_output()
            i=i+1

        return self.passed()

    def add_step(self, description, command, function_parameters=None, expect_description="", expect_return=None, expect_str=None, expect_istr=None, unexpect_str=None, unexpect_istr=None, try_count=1, try_interval=5, output_filter=None, string_parameters=None):
        """
        Support for old testcase.TestCaseStep functionality

        expect_str: (either string or list )
            "expected string A"
            or
            ["expected string A", "expected string B"]
            or
            "/regular expression A/"
            or
            ["/regular expression A/", "regular expression B"]
            or
            ["expected string A", "regular expression B"]

            - returns TestStep object
        """
        self._steps.append(TestStep(self,
                                    description,
                                    command,
                                    function_parameters = function_parameters,
                                    expect_description = expect_description, 
                                    expect_return      = expect_return, 
                                    expect_str         = expect_str,
                                    expect_istr        = expect_istr,
                                    unexpect_str       = unexpect_str,
                                    unexpect_istr      = unexpect_istr,
                                    string_parameters  = string_parameters,
                                    try_interval       = try_interval,
                                    try_count          = try_count,
                                    output_filter      = output_filter))

        return self._steps[len(self._steps)-1]

class RhTestLogger(object):
    """

    """
    _ui = None
    _report = None

    def __init__(self, ui, report):
        self._ui = ui
        self._report = report

    def info(self, msg):
        self._ui.info(msg)
        self._report.info(msg)

    def debug(self, msg):
        self._ui.diagnostic(msg)
        self._report.diagnostic(msg)

    def diagnostic(self, msg):
        self._ui.diagnostic(msg)
        self._report.diagnostic(msg)

    def error(self, msg):
        self._ui.error(msg)
        self._report.error(msg)



class TestStep(object):
    '''
    Step definition
    '''
    output = None
    retstatus = None
    function_parameters_kwargs = None

    def __init__(self, rhtest_obj, description, command, function_parameters=None, expect_description="", expect_return=None, expect_str=None, unexpect_str=None, expect_istr=None, unexpect_istr=None, try_count=1, try_interval=5, output_filter=None, string_parameters=None):
        self.rhtest_obj = rhtest_obj
        self.info = rhtest_obj.info  #let's use the same info fnuction as rhtest for logging
        self.debug = rhtest_obj.debug #let's use the same info fnuction as rhtest for logging
        self.error = rhtest_obj.error #let's use the same info fnuction as rhtest for logging
        self.description = description
        self.command = command

        self.function_kw_parameters = None
        if (isinstance(string_parameters, str)):
            self.string_parameters = [string_parameters]
        else:
            self.string_parameters = string_parameters
        if (isinstance(function_parameters,str)):
            self.function_parameters = [function_parameters]
        elif (isinstance(function_parameters, list)):
            self.function_parameters = function_parameters  
        elif (isinstance(function_parameters, dict)):  #only for functions
            self.function_kw_parameters = function_parameters  
            self.function_parameters = None
        elif function_parameters is None:
            self.function_parameters = None
        else:
            raise TypeError("Invalid function_parameters - possible types=[None, str, list, dict]")

        self.expect_description = expect_description
        self.expect_return = expect_return
        self.expect_str = expect_str
        self.unexpect_str = unexpect_str
        self.expect_istr = expect_istr
        self.unexpect_istr = unexpect_istr
        self.try_count = try_count
        self.try_interval = try_interval
        self.output_filter = output_filter

    def get_output(self):
        return self.output

    def get_retstatus(self):
        return self.retstatus

    def __call__(self, *args, **kwargs):
        """
         Wrapper for _run() used by individual execution
           - returns (status, output)
           - throws exceptions only when this step requires checking (defined *expect_* parameters in add_step(*) method)
        """
        if args is not None and len(args)>0:
            self.function_parameters = args #overwrite default function_parameters
        self.function_parameters_kwargs = kwargs #merge/overwrite default function_parameters
        self.debug("-"*80)
        self.debug("STEP: %s"%(self.description))
        self.debug("-"*80)
        self._run()

        return (self.retstatus, self.output)

    def eval_parameters_list(self, parameters_list):
        self.debug('Eval parameters of string type...')
        temp = []
        if parameters_list is None:
            return
        for parameter in parameters_list:
            if isinstance(parameter, str):
                re_match_obj = re.match(r"^__OUTPUT__(\[[^\[\]]+\])+$", parameter)
                if re_match_obj != None:
                    parameter = parameter.replace("__OUTPUT__", "self.rhtest_obj.__OUTPUT__")
                    parameter = eval(parameter)
                else:
                    parameter = re.sub(r"__OUTPUT__(\[[^\[\]]+\])+", self.repl, parameter)
                #__PARSED_VARS__
                re_match_obj = re.match(r"^__PARSED_VARS__(\[[^\[\]]+\])+$", parameter)
                if re_match_obj != None:
                    parameter = parameter.replace("__PARSED_VARS__", "self.rhtest_obj.__PARSED_VARS__")
                    parameter = eval(parameter)
                else:
                    parameter = re.sub(r"__PARSED_VARS__(\[[^\[\]]+\])+", self.repl, parameter)
            else:
                pass
            temp.append(parameter)

        self.debug('Parameters after evaluation[1]: %s'%temp)
        return temp

    def repl(self, matchobj):
        if matchobj != None:
            self.debug('''Found '__OUTPUT__|__PARSED_VARS__' keyword, replace it''')
            #hack to avoid using global vars!
            s = matchobj.group(0).replace("__OUTPUT__", "self.rhtest_obj.__OUTPUT__")
            s = s.replace("__PARSED_VARS__","self.rhtest_obj.__PARSED_VARS__")
            return eval(s)

    def eval_command_string(self, command_line):
        #self.debug('Evaluating command string...')
        cmd_after_eval = re.sub(r"__OUTPUT__(\[[^\[\]]+\])+",  self.repl, command_line)
        cmd_after_eval = re.sub(r"__PARSED_VARS__(\[[^\[\]]+\])+",  self.repl, cmd_after_eval)
        #self.debug('Command after evaluation: %s'%cmd_after_eval)
        return cmd_after_eval

    def _run(self):
        """
        Executes the function or shell command.
            - returns nothing
            - used by Test.run_steps() - for internal calls 
            - throws exceptions when expected conditions fail (expect_return, ...)
        """
        if len(self.expect_description) > 0:
            self.debug("Expectation: %s"%self.expect_description)
        #try to EVAL __OUTPUT__ and PARSED__VARS__
        try:
            self.function_parameters = self.eval_parameters_list(self.function_parameters)
        except Exception as e:
            self.error(str(e))
            raise e
        try:
            #
            # let's try to exec functions/closeures if present
            #
            if self.function_parameters is not None:
                executed = False
                l_params = []
                for p in self.function_parameters:
                    if inspect.isfunction(p) or inspect.ismethod(p):
                        self.debug("Found closure! Execute `%s' parameter as function."%p)
                        res = p()
                        l_params.append(res)
                        executed = True
                    else:
                        l_params.append(p)

                self.function_parameters = l_params
                if executed:
                    self.debug("Parameters after evaluation[2]: %s"%self.function_parameters)
        except:
            self.debug("-"*80)
            traceback.print_exc(file=sys.stderr)
            self.debug("-"*80)
            raise TestIncompleteError("Unable to evaluate closures in %s"%self.function_parameters)

        attempts = self.try_count
        if isinstance(self.command, str) or isinstance(self.command, unicode):

            if self.string_parameters:
                self.debug("String %s expansion...")
                l_params = [] #for expansion
                for p in self.string_parameters:
                    if inspect.isfunction(p):
                        l_params.append(p())
                    else:
                        l_params.append(p)
                try:
                    #make a quoted string
                    #TODO: check what kind of quotes have been used and based on that make fixes
                    l_params = ",".join(map(lambda x: '"'+x+'"', l_params))
                    self.debug("String expansion/array before: %s"%l_params)
                    str2exec = 'self.command=self.command%%(%s)'%l_params
                    self.debug("String expansion/after: %s"%str2exec)
                    #and do the expansion...
                    exec(str2exec)
                except Exception as e:
                    self.error("Unable to expand command: %s"%str(e))
                    raise TestIncompleteError("Unable to string expansion in %s"%self.function_parameters)

            try:
                self.command = self.eval_command_string(self.command)
            except Exception as e:
                self.error("Error during evaluating shell string"%(str(e)))
                raise e

            self.debug("Executing SHELL: %s"%self.command)

            while True:
                command = self.command
                self.debug("Attempt #%d"%(self.try_count-attempts+1))
                if self.function_parameters is not None and len(self.function_parameters)>0:
                    for a in self.function_parameters:
                        command = command.replace("%s", a, 1)
                (self.retstatus, self.output) = cmd_get_status_output(command)
                attempts -= 1
                if attempts == 0:
                    break
                try:
                    self._verify_step(dry=True)
                    break
                except:
                    pass
                time.sleep(self.try_interval)

        elif inspect.isfunction(self.command) or inspect.ismethod(self.command):
            self.debug("Executing FUNCTION: %s"%self.command.__name__)
            while True:
                #TODO:start to intercept stdout/stderr
                self.debug("Attempt #%d"%(self.try_count-attempts+1))
                if self.function_parameters is not None and self.function_parameters_kwargs is not None:
                    self.retstatus = self.command(*self.function_parameters, **self.function_parameters_kwargs)
                elif self.function_parameters is not None:
                    self.retstatus = self.command(*self.function_parameters)
                elif self.function_parameters_kwargs is not None:
                    self.retstatus = self.command(**self.function_parameters_kwargs)
                else:
                    self.retstatus = self.command()

                attempts -= 1
                if attempts == 0:
                    break
                try:
                    self._verify_step(dry=True)
                    break
                except:
                    pass
                time.sleep(self.try_interval)
            self.output = "Fun_None_Output" #we cannot capture output

            #TODO:stop of interception

        #append output into __OUTPUT__ for legacy support
        try:
            if self.output == "Fun_None_Output":
                if (self.output_filter):
                    self.rhtest_obj.__OUTPUT__.append(self.filter_output(self.retstatus, self.output_filter))
                else:
                    self.rhtest_obj.__OUTPUT__.append(self.retstatus)
            else:
                if (self.output_filter):
                    self.rhtest_obj.__OUTPUT__.append(self.filter_output(self.output, self.output_filter))
                else:
                    self.rhtest_obj.__OUTPUT__.append(self.output)
        except:
            pass
        self._verify_step(dry=False)  #real verification...

 
    def _verify_step(self, dry=False):
        """
        Throws exceptions if given conditions are not met with requirements
        """
        #checking the return value
        if self.expect_return is not None:
            retstatus = self.retstatus
            # if it is array, let's check the first value...
            if isinstance(self.retstatus, list) or isinstance(self.retstatus, tuple):
                retstatus = self.retstatus[0]

            if isinstance(self.expect_return, list) or isinstance(self.expect_return, tuple):
                self.error("TODO: Not yet implemented")
                #TODO

            if isinstance(self.expect_return, int): 
                self.rhtest_obj.assert_equal(retstatus, 
                                             self.expect_return, 
                                             "Expected return: %d, got %s"%
                                                (self.expect_return, retstatus))
            elif isinstance(self.expect_return, unicode) or isinstance(self.expect_return, str): 
                obj = re.search(r"^!(\d+)",self.expect_return)
                if obj:
                    self.rhtest_obj.assert_not_equal(int(retstatus), 
                                                     int(obj.group(1)), 
                                                     "Expected return: %s, got %s"%
                                                        (self.expect_return, retstatus))
                else: #just compare two strings
                    self.rhtest_obj.assert_equal(retstatus,
                                                 self.expect_return, 
                                                 "Expected return: %s, got %s"%
                                                    (self.expect_return, retstatus))
            else:
                self.error("Unknown `expect_return` type: %s"%type(self.expect_return))
        else:
            self.debug("No checking of return value...")

        if self.output is None:
            self.output = ''
        #checking the return value
        if self.expect_str:
            if self.output == "Fun_None_Output":
                print "WARNING: Unable to check STDOUT from function call! Fix the script or ignore it if you do it intentionally."
            if isinstance(self.expect_str, str) or isinstance(self.expect_str, unicode):
                self.rhtest_obj.assert_match(self.expect_str, self.output, "Unable to find `%s` string in the output."%self.expect_str)
            if isinstance(self.expect_str, list):
                for s in self.expect_str:
                    self.rhtest_obj.assert_match(s, self.output, "Unable to find `%s` string in the output."%s)

        if self.unexpect_str:
            if self.output == "Fun_None_Output":
                print "WARNING: Unable to check STDOUT from function call! Fix the script or ignore it if you do it intentionally."
            if isinstance(self.unexpect_str, str) or isinstance(self.unexpect_str, unicode):
                self.rhtest_obj.assert_not_match(self.unexpect_str, self.output, "Unexpected match of `%s` in output."%self.unexpect_str)
            if isinstance(self.unexpect_str, list):
                for s in self.unexpect_str:
                    self.rhtest_obj.assert_not_match(s, self.output, "Unexpected match of `%s` in output."%s)

        #if there is no verification, let's notify the user
        if sum(map(self.__dict__.has_key, ('expect_str',
                                           'expect_istr',
                                           'expect_return',
                                           'unexpect_str',
                                           'unexpect_istr'))) == 0:
            self.info("Nothing to verify in this step -> just executed")
            self._nothing4checking = True


    def filter_output(self, output, filter_reg):
        if filter_reg != None:
            search_obj = re.search(r"%s" %(filter_reg), output, re.M)
            if search_obj != None:
                ret_output = search_obj.group(0)
                self.debug("According to output filter - [%s], return [%s]" %(filter_reg, ret_output))
            else:
                ret_output = ""
                self.debug("According to output filter - [%s], return empty string" %(filter_reg))
        else:
            ret_output = output
        return ret_output

                

class PreReq(object):
    """A holder for test prerequiste."""
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        return "%s(%r, %r, %r)" % (self.__class__.__name__, self.name, self.args, self.kwargs)

    def __str__(self):
        return repr_test(self.name, self.args, self.kwargs)


# holds an instance of a Test class and the parameters it will be called with.
# This actually calls the test, and stores the result value for later summary.
# It also supports pre-requisite matching.
class _TestEntry(object):
    def __init__(self, inst, args=None, kwargs=None):
        self.inst = inst
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.result = None

    def __call__(self):
        try:
            self.result = apply(self.inst, self.args, self.kwargs)
        except KeyboardInterrupt:
            self.result = ABORT
            raise
        return self.result

    def __eq__(self, other):
        return self.inst == other.inst

    def matches(self, name, args, kwargs):
        return (name, args, kwargs) == (self.inst._testname, self.args, self.kwargs)

    def match_prerequisite(self, prereq):
        "Does this test match the specified prerequisite?"
        return (self.inst._testname, self.args, self.kwargs) == (prereq.name, prereq.args, prereq.kwargs)

    def get_result(self):
        return self.result

    def prerequisites(self):
        return self.inst.prerequisites()

    def abort(self):
        self.result = self.inst.abort("Abort forced by suite runner.")
        return self.result

    def was_aborted(self):
        return self.result == ABORT

    def name(self):
        return self.inst._testname

    def get_values(self):
        return self.inst._testname, self.args, self.kwargs, self.result

    def __repr__(self):
        return repr_test(self.inst._testname, self.args, self.kwargs)

class _SuiteEntry(_TestEntry):
    def get_result(self):
        # self.result is a list in this case
        self.results = self.inst.results()
        for res in self.results:
               if res != PASSED:
                   return res
        return PASSED

def repr_test(name, args, kwargs):
    args_s = IF(args, 
        IF(kwargs, "%s, ", "%s") % ", ".join(map(repr, args)),
        "")
    kws = ", ".join(map(lambda it: "%s=%r" % (it[0], it[1]), kwargs.items()))
    return "%s()(%s%s)" % (name, args_s, kws)


class TestSuite(object):
    """TestSuite(config)
    A TestSuite contains a set of test cases (subclasses of Test class objects)
    that are run sequentially, in the order added. It monitors abort status of each
    test, and aborts the suite if required. 

    To run it, create a TestSuite object (or a subclass with some methods
    overridden), add tests with the 'add_test()' method, and then call the
    instance. The 'initialize()' method will be run with the arguments given when
    called.

    """
    def __init__(self, cf, nested=0):
        self.config = cf
        self.report = cf.report
        self._debug = cf.options.DEBUG
        self._verbose = cf.options.VERBOSE
        self._tests = []
        self._nested = nested
        self.suite_name = self.__class__.__name__
        self._testbed_needed = None
    
    def __iter__(self):
        return iter(self._tests)

    def set_config(self, cf):
        self.config = cf

    def add_test(self, _testclass, *args, **kw):
        """add_test(Test, [args], [kwargs])
        Appends a test object in this suite. The test's test_method() will be called
        with the arguments supplied here. If the test case has a prerequisite defined
        it is checked for existence in the suite, and an exception is raised if it is
        not found."""
        if _testclass.INTERACTIVE and self.config.flags.NOINTERACTIVE:
            print >>sys.stderr, "%s is an interactive test and NOINTERACTIVE is set. Skipping." % (_testclass.__name__,)
            return
        testinstance = _testclass(self.config)
        entry = _TestEntry(testinstance, args, kw)
        self._verify_new(entry)
        self._tests.append(entry)

    def _verify_new(self, entry):
        prereqs = entry.prerequisites()
        count = 0
        for prereq in entry.prerequisites():
            for te in self._tests:
                if te.match_prerequisite(prereq):
                    count += 1
        if count < len(prereqs):
            raise TestSuiteAbort, "unable to add test case %s, prerequisite not already added!" % (entry, )

    def add_suite(self, suite, *args, **kw):
        """add_suite(TestSuite, [args], [kwargs])
            Appends an embedded test suite in this suite. """
        if type(suite) is type(Test): # class type
            suite = suite(self.config, 1)
        else:
            suite.config = self.config
            suite._nested = 1
        self._tests.append(_SuiteEntry(suite, args, kw))
        suite.test_name = "%s%s" % (suite.__class__.__name__,len(self._tests)-1)
        return suite

    def add(self, klass, *args, **kw):
        """add(classobj, [args], [kwargs])
        Most general method to add test case classes or other test suites."""
        if issubclass(klass, Test):
            self.add_test(klass, *args, **kwargs)
        elif issubclass(klass, TestSuite):
            self.add_suite(klass, *args, **kwargs)
        else:
            raise ValueError, "TestSuite.add: invalid class type."

    def get_tests(self):
        """Return a list of the test objects currrently in this suite."""
        return self._tests[:]

    def get_test(self, name, *args, **kwargs):
        for entry in self._tests:
            if entry.matches(name, args, kwargs):
                return entry
        return None

    def info(self, msg):
        """info(msg)
        Put in informational message in the test report."""
        self.config.userinterface.info(msg)
        self.report.info(msg)

    def error(self, msg):
        self.config.userinterface.error("ERROR: %s" % msg)
        self.report.add_message("ERROR", msg)

    def prerequisites(self):
        """Get the list of prerequisites, which could be empty. Primarily
        used by nested suites."""
        return getattr(self, "PREREQISITES", [])
    

    # this is the primary way to invoke a suite of tests. call the instance.
    # Any supplied parameters are passed onto the suite's initialize()
    # method.
    def __call__(self, *args, **kwargs):
        try:
            self._initialize(args, kwargs)
            rv = self.run_tests()
        except TestSuiteWaived, rv:
            #nasty hack to  update TCMS if exception occurs in Suite()
            #TODO: implement update_testcaserun() in TestSuite() scope !!!
            try:
                self._tests[0].inst.update_testcaserun('WAIVED')
            except:
                pass
            self.error("Suite waived: %s" % (rv,))
            rv = WAIVED
        except TestSuiteAbort, rv:
            #nasty hack to  update TCMS if exception occurs in Suite()
            #TODO: implement update_testcaserun() in TestSuite() scope !!!
            try:
                self._tests[0].inst.update_testcaserun()
            except:
                pass
            self.error("Suite aborted: %s" % (rv,))
            traceback.print_exc(file=sys.stderr)
            rv = INCOMPLETE
        except Exception, rv:
            #if 1:
            #    ex, val, tb = sys.exc_info()
            #    debugger.post_mortem(ex, val, tb)
            #nasty hack to  update TCMS if exception occurs in Suite()
            #TODO: implement update_testcaserun() in TestSuite() scope !!!
            try:
                self._tests[0].inst.update_testcaserun()
            except:
                pass
            self.error("General Exception - aborted: %s" % (rv,))
            traceback.print_exc(file=sys.stderr)
            rv = INCOMPLETE
        finally:
            pass #self._finalize()
        # do finalize() regardless
        self._finalize()
        return rv
        #return PASSED # suite ran without exception...


    def _initialize(self, args, kwargs):
        """ TestSuite """
        self.report.add_heading("Test suite: %s" % self.__class__.__name__, 1)
        #setup the run_mode
        if self.config.instance_info['ip'] == 'int.openshift.redhat.com':
            self.config.options.run_mode = 'INT'
        elif self.config.instance_info['ip'] == 'stg.openshift.redhat.com':
            self.config.options.run_mode = 'STG'
        elif self.config.instance_info['ip'] == 'openshift.redhat.com':
            self.config.options.run_mode = 'PROD'
        elif self.config.instance_info['ip'].find("example.com") != -1 or self.config.instance_info['ip'].find("test.com") != -1 or self.config.instance_info['ip'].find("broker") != -1: 
            self.config.options.run_mode = 'OnPremise'
        else: 
            self.config.options.run_mode = 'DEV'

        self.verify_testbed()
        #if self._testbed_needed:
        #    self.report.add_message("TESTBED", self.config.testbed.name)
        # initialize the suite
        try:
            rv = self.initialize(*args, **kwargs)
        except KeyboardInterrupt:
            self.info("Suite aborted by user in initialize().")
            raise TestSuiteAbort
        except:
            ex, val, tb = sys.exc_info()
            if self._debug:
                ex, val, tb = sys.exc_info()
                debugger.post_mortem(ex, val, tb)
            self.error("Suite failed to initialize: %s (%s)" % (ex, val))
            raise TestSuiteAbort, val
        # run all the tests

    # verify any prerequisites are met at run time. Note that this
    # currently only checks this particular suite.
    def check_prerequisites(self, currententry, upto):
        for prereq in currententry.prerequisites():
            for entry in self._tests[:upto]:
                if entry.match_prerequisite(prereq):
                    if entry.result == PASSED:
                        continue
                    else:
                        self.report.add_heading(repr(currententry), 2)
                        self.info("WARNING: prerequisite of %s did not pass." % (currententry,))
                        self.info("%s: %s" % (prereq, entry.result))
                        currententry.abort()
                        return False
        return True # no prerequisite
    
    def testbed_will_work(self, itest):
        """
        check if the ITEST directive matches the ip.  
        for PROD only ip that contains openshift.redhat.com will work
        for STG: only ip that contains stg.openshift.redhat.com will work
        """
        if itest == None:
            raise Exception("Unable to check testbed. ITEST property is not defined.")

        tb_will_work = False
        env_list = []
        if isinstance(itest,str):
            env_list.append(itest)
        elif isinstance(itest,list):
            env_list = itest
        else:
            raise Exception("Unknown ITEST type. Only str|list types are supported.")
            
        for env_type in env_list:
            if env_type:
                if env_type == 'PROD':
                    if 'openshift.redhat.com' in self.config.instance_info['ip']:
                        tb_will_work = True
                        break
                elif env_type == 'INT':
                    if 'int.openshift.redhat.com' in self.config.instance_info['ip']:
                        tb_will_work = True
                        break
                elif env_type == 'STG':
                    if 'stg.openshift.redhat.com' in self.config.instance_info['ip']:
                        tb_will_work = True
                        break
                elif env_type == 'DEV':
                    if self.config.instance_info['ip'] not in ('stg.openshift.redhat.com', 'int.openshift.redhat.com','openshift.redhat.com' ):
                        tb_will_work = True
                        break
            elif env_type is None:
                tb_will_work = True
                break

        return tb_will_work

    def verify_testbed(self):
        for entry in self._tests:
            if entry.inst.ITEST and not self.testbed_will_work(entry.inst.ITEST):
                reason = "Test can't run in this environment"
                raise TestSuiteWaived, "Cannot use testbed %s: %s" % (entry.inst.ITEST, reason)

    def run_tests(self):
        rv = PASSED
        for i, entry in enumerate(self._tests):
            if not self.check_prerequisites(entry, i):
                continue
            try:
                # XXX  put back later
                #self.config.logfile.note("%s: %r" % (timelib.localtimestamp(), entry))
                """
                print entry.args, len(entry.args)
                if len(entry.args) > 0:
                    self.config.tc_args = eval(entry.args[0])
                else:
                    self.config.tc_args = {}
                """
                rv = entry()
            except KeyboardInterrupt:
                self.info("Test suite aborted by user.")
                rv = ABORT
                if self._nested:
                    raise TestSuiteAbort, "aborted by user"
                else:
                    break
            except TestSuiteAbort, err:
                self.info("Suite aborted by test %s (%s)." % (entry.name(), err))
                rv = ABORT
            # this should only happen with incorrectly written test_method().
            if rv is None:
                self.report.diagnostic("warning: test returned None, assuming failed. Please fix the %s.test_method()" % (entry.name()))
                rv = FAILED
            # keep return value in results
            # check for abort condition and abort if so
            if rv == ABORT:
                break
        if self.config.options.TCMS:
            # mark test suite as finish and add the total time
            testrun_id = self.config.testrun_res[0]['run_id']
            tcms = self.config.tcms_obj
            params = {'status': 1, 'estimated_time': self.config.total_time }
            tcms.update_testrun(testrun_id, params),

        return rv

    def _finalize(self):
        # finalize the suite
        try:
            self.finalize()
        except KeyboardInterrupt:
            if self._nested:
                raise TestSuiteAbort, "Suite '%s' aborted by user in finalize()." % (self.suite_name,)
            else:
                self.info("Suite aborted by user in finalize().")
        except:
            ex, val, tb = sys.exc_info()
            if self._debug:
                debugger.post_mortem(ex, val, tb)
            self.info("Suite failed to finalize: %s (%s)" % (ex, val))
            if self._nested:
                raise TestSuiteAbort, "subordinate suite '%s' failed to finalize." % (self._tests[self._testname],)
        self._report_summary()

    def _report_summary(self):
        ui = self.config.userinterface
        self.report.add_heading("Summarized results for %s." % self.__class__.__name__, 2)
        ui.Print("Summarized results for %s." % self.__class__.__name__)
        
        msg = []
        for entry in self._tests:
            res = entry.get_result()
            if res == PASSED:
                msg.append("%50s: PASSED" % (entry,))
                ui.printf("%50s: %%GPASSED%%N" % (entry,))
            elif res == FAILED:
                msg.append("%50s: FAILED" % (entry,))
                ui.printf("%50s: %%RFAILED%%N" % (entry,))
            elif res == INCOMPLETE:
                msg.append("%50s: INCOMPLETE" % (entry,))
                ui.printf("%50s: %%YINCOMPLETE%%N" % (entry,))
            elif res == COMPLETED:
                msg.append("%50s: COMPLETED" % (entry,))
                ui.printf("%50s: %%GCOMPLETED%%N" % (entry,))
            elif res == ABORT:
                msg.append("%50s: ABORTED" % (entry,))
                ui.printf("%50s: %%yABORTED%%N" % (entry,))
            elif res is None:
                pass # test case did not run
            else:
                msg.append("%50s: strange test result value of: %s" % (entry, res))
        msg.append("%50s %.2f seconds" % ('SUITETIME:', self.config.total_time))
        msg.append("\n")
        ui.printf("%50s  %.2f seconds" % ('SUITETIME:', self.config.total_time))
        self.report.add_summary("\n".join(msg))

    def results(self):
        return map(lambda t: t.get_result(), self._tests)

    def __str__(self):
        s = ["Tests in suite:"]
        s.extend(map(str, self._tests))
        return "\n".join(s)

    ### overrideable interface.
    def initialize(self, *args):
        """Override this if you need to do some initialization just before the
suite is run. """ 
        pass

    def finalize(self, *args):
        """Override this if you need to do some clean-up after the suite is run."""
        try:
            if self.config.tcms_testcaserun_id is not None:
                sys.stdout.flush()
                sys.stderr.flush()
                time.sleep(2) #we need a time to flush the buffers for tee from launcher.py?
                f = open("%s/curr_tc_log.%s"%(get_tmp_dir(), self.config.tcms_testcaserun_id), 'r')
                log = f.read()
                self.info("<html>%s</html>" % log)
                f.close()
            else:
                self.info('Run manually - not by launcher.py => the stderr/stdout will not be included into the report.')
        except:
            pass

#######################
# helper functions
#######################

def underscore_to_camelcase(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))
 
def convert_script_to_cls(name):
    """
    convert a test script name as stored in TCMS and convert it into a class
    that can be added by add_test()
    XXX: due to inconsistent naming conventions between filename 
        for example:  quick_start_redmine.py vs the class name defined in the 
            testscript itself QuickStartRedmine
        we need to either have a naming convention in place and fix the exisiting
        scripts.  This function will help to guess the class name to import
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod_list = dir(mod)
        cls_name = underscore_to_camelcase(comp)
        mod = getattr(mod, comp)
        
    cls_list = dir (mod)
    try:
        klass = getattr(mod, cls_name)
    except:
       # crude hack.
       klass = getattr(mod, cls_list[0])
    return klass

#######################
# helper functions
#######################

def extract_tests_from_json_file(json_file):
    """
    
    """
    import json
    tests = []
    json_text = open(json_file, 'r')
    json_data = json.load(json_text)
    for data in json_data:
        converted_name = data['script'].replace("/", '.').split('.py')[0]
        args = data['arguments']
        tests.append((converted_name, args))
        """
        if data['arguments']:
            testcase_variants = eval(data['arguments']).__getitem__('variants')
            testcase_arg_dict[data['case_id']] = testcase_variants
        """
    return (tests)


# A test module may use "from qatest import *" and get these default
# initialize/finalize functions. These are run as module-level initialize and
# finalize by the testrunner module.

def initialize(conf):
    pass

def finalize(conf):
    pass

if __name__ == "__main__":
    #os.system("qaunittest test_stratatest")
    #val = underscore_to_camelcase('sending_email')
    val = convert_script_to_cls('Collections.Demo.demo_03')
    print val

