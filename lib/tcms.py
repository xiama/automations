# mzimen@redhat.com
# jialiu@redhat.com
# 2012-01-05
#

#for XMLRPC check this site:
#https://tcms.engineering.redhat.com/xmlrpc/
import nitrate
from kerberos import GSSError
import clog

rhtest_disposition_to_tcms_mapping = {'COMPLETED':'PAUSED', 'PASSED':'PASSED', 'FAILED':'FAILED', 'ABORT':'ERROR', 'SKIP':'WAIVED', 'INCOMPLETE' :'ERROR'}

TEST_RUN_STATUS = {'RUNNING' : 0, 'FINISHED' : 1}
CASE_RUN_STATUS = {'IDLE':1,'PASSED':2,'FAILED':3, 'RUNNING':4, 'PAUSED':5, 'BLOCKED':6,'ERROR':7, 'WAIVED':8}
#tag_id_name_map = [{'id': 513, 'name': 'acceptance'}, {'id': 1310, 'name': 'rhc-cartridge'}, {'id': 1859, 'name': 'non_site'}, {'id': 1860, 'name': 'devenv'}, {'id': 1876, 'name': 'cartridge'}, {'id': 1882, 'name': 'standalone'}, {'id': 1785, 'name': 'sprint6'}, {'id': 1958, 'name': 'fedoraenv'}, {'id': 2082, 'name': 'fwtest5'}, {'id': 2087, 'name': 'fwtest6'}]

