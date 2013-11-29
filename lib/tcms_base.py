#!/usr/bin/env python

"""
test TCMS python module

"""
import os
import sys
import datetime as dt
from nitrate import NitrateKerbXmlrpc
from datetime import timedelta
import datetime
import time
import json
from StringIO import StringIO
import database

#PROD = 'OpenShift Flex'
IDLE   = 1
PASSED = 2
FAILED = 3

RUNNING = 0
FINISHED = 1

TEST_RUN_STATUS = {'RUNNING' : 0, 'FINISHED' : 1}
CASE_RUN_STATUS = {'IDLE':1,'PASSED':2,'FAILED':3, 'RUNNING':4, 'PAUSED':5, 
    'BLOCKED':6,'ERROR':7, 'WAIVED':8}

class RunStatus(object):
    IDLE, PASSED, FAILED, RUNNING, PAUSED, BLOCKED, ERROR, WAIVED = range(1,
            9)

def run_kinit():
    tcms_user = os.getenv('TCMS_USER')
    tcms_passwd = os.getenv('TCMS_PASSWORD')
    if (tcms_user is None) or (tcms_passwd is None):
        raise Exception("Missing TCMS login information in your env variables...")
    ret_code = os.system("echo \"%s\" | kinit %s" % (tcms_passwd, tcms_user))
    if ret_code != 0 :
        print "Error: kinit failed!, ret_code is: %s" % ret_code



