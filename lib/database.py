#!/usr/bin/env python
"""
database support library

"""

from sqlobject import *
from sqlobject.sqlbuilder import Select, func
import json
import time
import datetime
global sqlhub
logdb = 'localhost'
#logdb  = 'ec2-50-17-200-67.compute-1.amazonaws.com'

__all__ = ['TestResults', 'LibraAmis', 'PerfManifest', 'PerfResults',
 
           # Misc classes/functions.
           'connect2db', 'disconnect',
           ]
BUILD_DBURI="mysql://ruser:lab@%s/reports" % logdb
#DBURI="mysql://ruser:lab@%s/Openshift" % "localhost" 
DBURI="mysql://ruser:lab@%s/Openshift" % "10.14.16.138" 

TEST_RUN_STATUS = {'RUNNING' : 0, 'FINISHED' : 1}
CASE_RUN_STATUS = {'IDLE':1,'PASSED':2,'FAILED':3, 'RUNNING':4, 'PAUSED':5, 
    'BLOCKED':6,'ERROR':7, 'WAIVED':8}

def connect2db(uri=DBURI):
    global sqlhub
    if not hasattr(sqlhub, "processConnection"):
        connection = connectionForURI(uri)
        sqlhub.processConnection = connection
    return sqlhub.processConnection

def disconnect():
    global sqlhub
    if hasattr(sqlhub, "processConnection"):
        conn = sqlhub.processConnection
        del sqlhub.processConnection

class TestResults(SQLObject):
    AmiID = StringCol()                               # AMI that the instance is based on. 
    TestName = StringCol()                            # Name of the test that was run  AMI that the instance is based on.
    StartTime = DateTimeCol()                         # The date and time that the test was started. 
    EndTime = DateTimeCol()                           # The date and time that the test was completed. This is the time that the script wrote a P/F/I result into this record.
    TestbedID = StringCol()                     # the ip of the instance 
    TestScript = StringCol()                    # need this?? 
    #ConfigFile = StringCol()                          # A file pointer to the test configuration file that was used during the test.
    ResultsDataFile = StringCol()                     # File pointer. If a lengthy report or text file of data is produced during the test iterations, the results from all iterations are stored in a single file. NULL if none.
    User = StringCol()                                # Name of the user that ran the test
    Comments = StringCol()                            # User comments about the test
    PassFail = EnumCol(enumValues=["P", "F", "I","A"])    # The test PASS/FAIL result. P=PASS, F=FAIL, I=INCOMPLETE
    BuildVersion = StringCol()                    # DSP sw version
    RunMode = StringCol()
    TcmsTag = StringCol()
    TcmsTestCaseId = IntCol()
    TcmsTestCaseRunId = IntCol()
    TcmsTestRunId = IntCol()

class LibraAmis(SQLObject):
    ami_id = StringCol()
    #provider = ('Provider')  # 
    build_version = StringCol()     # ami ID
    ami_time = DateTimeCol()    # when the ami was created.        

class PerfManifest(SQLObject):
    action = StringCol()
    cartridge = StringCol()

class PerfResults(SQLObject):
    TestResultsID       = IntCol() #ForeignKey("TestResults")
    ActionID            = IntCol() #ForeignKey("PerfManifest")
    ActionTime          = FloatCol()  # seconds the action took
    GearSize            = IntCol()

class TcmsTags(SQLObject):
    plan_id = IntCol()
    tcms_id =   IntCol()
    name = StringCol()
    tc_count = IntCol()
    tag_json = BLOBCol()

class TcmsTestcases(SQLObject):
    plan_id = IntCol()
    case_id = IntCol()
    case_json = BLOBCol()  # dict is reprsented as JSON 

class TcmsTestRun(SQLObject):
    plan = IntCol()
    #errata_id = IntCol()
    manager = IntCol()
    summary = StringCol()
    product = IntCol()
    product_version = IntCol()
    default_tester = IntCol()
    plan_text_version = IntCol()
    estimated_time = StringCol()
    notes = StringCol()
    status = IntCol()
    case_list = StringCol()
    tag_list = StringCol()
    migrated = IntCol()    # default to 0, migrated = 1 if user migrated the result back into tcms after tcms server is back online
    launched_time = DateTimeCol()

class TcmsTestcaseRun(SQLObject):
    run = IntCol()
    case_id = IntCol()
    build = IntCol()
    assignee = IntCol()
    case_run_status = IntCol()
    case_text_version = IntCol()
    notes = StringCol()
    sortkey = IntCol()
    migrated = IntCol()  # default to 0, migrated = 1 if user migrated the result back into tcms after tcms server is back online





class ConfigDefaults(SQLObject):
    name            = StringCol()
    value           = StringCol()

###### helper function

def ami_in_db(ami_id):
    """
    return true if the ami_id exists in table already, false otherwise.

    """
    connect2db()
    tbl = LibraAmis
    sql = tbl.select(tbl.q.ami_id==ami_id)
    res = list(sql)
    if len(res) > 0:
        return True
    else:
        return False