class TCMS(object):
    """
    Base object for initializing connection to XML RPC
    """
    def __init__(self, xmlrpc_obj=None):
        self.log = clog.get_logger()
        if xmlrpc_obj is None:
            try:
                self.conn = nitrate.NitrateKerbXmlrpc('https://tcms.engineering.redhat.com/xmlrpc/')
                self.conn.get_me()
                self.server = self.conn.server
            except nitrate.NitrateXmlrpcError as e:
                self.log.error("Unable to connect via XMLRPC service: %s"%str(e))
                raise e
            except GSSError as e:
                self.log.error("Invalid kerberos ticket or hostname: %s"%str(e))
                raise e
            #server_url = "https://"+LOGIN+":"+PASSWORD+'@'+XMLRPC_URL;
            #Create an object to represent our server.
            #self.server = xmlrpclib.ServerProxy(server_url);
        else:
            self.server = xmlrpc_obj


    def update_testcaserun_status(self, testcaserun_id, status):
        self.log.debug("Updating TestCaseRun - %s Status to %s ..." %(testcaserun_id, status))
        return self.server.TestCaseRun.update([testcaserun_id], {'case_run_status' : CASE_RUN_STATUS[status]})

    def update_testcaserun_notes(self, testcaserun_id, notes):
        self.log.debug("Updating TestCaseRun Notes ...")
        return self.server.TestCaseRun.update([testcaserun_id], {'notes' : notes})

    def update_testcaserun_testlog(self, testcaserun_id, name, url):
        self.log.debug("Updating TestCaseRun Comments ...")
        return self.server.TestCaseRun.attach_log(testcaserun_id, name, url)

    def update_testcaserun_comments(self, testcaserun_id, comments):
        self.log.debug("Updating TestCaseRun Comments ...")
        return self.server.TestCaseRun.add_comment(testcaserun_id, comments)

    def update_testcaserun(self, testcaserun_id, params):
        return self.server.TestCaseRun.update([testcaserun_id], params)


    def create_testrun(self,summary=None, build=1770, plan_id=4962, manager_id=2351, product=292, product_version=1212, status=0):
        
        self.testrun_values = {
                'build'  : build,
                'plan'   : plan_id,
                'manager': manager_id,
                'summary': summary,
                'product': product,
                'product_version' : product_version,
                'status': status,
                }
        try:
            self.log.debug("Creating Test Run ...")
            testrun = self.server.TestRun.create(self.testrun_values)
            self.testrun_id = testrun['run_id']
            self.log.info("TCMS Test Run - https://tcms.engineering.redhat.com/run/%s/ was sucessfully created." %(self.testrun_id))
            return testrun
        except Exception as e:
            raise TCMSException("ERROR[TCMS]: Couldn't create TestRun(%s) :: %s" %(str(self.testrun_values), str(e)) )


    def get_testrun(self, testrun_id):
        try:
            return  self.server.TestRun.get(testrun_id)
        except:
            raise TCMSException("ERROR[TCMS]: Test run %s does not exist" % str(testrun_id))


    def add_testcase_to_run(self, testcase_id, testrun_id):
        self.log.debug("Adding test case with id - %s to test run %s" %(testcase_id, testrun_id))
        try:
            self.server.TestCase.add_to_run(testcase_id, testrun_id) 
        except Exception as e:
            self.log.warning("Duplicate entry attempted: Testcase %s already added to test run %s" % (testcase_id, testrun_id))


    def get_testcase_from_run(self, testrun_id):
        try:
            return self.server.TestRun.get_test_cases(testrun_id)
        except:
            raise TCMSException("ERROR[TCMS': Failed to get testcases for testrun %s" % str(testrun_id))

    get_testcase_by_run_id = get_testcase_from_run

    def reset_testrun(self, testrun_id, status=[]):
        """
        Set all (if status==None) caseruns' status to IDLE
        """
        testrun_cases = self.get_testcaseruns(testrun_id)
        caseruns2update = []
        for tcrun in testrun_cases:
            if status == None or len(status)==0 or tcrun['case_run_status'] in status:
                caseruns2update.append(tcrun['case_run_id'])
        try:
            self.server.TestCaseRun.update(caseruns2update, {'case_run_status': 1}) #1-IDLE
        except Exception as e:
            raise TCMSException("Unable to reset testrun[%s]: %s" %(testrun_id, str(e)))

    def get_testcaseruns(self, testrun_id):
        try:
            return self.server.TestRun.get_test_case_runs(testrun_id, 0)
        except Exception as e:
            raise TCMSException("Unable to fetch testcaseruns from DB per testrun[%s]: %s" %(testrun_id, str(e)))

    def get_testcaserun(self, testcase_id, testrun_id, build=None):
        if not build:
            build = self.get_testrun(testrun_id)["build_id"]
        try:
            return self.server.TestCaseRun.get_s(testcase_id, testrun_id, build)
        except Exception as e:
            raise TCMSException("Test case not in this test run %d" % testrun_id)

    def get_testcaserun_by_id(self, testcaserun_id):
        return self.server.TestCaseRun.get(testcaserun_id)


    def get_testcases(self, filter=None, plain_id='4962'):
        filter['is_automated'] = 1
        filter['plan__plan_id']         = plain_id
        filter['case_status']  = 2 #2-#CONFIRMED

        testcases = self.server.TestCase.filter(filter)
        if len(testcases) == 0 :
            raise TCMSException("ERROR[TCMS] : No test cases to run with filter %s" % str(filter))
        return testcases

    def get_tag_id(self, tag_name):
        if isinstance(tag_name, str):
            try:
                return int(self.server.Tag.get_tags({'names':[tag_name]})[0]['id'])
            except Exception as e:
                self.log.error(str(e))
                return None
        elif isinstance(tag_name, list) or isinstance(tag_name, tuple):
            try:
                return map(lambda x: x['id'], self.server.Tag.get_tags({'names':tag_name}))
            except Exception as e:
                self.log.error(str(e))
                return None
        else:
            return None

    def get_testcase_id_list_by_tag(self, testcase_tag_list, plan_id=4962):
        self.log.debug("Geting test cases taged by %s" %(testcase_tag_list))
        try:
           tag_id_list = [ i['id'] for i in self.server.Tag.get_tags({'names': testcase_tag_list}) ]
           """
           tag_id_list = []
           # TCMS bug - 808691, so here I must use hard code - tag_id_name_map:.
           for i in testcase_tag_list:
               for j in tag_id_name_map:
                   if i == j["name"]:
                       tag_id_list.append(j["id"])
                       break
           """
           filter = {
               'plan': plan_id,
               'tag__in': tag_id_list}
           #print filter
           tc_list = self.get_testcases(filter)
           tc_id_list = []
           for tc in tc_list:
               tc_id_list.append(tc["case_id"])
           return tc_id_list
        except Exception as e:
            self.log.error(e)

    def add_testcase_to_run_by_tag(self, testcase_tag_list, testrun_id):
        self.log.debug("Adding test cases taged by %s to test run %s" %(testcase_tag_list, testrun_id))
        try:
           tc_id_list = get_testcase_id_list_by_tag(testcase_tag_list)
           self.add_testcase_to_run(tc_id_list, testrun_id)
        except Exception as e:
            self.log.error(e)

    def update_testrun(self, testrun_id,  filter):
        return self.server.TestRun.update([testrun_id], filter)



class TCMSException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)




if __name__ == "__main__":
    pass