class TCMS(object):
    ns = None
    test_plan_cases = None # total number ot testcases with this testplan
    prod_name = 'OpenShift 2.0'
    #prod_name = 'OpenShift Flex'
    host = 'https://tcms.engineering.redhat.com/xmlrpc/'
    #test_plan_name = 'Test Plan for OpenShift 2.0'
    test_plan_name = 'PPP_sandbox3'
    tcms_time =  datetime.datetime.now()
    plan_id = None
    #tcms_time =  datetime.datetime.now() + timedelta(hours=15)

    def __init__(self, product=None, test_plan=None, host=None):
        run_kinit()
        if product:
            self.prod_name = product
        if host:
            self.host = host
        if test_plan:
            self.test_plan_name = test_plan
         
        # do a kinit just in case.
        n = NitrateKerbXmlrpc(self.host)
        self.ns = n.server
        # get product information
        print ("Getting information from testplan '%s'" % self.test_plan_name) 
        #self.info("xxx", 1)
        self.test_plan = self.ns.TestPlan.filter({'name': self.test_plan_name})[0]
        self.plan_id = self.test_plan['plan_id']
        self.builds = self.get_builds()
        ### for a testplan with many cases, this can take a while, don't do it on init
        #self.test_plan_cases = self.ns.TestPlan.get_test_cases(self.test_plan['plan_id'])
        #print("TestPlan '%s', Number of testcases: %s" % (test_plan, len(self.test_plan_cases))) 

    def get_test_runs(self, plan_id=None):
        if plan_id == None:
            plan_id = self.test_plan['plan_id']

        runs = self.ns.TestPlan.get_test_runs(plan_id)
        return runs
    
    def get_product_version_id(self):
        prod_version_id = None
        versions = self.ns.Product.get_versions(self.test_plan['product_id'])
        for version in versions:
            if version['value'] == self.test_plan['default_product_version']:
                prod_version_id = version['id']
        return prod_version_id
        
    def get_components(self):
        components = self.ns.Product.get_components(self.prod_name)
        return components

    def get_builds(self):
        builds = self.ns.Product.get_builds(self.prod_name)
        return builds
    
    def create_build(self, params):
        return self.ns.Build.create(params)


    def get_build_id(self, build_name):
        res = self.ns.Build.check_build(build_name, self.prod_name)
        if res.has_key('args'): 
            build_id = None
        else:
            build_id = self.ns.Build.check_build(build_name, self.prod_name)['build_id']
        return build_id

    def check_and_insert_build(self, build_name):
        """ helper function, insert a build by name if it does not exists in
        TCMS """
        build_id = self.get_build_id(build_name)
        if build_id:
            return build_id
        else:
            # no build match found, insert it.
            build_params = {'product': self.prod_name, 'name': build_name,
                    'description': build_name}
            return self.create_build(build_params)

    def get_testcases_by_plan(self, plan_name, params):
        filter_dict = {'plan__name': plan_name}
        filter_dict = dict(filter_dict.items() + params.items())
        ts_list = self.ns.TestCase.filter(filter_dict)
        print("There is a total of %s testcases within plan %s" % (len(ts_list),
                filter_dict['plan__name']))
        return ts_list
    
    def get_testcases(self, params={}):
        ts_list = self.get_testcases_by_plan(self.test_plan_name, params)
        self.testcases = ts_list
        return ts_list
    
    TestCases = property(get_testcases, None)


    def get_testcases_by_tag(self, tag_name, params=None):
        filter_dict = {'tag__name': tag_name, 'plan__name': self.test_plan_name}
        #filter_dict = {'tag__name': tag_name, 'plan': self.plan_id}
        res = self.ns.TestCase.filter(filter_dict)
        return res

    def get_testscripts_by_tag(self, tag_name):
        test_scripts = []
        filter_dict = {'tag__name': tag_name, 'plan__name': self.test_plan_name}
        #filter_dict = {'tag__name': tag_name, 'plan': self.plan_id}
        tests = self.ns.TestCase.filter(filter_dict)
        for test in tests:
            script =  test['script'].split('.py')[0].replace("/", ".")
            args = test['arguments']
            case_id = test['case_id']
            test_scripts.append((script, args, case_id))
        return test_scripts

    def get_test_runs_by_build(self, build_name):
        build_id = self.get_build_id(build_name)
        runs = self.ns.Build.get_runs(build_id)
        return runs


    def get_testcases_by_components(self, comp_name):
        plan_id = self.test_plan['plan_id']
        filter_dict = {'component__name': comp_name, 'plan': plan_id}
        #testcases = {}
        ts_list = self.ns.TestCase.filter(filter_dict)
        print("Component: %s, testcases: %s" % (comp_name, len(ts_list)))
        return ts_list

    def get_testcase_by_script_name(self, script_name):
        plan_id = self.test_plan['plan_id']
        filter_dict = {'script' : script_name}
        ts_list = self.ns.TestCase.filter(filter_dict)
        print("ts_list: %s" % ts_list)
        return ts_list[0]

    def get_case_ids_by_components(self, comp_name):
        """ return a list of testcases's id """
        tc_list = self.get_testcases_by_components(comp_name)
        tc_id_list = []
        for tc in tc_list:
            tc_id_list.append(tc['case_id'])
        return tc_id_list

    def get_testcases_with_variants(self):
        """
        return a list of testcases that contain the variants in its argument
        XXX: unfortunately, TestCase.filter does not support arguments yet.
        """
        plan_id = self.test_plan['plan_id']
        filter_dict = {'arguments__icontain': 'variants', 'plan': plan_id}
        ts_list = self.ns.TestCase.filter(filter_dict)
        return ts_list

    def get_testcase_arguments(self, testcase_id):
        res = self.ns.TestCase.get(testcase_id)
        variants = []
        if res['arguments']:
            arg = eval(res['arguments'])
            if arg.has_key('variants'):
                variants = arg['variants']
        return variants

    def get_variants_mapping(self, testcase_ids):
        testcase_variants = {}
        print testcase_ids
        for testcase_id in testcase_ids:
            if testcase_id:
                variants = self.get_testcase_arguments(testcase_id)
                if len(variants) > 0:
                    testcase_variants[testcase_id] = variants
        return testcase_variants


    def get_plan_runs(self, plan_name):
        # first get plan info
        plan_dict = self.ns.TestPlan.filter({'name': plan_name})[0]
        plan_id = plan_dict['plan_id']
        test_runs = self.ns.TestPlan.get_test_runs(plan_id)
        self.test_plan_cases = self.ns.TestPlan.get_test_cases(plan_id)
        return test_runs
    

    def get_daily_runs(self, target_date=None):
        """ return all the runs done on a daily bases, the the target_date is
        empty, then default to to 
            XXX: please note that the server is based in Beijing, China...so 
            have to take care of time difference
        """
        tcms_time = self.tcms_time

        if target_date is None:
            # default to today, but since the data server is located in
            # Beijing, we need to compensate, for the first cut, assume we are
            # running the job in California, so the difference is 15 hrs.
            end_date = (tcms_time + timedelta(days=1)).strftime("%Y-%m-%d")
            start_date = tcms_time.strftime("%Y-%m-%d")
        else:
            date_format = "%Y-%m-%d"
            start_date = target_date
            sd = datetime.datetime.strptime(target_date, date_format)
            end_date = (sd + datetime.timedelta(days=1)).strftime(date_format)

        run_filter = {
            'plan' : self.test_plan['plan_id'], 
            #'stop_date__gte': (start_date)
            'stop_date__range': (start_date, end_date)
            }
        print("%s" % run_filter)
        daily_runs = self.ns.TestRun.filter(run_filter)

        return daily_runs

    Components = property(get_components)
    Builds = property(get_builds)
    #TestPlan = property(get_test_plan)
    
    def create_testrun(self, test_id_list, build_version, summary, test_run_id=None):
        """
        can be used by test scripts to create a test run into TCMS system.
        each individual testcase run is attached to a top level test run and
        therefore a TestRun entry into the system is needed 
        
  +-------------------+----------------+-----------+------------------------------------+
  | Field             | Type           | Null      | Description                        |
  +-------------------+----------------+-----------+------------------------------------+
  | plan              | Integer        | Required  | ID of test plan                    |
  | build             | Integer/String | Required  | ID of Build                        |
  | manager           | Integer        | Required  | ID of run manager                  |
  | summary           | String         | Required  |                                    |
  | product           | Integer        | Required  | ID of product                      |
  | product_version   | Integer        | Required  | ID of product version              |
  | default_tester    | Integer        | Optional  | ID of run default tester           |
  | plan_text_version | Integer        | Optional  |                                    |
  | estimated_time    | TimeDelta      | Optional  | HH:MM:MM                           |
  | notes             | String         | Optional  |                                    |
  | status            | Integer        | Optional  | 0:RUNNING 1:STOPPED  (default 0)   |
  | case              | Array/String   | Optional  | list of case ids to add to the run |
  | tag               | Array/String   | Optional  | list of tag to add to the run      |
  +-------------------+----------------+-----------+------------------------------------+
        """
        build_info = self.check_and_insert_build(build_version)
        if build_info is dict:
            build_id = build_info['build_id']
        else:
            build_id = build_info
        #build_id = self.check_and_insert_build(builds[0]['build_id']
        prod_version_id = self.get_product_version_id()
        run_res = None
        if summary:
            summary_note = summary
        else:
            summary_note = 'TestRun create via XML-RPC'
        if test_run_id is None:
            params = {
                      'plan'    : self.plan_id,
                      'build'   : build_id, #'unspecified',
                      'manager' : self.test_plan['author_id'],
                      'product' : self.test_plan['product_id'],
                      'summary' : summary_note,
                      'product_version':prod_version_id, #self.test_plan['default_product_version']
                      
                      }
            run_res = self.ns.TestRun.create(params)
            test_run_id = run_res['run_id']
        # step2. create the actual testrun based on test_id
        testcase_run_res = []
        for test_id in test_id_list:
            input_params = {
                    'run'       : test_run_id,
                    'case'      : test_id,
                    'build'     : build_id,
                    }
            case_run_res = self.ns.TestCaseRun.create(input_params)
            testcase_run_res.append(case_run_res)
        return (testcase_run_res)

 
    ######################################################################
    # action reponses
    #   these class methods in response to the user option.action
    ######################################################################
    
    def get_latest_runs(self, test_ids):
        """
        testcase_ids: is a list of test ids that you want to filter 

        """
        tcms_time =  datetime.datetime.now()
        date_format = "%Y-%m-%d"
        target_date=self.test_plan['create_date']#tcms_time.strftime("%Y-%m-%d")
        target_date  = '2011-08-17'
        #print("TARGET_DATE: %s" % target_date)
        #target_date=tcms_time.strftime("%Y-%m-%d")
        #self.info('xxx', 1) 
        params = {
                'case__case_id__in': test_ids, 
                #'case__summary__icontain': "El Nath",
            #'case_run_id' : 692230
                #'running_date__gt' : target_date,
                #'close_date__gt': target_date
            }
            #'notes': 'El Nath'}
        print("params: %s" % params)
        res = self.ns.TestCaseRun.filter(params)
        new_res = []
        ###########################################
        # XXX : need to filter out by testplan
        ############################################
        if len(res) > len(test_ids):
            # testcases ran more than once get unique_run_id and put it into an array, the latest should have an id that's the biggest
            run_list = []
            target_run_id = None
            for result in res:
                run_id = result['run_id']
                test_run = self.ns.TestRun.get(run_id)
                if test_run['plan_id'] == self.test_plan['plan_id']:
                    run_list.append(run_id)
                    target_run_id = run_list
            
            #params = {'run': target_run_id, 'case__case_id__in': test_ids,
            #        'case_run_status__in': [1, 2, 3, 4, 5]
            #        }  # pass or fail
                    new_res.append(result) #self.ns.TestCaseRun.filter(params)
            #self.info("xxx", 1)
        else:
            new_res = res
        #self.info("xx", 1)
        return new_res

    def get_testcase_id_by_script_name(self, script_name):
        #self.info("xxx", 1)
        if '.' in script_name:  # already in good form
            script_name =  script_name.replace('.', '/') + ".py"

        filter_val = {'script': script_name , 'plan': self.plan_id}
        print filter_val
        try:
            res = self.ns.TestCase.filter(filter_val)[0]
        except:
            name = script_name.replace('.', '/') + ".py"
            filter_val = {'plan': self.plan_id, 'script': name}
            try:
                res = self.ns.TestCase.filter(filter_val)[0]
            except:
                res = None
        if res:
            return res['case_id']
        else:
            return None

    def get_testcase_ids(self, tests):
        """
        given a list of RHTEST TestEntry object, retrieve a list of TCMS testCase IDs
        """
        testcases_dict = {}
        testcases = []  # array of test
        for test in tests:
            test_name = test.inst.__module__
            if test.args:   # there are arguments it's a tuple (variant, case_id)
                case_id = test.args[1]
            else:  # no arguemnt
                case_id = self.get_testcase_id_by_script_name(test_name)
            testcases_dict[case_id] = test_name
            testcases.append(case_id)
        return (testcases, testcases_dict)

    def get_testrun(self, run_id):
        return self.ns.TestRun.get_test_case_runs(run_id)

    def get_testcaserun(self, tc_run_id):
        return self.ns.TestCaseRun.filter({'case_run_id': tc_run_id})
    
    def update_testcaserun(self, caserun_id, params):
        return self.ns.TestCaseRun.update(caserun_id, params)
    
    def update_testrun(self, run_id, params):
        return self.ns.TestRun.update(run_id, params)

    def create_testrun_from_script(self, script_name,
        build_version='unspecified'):
        """
        create a test run in TCMS based on the testcase ID which we get with

        """
        testcases = []
        case_id = self.get_testcase_id_by_script_name(script_name)
        testcases.append(case_id)
        res = self.create_testrun(testcases, build_version)
        return res
        
    def create_testcaserun(self, params):
    
        """
        should be called after a top level testRun has been created
        """
        pass

    def dump_testcases_to_json_by_tag(self, tag_name, write_to_file=False):
        """ dumps out the testcase to a json format given the tcms tag name """
        import json
        output_name = tag_name + ".json"
        testcases = self.get_testcases_by_tag(tag_name)
        json_output = json.dumps(testcases)
        #json_output = json.dumps(testcases, indent=4)
        if write_to_file:
            fd = open(output_name, 'w')
            fd.write(json_output + "\n")
            fd.close()
        return (json_output, len(testcases))

    def extract_testcases_from_json(self, json_data):
        """ given a json formated testcase data, extract all of the testcase ids"""
        testcase_data = json.loads(json_data)
        for testcase in testcase_data:
            self.info("xxx", 1)

    def get_testcases_str_by_tag(self, tag_name):
        testcases = self.get_testcases_by_tag(tag_name)
        json_ouput = json.dumps(testcases, indent)
        return testcases


    def get_tags_in_testplan(self, test_plan_id=None, tag_name = None):
        if test_plan_id is None:
            test_plan_id = self.plan_id
        
        tags = self.ns.TestPlan.get_tags(test_plan_id)

        # tag is a dictionary of id, name  {'id': 344, 'name': 'migration'}
        if tag_name:
            for tag in tags:
                if tag['name'] == tag_name:
                    return tag
        else:
            return tags

    def get_case_tags(self, test_plan_id=None, tag_name=None):
        if test_plan_id is None:
            test_plan_id = self.plan_id

        case_tags = self.ns.TestPlan.get_all_cases_tags(test_plan_id)
        casetags = []
        tags_obj = []

        for case_tag in case_tags:
            if tag_name:
                if case_tag['name'] == tag_name:
                    casetags.append(case_tag['name'])
                    tags_obj.append(case_tag)
                    return case_tag['name'], case_tag
            else: 
                casetags.append(case_tag['name'])
                tags_obj.append(case_tag)

        return casetags, tags_obj

        