def get_ami_info(ami_id):
    connect2db()
    tbl = LibraAmis
    sql = tbl.select(tbl.q.ami_id==ami_id)
    res = list(sql)
    if len(res) > 0:
        return res[0]
    else:
        return None

def get_stg_ami(pattern='devenv-stage_'):
    connect2db()
    tbl = LibraAmis
    sql = tbl.select(tbl.q.build_version.startswith(pattern)).orderBy('ami_time').reversed()
    res = list(sql)[0]
    return res
"""
def get_perf_action_id(action):
    connect2db()
    tbl = PerfManifest
    sql = tbl.select(tbl.q.action==action)
    res = list(sql)
    if (len(res) == 0):
        # nothing found, insert it
        res = PerfManifest(action=action)
        return res[0]
    else:
        return res[0]
"""
def get_perf_action_id(action, cartridge=None):
    connect2db()
    tbl = PerfManifest
    sql = tbl.select(AND(tbl.q.action==action, tbl.q.cartridge==cartridge))
    res = list(sql)
    if (len(res) == 0):
        res = PerfManifest(action=action, cartridge=cartridge)
        print #################
        return res.id
    else:
        return res[0].id
    
def record_results(resid, res_dict):
    #self.info("xx", 1)
    for k, v in res_dict.items():
        # first check to see if the performance action exists
        action = get_perf_action_id(k)
        res  = PerfResults(TestResultsID=resid, ActionID=action.id, 
                           ActionTime=v[0], GearSize=v[1])
        print res.id

def get_defaults():
    connect2db()
    tbl = ConfigDefaults
    sql = tbl.select()
    res_list = list(sql)
    configs = {}
    for res in res_list:
        configs[res.name] = res.value

    return configs

def populate_tcms_testcases_by_tag(tcms_obj, tag):
    """ 
    save the json tag into mysql 

    """
    connect2db()
    tbl = TcmsTags
    test_plan_id = tcms_obj.plan_id
    testcase_json, tc_count = tcms_obj.dump_testcases_to_json_by_tag(tag['name'])
    # check to see if that exists in DB, insert it if not
    sql = tbl.select(AND(tbl.q.name==tag['name'], tbl.q.tcms_id==tag['id']))
    res = list(sql)
    if len(res):
        # exist already just update the json field and count
        res[0].tag_json = testcase_json
        res[0].tc_count = tc_count 
    else:
        print "Row does not exist...adding..."
        TcmsTags(
                plan_id=test_plan_id,
                tcms_id=tag['id'],
                name = tag['name'],
                tc_count = tc_count,
                tag_json = testcase_json
                )
        
def populate_tcms_testcases(testcase_dict, plan_id=4962):
    connect2db()
    tbl = TcmsTestcases
    testcase_json = json.dumps(testcase_dict)
    sql = tbl.select(tbl.q.case_id == testcase_dict['case_id'])
    res = list(sql)
    if len(res):
        res[0].case_json = testcase_json
    else:
        res = tbl(plan_id=plan_id,
                case_id=testcase_dict['case_id'],
                case_json = testcase_json)
    return res
        
    
def get_testcases_json_by_tag(tag_name):
    """
    return the testcases represented in JSON given a tag_name
    """
    connect2db()
    tbl = TcmsTags
    sql = tbl.select(tbl.q.name==tag_name)
    res = list(sql)
    if len(res):
        return res[0].tag_json
    else:
        print "No information found in mysql for tag '%s'" % tag_name
        return None

def extract_testcase_ids_from_json(json_data, params=None):
    """ given a json formated testcase data, extract all of the testcase ids
    user can filter out cases by providing the params with parameters to filter
    params = {'is_automated': 1, 'case_status' : 'CONFIRMED'}
    """
    testcase_data = json.loads(json_data)
    tc_id_list = []
    for testcase in testcase_data:
        if params:
            match = 1
            for param in params.items():
                if testcase[param[0]] != param[1]:
                    match = 0
                    break
            if match:
                tc_id_list.append(testcase['case_id'])
        else:
            tc_id_list.append(testcase['case_id'])
    return tc_id_list

def get_testcase_ids_by_tag(tag_names, params=None):
    """ params contains parameters user wish to return testcase to be filtered
    by: for example... params = {'is_automated': 1, 'case_status' : 'CONFIRMED'}
    will only return testscases that are marked automated and confirmed 
    """
    tc_list = []
    for tag_name in tag_names:
        json_data = get_testcases_json_by_tag(tag_name)
        tc_list = tc_list + extract_testcase_ids_from_json(json_data, params)
    return tc_list

def get_testcase_by_id(case_id):
    
    connect2db()
    tbl = TcmsTestcases
    sql = tbl.select(tbl.q.case_id == case_id)
    res = list(sql)
    if len(res):
        tc_dict = json.loads(res[0].case_json)
        
        return tc_dict
    else:
        print "No testcase id '%s' found in database" % case_id
        return None
    
def get_all_tcms_testcases():
    connect2db()
    testcases = []
    tbl = TcmsTestcases
    sql = tbl.select()
    results = list(sql)
    for res in results:
        test = {}

        details = json.loads(res.case_json)
        test['id'] = res.id
        test['details'] = details
        testcases.append(test)
    return testcases

