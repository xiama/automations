import unittest, time, re
import baseutils
import sys
import re
from optparse import OptionParser 
import commands
import subprocess
import random
import TCMS
import TCMSTestRunner

'''
1. get the list of scripts from TCMS
2. run them one by one
3. do update
'''

def get_classname_from_testcase(script_file):
    f = open(script_file, "r")
    obj = re.search(r"class\s+([^\(]+)\(", f.read())
    f.close()
    if obj:
        print obj.group(1)
        return obj.group(1)
    else:
        raise Exception("Unable to get classname from %s."%script_file)


def testrun_suite(testrun_id):
    '''
    Returns a array of
    '''
    suites = []
    try:
        openshift = TCMS.OpenShift(4962, 'demo', repo='./openshift_web')
        script_list = openshift.get_testrun_scripts(testrun_id)
    except Exception as e:
        raise e

    for s in script_list:
        tcms_suite=unittest.TestSuite()
        try:
            script_name = s['script']
            print "DEBUG: script: %s"%script_name
            #TODO:obj = re.search(r"(.*)/([^/]+).py",script_name)
            obj = re.search(r"(.*).py",script_name)
            module_name = obj.group(1)
            #print "Importing %s"%module_name
            exec "import %s"%module_name
            #print "Done."
            classname = get_classname_from_testcase(script_name) 
            #print "tcms_suite=unittest.TestLoader().loadTestsFromTestCase(%s.%s)"%(module_name, classname)
            #exec "tcms_suite=unittest.TestLoader().loadTestsFromTestCase(%s.%s)"%(module_name, classname)
            exec "tcms_suite=unittest.TestLoader().loadTestsFromTestCase(%s.%s)"%(module_name, classname)
            tcms_suite.case_run_id=s['case_run_id']
#
#hack the class: add title,script for the first object
#
            #For all possible test cases... def test_X_...
            for i in range(len(tcms_suite._tests)):
                tcms_suite._tests[i].title      = s['title']
                tcms_suite._tests[i].case_id    = s['case_id']
                tcms_suite._tests[i].script     = s['script']
                tcms_suite._tests[i].case_run_id= s['case_run_id']
            suites.append(tcms_suite)
        except Exception as e:
            raise Exception(e)

    return unittest.TestSuite(suites)


if __name__ == "__main__":
    i=random.uniform(1,10)
    generate_new_user="libra-test+stage"+str(i)[3:10]+"@redhat.com"
    baseutils.update_config_file('environment','new_user',generate_new_user)
    if len(sys.argv) < 2:
        print """usage: --url=<url> --testrun_id=<testrun_id>  --browser=<browser> --new_user=<new_user> --title=<title> --description=<decription> --proxy=<http://proxy>"""
        sys.exit(1)
    else:
        parser = OptionParser()
        parser.add_option("--url", dest="url",default="https://openshifttest.redhat.com",
                   help="url link")
        parser.add_option("--browser", dest="browser",default="firefox",
                   help="browser name")
        parser.add_option("--browserpath", dest="browserpath",default=0,
                   help="browser path")
        parser.add_option("--proxy", dest="proxy", default="",
                   help="Proxy URL")
        parser.add_option("--new_user", dest="new_user",
                   help="new user")
        parser.add_option("--resultfile", dest="resultfile",default="OpenShift.WebTestResult.html",
                   help="result file name")
        parser.add_option("--title", dest="title",default="OpenShift Web Test Report",
                   help="result file title")
        parser.add_option("--description", dest="description",default="This is OpenShift Web Test Result",
                   help="result file description")
        parser.add_option("--testrun_id", dest="testrun_id",default=False,
                   help="testrun_id for web automated test cases")
        (options, args) = parser.parse_args()
        if options.url != None: baseutils.update_config_file('environment','url', options.url)
        if options.browser != None:baseutils.update_config_file('environment','browser', options.browser)
        if options.browserpath != None:baseutils.update_config_file('environment','browserpath',options.browserpath)
        if options.proxy != None: baseutils.update_config_file('environment', 'proxy', options.proxy)
        if options.new_user != None:baseutils.update_config_file('environment','new_user',options.new_user)
        #if config.proxy:
        #    baseutils.update_config_file('environment','libra_server',"stg.rhcloud.com")
        #else:
        #    baseutils.update_config_file('environment','libra_server',"dev.rhcloud.com")
        if options.resultfile != None: baseutils.update_config_file('output','resultfile',options.resultfile)
        if options.title != None:baseutils.update_config_file('output','title',options.title)
        if options.description != None:baseutils.update_config_file('output','description',options.description)

        runner = TCMSTestRunner.TCMSTestRunner(testrun_id=options.testrun_id)
#we should load it here...
        ret=runner.run(testrun_suite(options.testrun_id))
        sys.exit(ret)
        
    

    
     