#######################
# helper functions
#######################

def construct_json_obj(script_str):
    """ given a script string convert it into a JSON object """
    json_repr = None
    json_dict = None
    if script_str.endswith(".py"):
        # it's a python file
        json_dict = {"python" : script_str}
    elif script_str.endswith(".rb") or script_str.endswith(".feature"):
        # it's a ruby/cucumber file
        json_dict = {"ruby": script_str}
    io = StringIO()    
    json.dump(json_dict, io)
    json_str = io.getvalue()
    return (json_str, json_dict) 


def convert_python_script_to_json(test_obj, tcms_obj):
    script_json = None
    json_dict = None
    script_name = test_obj['script'].strip()
    try:
        script_json = json.loads(script_name)
    except:
        # the existing string is not a JSON string. construct 
        script_json, json_dict = construct_json_obj(script_name)
    if json_dict:
        if json_dict.has_key('python'):
            param = {'script': script_json}
            res = tcms_obj.ns.TestCase.update(test_obj['case_id'], param)
      
    print "ID: %s, OLD: %s, NEW: %s" % (test_obj['case_id'], script_name, script_json)

def convert_json_to_python_script(test_obj, tcms_obj):
    """ reverse of convert_python_script_to_json """
    script_python = None
    try:
        script_json = json.loads(test_obj['script'])
    except:
        script_json = None
    
    if script_json:
        script_python = script_json['python']

        param = {'script': script_python}
        res = tcms_obj.ns.TestCase.update(test_obj['case_id'], param)
        print "ID: %s, OLD: %s, NEW: %s" % (test_obj['case_id'], script_json, script_python)