def get_testcase_run_id_from_db(test_run_id, tcms_testcase_id):
    """
    given a test_run id and tcms_testcase_id, return the testcase_run id in db
    """
    connect2db()
    tbl = TcmsTestcaseRun
    sql = tbl.select(AND(tbl.q.case_id==tcms_testcase_id, tbl.q.run==test_run_id))
    results = list(sql)
    if results:
        return results[0].id
    else:
        return None


def create_tcms_testrun(params = None):
    """
    create an new entry into the mysql database for a testrun that will eventually
    store back into TCMS once the server is back-online
    """
    connect2db()
    tbl = TcmsTestRun
    launched_time = datetime.datetime.fromtimestamp(time.time())
    default_params= {
            'plan' : 4962,
            'manager' : 2351,

            'summary' : 'Automated summary',
            'product' : 292,
            'product_version' : 1212,
            'default_tester' : 2955,
            'plan_text_version' : 1,
            'estimated_time' : '00:00:00',
            'notes' : 'automated notes',
            'status' : 0, 
            'case_list' : None,
            'tag_list' : None,
            'migrated' : 0,
            'launched_time': launched_time,
        }

    if params is None:
        params = default_params

    else:
        for k, v in params.items():
            default_params[k] = params[k]

        params = default_params

    res = tbl(
        plan = params['plan'],
        manager = params['manager'],
        summary = params['summary'],
        product = params['product'],
        product_version = params['product_version'],
        default_tester = params['default_tester'],
        plan_text_version = params['plan_text_version'],
        estimated_time = params['estimated_time'],
        notes = params['notes'],
        status = params['status'],
        case_list = params['case_list'],
        tag_list = params['tag_list'],
        migrated = params['migrated'],
        launched_time=params['launched_time'],
        )
            
    return res

def update_testrun(testrun_id, params):
    tbl = connect2db()
    tbl = TcmsTestRun
    res = tbl.select(tbl.q.id == testrun_id)
    if res:
        for k, v in params.items():
            res[0].__setattr__(k, v)

    
    return res

def create_tcms_testcase_run(params = None):
    """
    create an new entry into the mysql database for a testrun that will eventually
    store back into TCMS once the server is back-online
    """
    connect2db()
    tbl = TcmsTestcaseRun
    default_params= {
            'assignee' : 2351,
            'case_run_status' : 1,  # IDLE
            'case_text_version' : 1,
            'notes' : 'TBD',
            'sortkey': 0,
            'migrated' : 0,
            'build': 1770,
        }

    if params is None:
        params = default_params

    else:
        for k, v in params.items():
            default_params[k] = params[k]

        params = default_params

    res = tbl(
        run = params['run'],
        case_id = params['case_id'],
        build = params['build'],
        assignee = params['assignee'],
        case_run_status = params['case_run_status'],
        case_text_version = params['case_text_version'],
        notes = params['notes'],
        sortkey = params['sortkey'],
        migrated = params['migrated'])
            
    return res

def update_testcase_run(testcase_run_id, params):
    tbl = connect2db()
    tbl = TcmsTestcaseRun
    res = tbl.select(tbl.q.id == testcase_run_id)
    if res:
        for k, v in params.items():
            res[0].__setattr__(k, v)
    return res

def update_testcaserun_status(test_run_id, tcms_testcase_id, status):
    run_status = CASE_RUN_STATUS[status]
    params = {'case_run_status': run_status}
    db_testcase_run_id = get_testcase_run_id_from_db(test_run_id, tcms_testcase_id)
    res = update_testcase_run(db_testcase_run_id, params)
    return res

def get_latest_test_result():
    tbl = connect2db()
    tbl = TestResults
    id_count = tbl.select().reversed().count()
    res = tbl.select(tbl.q.id==id_count)[0]
    return res


def _test():
    cart_types = ['php-5.3', 'ruby-1.8']
    domain_action = ['domain_create', 'domain_', 'domain_delete']
    app_action = ['app_start', 'app_stop', 'app_reload', 'app_restart']
    
    for cart in cart_types:
        for action in app_action:
            id = get_perf_action_id(action, cart)
            print "ID: %s" % id
            
if __name__ == '__main__':
    #_test()

    #val = get_defaults()
    #val = get_stg_ami()
    ##res_dict = {'create_domain': 4.3, 'delete_domain': 3.1}
    #res = get_testcase_by_id(122349)
    #update_tcms_testrun(18, {'status': 0})
    #res = create_tcms_testcase_run({'run': 3, 'case_id': 122349})
    #res = create_tcms_testrun({'notes': "This is a test"})
    ##record_results(50, res_dict)
    #res  = get_testcases_json_by_tag('origin')
    #params = {'is_automated': 1, 'case_status': 'CONFIRMED'}
    #res = get_testcase_ids_by_tag(["origin"], params=params)
    #get_testcase_run_id_from_db(21, 122166)
    get_test_result_status()
    self.info("xxx", 1)
    pass