def update_script_field_to_json_format(tcms_obj=None, testcase_id=None):
    if tcms_obj is None:
        ### XXX change this to openshift 2.0 once fully tested
        tcms_obj = TCMS(test_plan='ppp_sandbox3') #openshift 2.0')

    script_json = None
    if testcase_id is None:
        # go through the entire testplan looking for automated and confirmed
        params = {'is_automated': 1, 'case_status': 2}
        tests = tcms_obj.get_testcases(params)
        for test in tests:
            convert_python_script_to_json(test, tcms_obj)
    else:
        test = tcms_obj.ns.TestCase.get(testcase_id)
        convert_python_script_to_json(test, tcms_obj)

def revert_script_field_to_python_format(tcms_obj=None, testcase_id=None):
    """
    undo update_script_field_to_json_format

    """
    if tcms_obj is None:
        ### XXX change this to openshift 2.0 once fully tested
        tcms_obj = TCMS(test_plan='ppp_sandbox3') #openshift 2.0')

    script_python = None
    if testcase_id is None:
        # go through the entire testplan looking for automated and confirmed
        params = {'is_automated': 1, 'case_status': 2}
        tests = tcms_obj.get_testcases(params)
        for test in tests:
            convert_json_to_python_script(test, tcms_obj)
    else:
        test = tcms_obj.ns.TestCase.get(testcase_id)
        convert_json_to_python_script(test, tcms_obj)



def extract_script_field(script_field):
    """ given a testcase's script field information, extract the script path """
    try:
        script_json = json.loads(script_field)
    except:
        # the existing string is not a JSON string. construct 
        pass 
    if not script_json.has_key('python'):    
        return script_field
    else:
        return script_json['python']

def test():
    n = NitrateKerbXmlrpc('https://tcms.engineering.redhat.com/xmlrpc/')
    ns = n.server

    user = ns.User.get_me()
    #components = ns.Product.get_components('OpenShift Flex')
    #i  = 0
    #for comp in components:
    #    i += 1
    #    print "COMP %s: %s" % (i, comp['name'])
    filter_val = {'script': 'demo/simple_demo.py'}
    #resp = ns.TestCase.filter(filter_val)
    filter_val = {'plan__name' : 'PPP'}
    res = ns.TestRun.filter(filter_val)
    #res = ns.TestRun.filter({'run_id': 23373})
    testcase_id = int(res[0]['case_id'])
    ts_run_vals = {
            'case': testcase_id
            }
    self.info('xxx', 1)
    res = ns.TestCaseRun.create(ts_run_vals)

    self.info("xx", 1)
    # get builds by product
    builds = ns.Product.get_builds(PROD)
    # get build_id_by_name
    build_name = '31afead'
    build_id = ns.Build.check_build(build_name, PROD)['build_id']
    runs = ns.Build.get_runs(build_id)
    
    filter_val = {'build': build_id, 'case_run_status': '2'}
    cases_p = ns.TestCaseRun.filter(filter_val)
    filter_val = {'build': build_id, 'case_run_status': '3'}
    cases_f = ns.TestCaseRun.filter(filter_val)




if __name__ == '__main__':
    revert_script_field_to_python_format()
    self.info("xxx", 1)
    #test()
    tcms = TCMS(test_plan='Test Plan for OpenShift 2.0')
    name = 'fwtest_simple'
    res = tcms.get_case_tags(tag_name=name)
    self.info('xxx', 1)  
    res = tcms.dump_testcases_to_json_by_tag('manual_run')
    tc_list  = tcms.extract_testcases_from_json(res)
    self.info('xx',1)
    #tcms = TCMS(test_plan='ppp_sandbox3')
    res = tcms.get_testcase_id_by_script_name('RT/security/qpid_binding_stage.py')
    #tests = tcms.get_testscripts_by_tag('test_variants')
    testcase_ids = [161932]
    build_version = 'devenv_1808'
    summary = '2012_05_31-14:20:36_QPIDbinding'

    tcms.create_testrun(testcase_ids, build_version, summary)
    self.info("xxx", 1)
    #tests = tcms.get_testcases_by_tag('collections')
    #from datetime import time
    #total_seconds = 2332.333
    #params = {'status': 1, 'estimated_time_seconds': total_seconds }
    #res = tcms.update_testrun(38273, params)
    tests = tcms.get_testcase_id_by_script_name('Collections/Demo/Demo01.py')

    self.info('xxx', 1)
    tests = tcms.get_testcases()
    tc_ids = []
    for test in tests:
        if test['arguments']:
            tc_ids.append(test['case_id'])

    #tests = tcms.get_testcases_by_plan('Test Plan for OpenShift 2.0')
    variants_dict = tcms.get_variants_mapping(tc_ids) 
    for k, v in variants_dict.items():
        print "%s: %s" % (k, v)
    #tcms.dump_testcaes_to_json_by_tag('quick_smoke')
    self.info('xxx', 1)
    #name =  a[0]['script'].split('.py')[0].replace("/", ".")

    #res = tcms.check_and_insert_build('devenv_1651')
    #self.info("xxx", 1)
    #res = tcms.get_testcase_id_by_script_name('demo/simple_demo.py')
    # XXX assume we have run this step already caserun id is 846534, testrun ID is '33030'
    #res = tcms.create_testrun_from_script('demo/simple_demo.py')
    #TEST_RUN_ID = 33030
    run_list = tcms.get_testrun(TEST_RUN_ID)
    for run in run_list:
        tc_run = tcms.get_testcaserun(run['case_run_id'])
        case_run_params = {'case_run_status': FAILED}
        run_params = {'status': FINISHED}
        tcms.update_testrun(TEST_RUN_ID, run_params)
        res = tcms.update_testcaserun(run['case_run_id'], case_run_params)
        self.info('xx', 1)
    #res = tcms.ns.Product.get_versions(281)
    #version_id = tcms.get_product_version_id()

    components = tcms.Components
    #tests = {}
    #total_tests = 0
    #tcms.get_testcases_by_plan(3396)
    """
    res_list = tcms.get_testcases_by_components('Admin::Rsync')
    for res in res_list:
        print res['case_id']
    """
    #for i, comp in enumerate(components):
    #    #print "%04s: %s" % (i, comp['name'])
    #    test_cases = tcms.get_testcases_by_components(comp['name'])
    #    tests[comp['name']] = test_cases
    #    total_tests += len(test_cases)
    #print "Total test cases within test plan: %s" % total_tests

    #test_runs = tcms.get_plan_runs('Furud SP1')
    #build_name = '31afead'
    #runs = tcms.get_test_runs_by_build(build_name)
    #user_profile = tcms.User.get_me()
    #components = tcms.Product.get_components('OpenShift Flex')

    #test()
