#!/usr/bin/env python
import re
import time
import sys
import inspect
import subprocess
import os
import signal
from helper import TimeoutError, Alarm, _alarm_handler, COMMAND_TIMEOUT, cmd_get_status_output
# test By default, already have one element to occupy 0 index, so that steps' output will be saved from 1 index
# Every element in this list should be string.
__OUTPUT__ = [None]
__PARSED_VARS__ = {}
# parameters eval only occurs in TestCase instance, not in TestCaseStep instance
__EVAL_FLAG__ = False


def repl(matchobj):
    #global __OUTPUT__
    if matchobj != None:
        print '''Found '__OUTPUT__|__PARSED_VARS__' keyword, replace it'''
        return eval(matchobj.group(0))

def eval_parameters_list(parameters_list):
    #global __OUTPUT__
    print '''Eval parameters of string type...'''
    temp = []
    for parameter in parameters_list:
        if isinstance(parameter, str):
            re_match_obj = re.match(r"^__OUTPUT__(\[[^\[\]]+\])+$", parameter)
            if re_match_obj != None:
                parameter = eval(parameter)
            else:
                parameter = re.sub(r"__OUTPUT__(\[[^\[\]]+\])+", repl, parameter)
            #__PARSED_VARS__
            re_match_obj = re.match(r"^__PARSED_VARS__(\[[^\[\]]+\])+$", parameter)
            if re_match_obj != None:
                parameter = eval(parameter)
            else:
                parameter = re.sub(r"__PARSED_VARS__(\[[^\[\]]+\])+", repl, parameter)
        else:
            pass
        temp.append(parameter)
    return temp


def run_function(function_name, parameters_list):
    #global __OUTPUT__
    print "\nFunction is running ..."
    #apply is deprecated since version 2.3, http://docs.python.org/library/functions.html#apply
    #retcode = apply(self.cmd, self.parameters)
    retcode = function_name(*parameters_list)
    print "\nFunction Return:", retcode
    # Function's output will not be captured, so set it to "Fun_None_Output"
    return (retcode, "Fun_None_Output")


def eval_command_string(command_line):
    print '''Evaluting command string...'''
    cmd_after_eval = re.sub(r"__OUTPUT__(\[[^\[\]]+\])+",  repl, command_line)
    cmd_after_eval = re.sub(r"__PARSED_VARS__(\[[^\[\]]+\])+",  repl, cmd_after_eval)
    return cmd_after_eval



def run_command(command):
    return cmd_get_status_output(command)


def check_ret(real_ret, expect_ret):
    if not isinstance(real_ret, list) and isinstance(expect_ret, str) and re.match("^!",expect_ret):
        real_expect_ret = int(expect_ret.replace('!',''))
        if real_ret != real_expect_ret:
            print "Return %s, Expect %s - [PASS]" %(real_ret, expect_ret)
            return True
        else:
            print "Return %s, Expect %s - [FAIL]" %(real_ret, expect_ret)
            return False
    elif (isinstance(real_ret, list) or isinstance(real_ret, tuple)) and not (isinstance(expect_ret, tuple) or isinstance(expect_ret, list)): 
        #case when the list is returned from function...
        #will check only the first item in the list
        if len(real_ret)>0 and real_ret[0] == expect_ret:
            print "Return %s, Expect %s - [PASS]" %(real_ret[0], expect_ret)
            return True
        else:
            print "Return %s, Expect %s - [FAIL]" %(real_ret[0], expect_ret)
            return False
    elif (isinstance(real_ret, list) or isinstance(real_ret, tuple)) and (isinstance(expect_ret, list) or isinstance(expect_ret, tuple)):
        #case when the list is returned from function
        #also expected value is list
        if len(real_ret) != len(expect_ret):
            return False

        for i in real_ret:
            if real_ret[i] != expect_ret[i]:
                print "Return %s, Expect %s - [FAIL]" %(real_ret[i], expect_ret[i])
                return False
        print "Return %s, Expect %s - [PASS]" %(real_ret, expect_ret)
        return True
    elif real_ret == expect_ret:
        print "Return %s, Expect %s - [PASS]" %(real_ret, expect_ret)
        return True
    else:
        print "Return %s, Expect %s - [FAIL]" %(real_ret, expect_ret)
        return False


def check_output(output, expect_str_reg_list, ex_re_ignore_case, unexpect_str_reg_list, unex_re_ignore_case):
    if ex_re_ignore_case:
        print "re.I flag is trun on for expect string matching"
        ex_re_flag = re.M | re.I
    else:
        ex_re_flag = re.M
    for reg in expect_str_reg_list:
        search_obj = re.search(r'''%s'''%(reg), output, ex_re_flag)
        if search_obj != None:
            print "According to [%s] regular express, find out expected string: [%s] - [PASS]" %(reg, search_obj.group(0))
        else:
            print "According to [%s] regular express, no expected string is found out - [FAIL]" %(reg)
            return False

    if unex_re_ignore_case:
        print "re.I flag is trun on for unexpect string matching"
        unex_re_flag = re.M | re.I
    else:
        unex_re_flag = re.M
    for reg in unexpect_str_reg_list:
        search_obj = re.search(r'''%s'''%(reg), output, unex_re_flag)
        if search_obj != None:
            print "According to [%s] regular express, find out unexpected string: [%s] - [FAIL]" %(reg, search_obj.group(0))
            return False
        else:
            print "According to [%s] regular express, no unexpected string is found out - [PASS]" %(reg)

    return True


def filter_output(output, filter_reg):
    if filter_reg != None:
        search_obj = re.search(r"%s" %(filter_reg), output, re.M)
        if search_obj != None:
            ret_output = search_obj.group(0)
            print "According to output filter - [%s], return [%s]" %(filter_reg, ret_output)
        else:
            ret_output = ""
            print "According to output filter - [%s], return empty string" %(filter_reg)
    else:
        ret_output = output
    return ret_output


def run(command, function_parameters):
    if isinstance(command, str):
        print '''Command: %s''' %(command)
        if __EVAL_FLAG__:
            command = eval_command_string(command)
            print '''Command after evalute: %s\n''' %(command)
        (retcode, output) = run_command(command)
    elif inspect.isfunction(command):
        print '''Function: %s''' %(command)
        print '''Parameters: %s''' %(function_parameters)

        #
        # let's try to exec functions/closeures if present
        #
        l_params = []
        for p in function_parameters:
            if inspect.isfunction(p) or inspect.ismethod(p):
                print '''INFO: Execute %s parameter as function'''%p
                res = p()
                l_params.append(res)
            else:
                l_params.append(p)

        function_parameters = l_params
        print '''Parameters: %s''' %(function_parameters)
        if __EVAL_FLAG__:
            function_parameters = eval_parameters_list(function_parameters)
            print '''Parameters after evalute: %s\n''' %(function_parameters)
        (retcode, output) = run_function(command, function_parameters)
    else:
        print "Unknow command type !!!"
        return 254

    return (retcode, output)




class TestCase():

    def __init__(self, summary, steps=[], clean_up_command=None, clean_up_function_parameters=[], testcase_id=None):
        if not isinstance(steps, list):
            print "Parameter Error: list type is expected for steps option, e.g: [{'description': <value>, 'command': <value>}, TestCaseStep_Object]"
            sys.exit(99)
        if not isinstance(summary, str):
            print "Parameter Error: str type is expected for summary option"
            sys.exit(99)

        self.summary = summary
        self.TestCaseStep_Obj_list = []
        self.count = 0
        self.Step_Output_List = []
        self.__clean_up_cmd = clean_up_command
        self.__clean_up_fun_parameters = clean_up_function_parameters
        self.testcase_status= 'IDLE'   #default state... (we need this for backward compatibility)

        for step in steps:
            self.count = self.count + 1
            if isinstance(step, dict):
                step_parameters_list = []
                step_parameters_list.append(step['Description'])
                step_parameters_list.append(step['Command'])
                if step.has_key('Function_Parameters'):
                    step_parameters_list.append(step['Function_Parameters'])
                else:
                    step_parameters_list.append([])
                if step.has_key('Expect_Description'):
                    step_parameters_list.append(step['Expect_Description'])
                else:
                    step_parameters_list.append("")
                if step.has_key('Expect_Return'):
                    step_parameters_list.append(step['Expect_Return'])
                else:
                    step_parameters_list.append(None)
                if step.has_key('Expect_String_List'):
                    step_parameters_list.append(step['Expect_String_List'])
                else:
                    step_parameters_list.append([])
                if step.has_key('Expect_Str_Re_IgnoreCase'):
                    step_parameters_list.append(step['Expect_Str_Re_IgnoreCase'])
                else:
                    step_parameters_list.append(False)
                if step.has_key('Unexpect_String_List'):
                    step_parameters_list.append(step['Unexpect_String_List'])
                else:
                    step_parameters_list.append([])
                if step.has_key('Unexpect_Str_Re_IgnoreCase'):
                    step_parameters_list.append(step['Unexpect_Str_Re_IgnoreCase'])
                else:
                    step_parameters_list.append(False)
                if step.has_key('Output_Filter'):
                    step_parameters_list.append(step['Output_Filter'])
                else:
                    step_parameters_list.append(None)
                step_parameters_list.append(self.count)
                if step.has_key('Try_Count'):
                    step_parameters_list.append(step['Try_Count'])
                else:
                    step_parameters_list.append(1)
                if step.has_key('Try_Interval'):
                    step_parameters_list.append(step['Try_Interval'])
                else:
                    step_parameters_list.append(5)
                if step.has_key('Clean_Up_Command'):
                    step_parameters_list.append(step['Clean_Up_Command'])
                else:
                    step_parameters_list.append(None)
                if step.has_key('Clean_Up_Function_Parameters'):
                    step_parameters_list.append(step['Clean_Up_Function_Parameters'])
                else:
                    step_parameters_list.append([])
                TestCaseStep_Obj = TestCaseStep(*step_parameters_list)
                self.TestCaseStep_Obj_list.append(TestCaseStep_Obj)
            elif isinstance(step, TestCaseStep):
                step.step_id = self.count
                self.TestCaseStep_Obj_list.append(step)
            else:
                print "Parameter error: nethier dict type nor TestCaseStep Object"
                sys.exit(99)


    def run(self):
        """
        TestCase.run()
        """
        # init __OUTPUT__ list and __EVAL_FLAG__ at the begin of test case
        global __OUTPUT__
        global __PARSED_VARS__
        global __EVAL_FLAG__
        __OUTPUT__ = [None]
        __PARSED_VARS__ = {}
        __EVAL_FLAG__ = True
        print "="*80
        print self.summary
        print "="*80
        # Start run every step
        try:
            fail_detected = None
            for step_obj in self.TestCaseStep_Obj_list:
                (step_ret, step_output) = step_obj.run()
                if step_output == "Fun_None_Output":
                    __OUTPUT__.append(step_ret)
                #if isinstance(step_ret, str):
                #    __OUTPUT__.append(step_ret)
                #else:
                #    print "WARNING!!!\nThe return value of function is not string type, so empty string will be saved into __OUTPUT__ list"
                #    __OUTPUT__.append("")
                else:
                    __OUTPUT__.append(step_output)
                #print "\n----> Current __OUTPUT__:", __OUTPUT__, "\n"
            #TODO: check this assumption: I case of failure --> Exception otherwise PASS
            self.testcase_status = 'PASSED'
        except TestCaseStepFail as fail:
            self.testcase_status = 'FAILED'
            raise fail
        except Exception as e:
            self.testcase_status = 'ERROR'
            raise e
        finally:
            if self.__clean_up_cmd != None:
                self.clean_up()

            # clean up __OUTPUT__ list and __EVAL_FLAG__ list at the end of test case
            __OUTPUT__ = [None]
            __PARSED_VARS__= {}
            __EVAL_FLAG__ = False


    def add_clean_up(self, command, function_parameters=[]):
        self.__clean_up_cmd = command
        if len(function_parameters) != 0:
            self.__clean_up_fun_parameters = function_parameters


    def clean_up(self):
        print "~"*50
        print "Test Case Clean Up ..."
        print "~"*50
        run(self.__clean_up_cmd, self.__clean_up_fun_parameters)


class TestCaseStep():
    def __init__(self, description, command, function_parameters=[], expect_description="", expect_return=None, expect_string_list=[], ex_re_ignore_case=False, unexpect_string_list=[], unex_re_ignore_case=False, output_filter=None, step_id=None, try_count=1, try_interval=5, clean_up_command=None, clean_up_function_parameters=[], output_callback=None, string_parameters=None):
        self.desc = description
        self.cmd = command
        self.parameters = function_parameters
        self.string_parameters = string_parameters
        self.expect_desc = expect_description
        self.expect_ret = expect_return
        self.expect_str_list = expect_string_list
        self.ex_re_ignore_case = ex_re_ignore_case
        self.unexpect_str_list = unexpect_string_list
        self.unex_re_ignore_case = unex_re_ignore_case
        self.output_filter = output_filter
        self.step_id = step_id
        self.try_count = try_count
        self.try_interval = try_interval
        self.__clean_up_cmd = clean_up_command
        self.__clean_up_fun_parameters = clean_up_function_parameters
        self.__output_callback = output_callback

        if self.expect_ret != None:
            self.check_ret_enable = True
        else:
            self.check_ret_enable = False

        if len(self.expect_str_list) != 0 or len(self.unexpect_str_list) != 0:
            self.check_output_enable = True
        else:
            self.check_output_enable = False


    def add_clean_up(self, command, function_parameters=[]):
        self.__clean_up_cmd = command
        if len(function_parameters) != 0:
            self.__clean_up_fun_parameters = function_parameters


    def clean_up(self):
        print "~"*50
        print "Test Case Step Clean Up ..."
        print "~"*50
        run(self.__clean_up_cmd, self.__clean_up_fun_parameters)


    def __check_command_result(self, result, expect_ret, expect_str_list, ex_re_ignore_case, unexpect_str_list, unex_re_ignore_case):
        (retcode, output) = result

        if self.check_ret_enable == False and self.check_output_enable == False:
            print "No check!!!!"
            return None

        if self.check_ret_enable == True:
            print "Checking return value ..."
            if check_ret(retcode, expect_ret):
                self.check_ret_enable = False
            else:
                return None

        if self.check_output_enable == True:
            print "Checking output string ..."
            if check_output(output, expect_str_list, ex_re_ignore_case, unexpect_str_list, unex_re_ignore_case):
                self.check_output_enable = False
            else:
                return None


    def __check_function_result(self, result, expect_ret):
        (retcode, output) = result

        if self.check_ret_enable == True:
            print "Checking return value..."
            if check_ret(retcode, expect_ret):
                self.check_ret_enable = False
            else:
                return None
        else:
            print "No check!!!!"


    def run(self):
        """
        TestCaseStep.run()
        """
        global __EVAL_FLAG__
        global __PARSED_VARS__
        #global __OUTPUT__

        print "-"*80
        if self.step_id is not None:
            print "Step %s:" %(self.step_id)
        print "Description: %s" %(self.desc)
        if isinstance(self.expect_desc, str):
            print "Expect Result: %s" %(self.expect_desc)
        print "-"*80

        if isinstance(self.cmd, str) or isinstance(self.cmd, unicode):
            if (isinstance(self.cmd, unicode)):
                print "Warning: UNICODE format of command."
            print '''Command: %s''' %(self.cmd)
            if self.string_parameters:
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
                    print "DEBUG:", l_params
                    str2exec = 'self.cmd=self.cmd%%(%s)'%l_params
                    print "DEBUG:", str2exec
                    #and do the expansion...
                    exec(str2exec)
                except Exception as e:
                    print "WARN: Unable to expand command.",e

                print '''Command after expansion: %s\n''' %(self.cmd)

            if __EVAL_FLAG__:
                self.cmd = eval_command_string(self.cmd)
                print '''Command after evalute: %s\n''' %(self.cmd)

            (retcode, output) = run_command(self.cmd)

            #
            #handling of output_callback function
            #
            if self.__output_callback and (inspect.isfunction(self.__output_callback) or inspect.ismethod(self.__output_callback)):
                print "DEBUG: Calling callback...",self.__output_callback
                try:
                    __PARSED_VARS__ = self.__output_callback(output)
                    if not isinstance(__PARSED_VARS__, dict):
                        print "WARN: Wrong return value of callback. Should be dict()"
                    print "DEBUG: Callback Done.", __PARSED_VARS__
                except Exception as e:
                    print "CALLBACK ERROR: ",e


            self.__check_command_result((retcode, output), self.expect_ret, self.expect_str_list, self.ex_re_ignore_case, self.unexpect_str_list, self.unex_re_ignore_case)
            # If check failed, will try again
            for num in range(1, self.try_count):
                if self.check_ret_enable == True or self.check_output_enable == True:
                    print "\nSleep %s seconds, after that, will try again ...\n" %(self.try_interval)
                    time.sleep(self.try_interval)
                    (retcode, output) = run_command(self.cmd)
                    self.__check_command_result((retcode, output), self.expect_ret, self.expect_str_list, self.ex_re_ignore_case, self.unexpect_str_list, self.unex_re_ignore_case)
                else:
                    break

            if self.__clean_up_cmd != None:
                self.clean_up()

            if self.check_ret_enable == False and self.check_output_enable == False:
                output = filter_output(output, self.output_filter)
                return (retcode, output)
            else:
                raise TestCaseStepFail('Check Failed !!! @shell %s'%self.cmd)

        elif inspect.isfunction(self.cmd) or inspect.ismethod(self.cmd):
            print '''Function: %s''' %(self.cmd)
            print '''Parameters: %s''' %(self.parameters)


            #
            # let's try to exec functions/closeures if present
            #
            l_params = []
            for p in self.parameters:
                if inspect.isfunction(p) or inspect.ismethod(p):
                    print '''INFO: Execute %s parameter as function '''%p
                    res = p()
                    l_params.append(res)
                else:
                    l_params.append(p)

            if __EVAL_FLAG__:
                l_params = eval_parameters_list(l_params)
                print '''Parameters after evalute: %s\n''' %(l_params)

            print '''Parameters: %s''' %(l_params)
            self.parameters = l_params
            (retcode, output) = run_function(self.cmd, l_params)

            #
            #handling of output_callback function
            #
            if self.__output_callback and (inspect.isfunction(self.__output_callback) or inspect.ismethod(self.__output_callback)):
                print "DEBUG: Calling callback...",self.__output_callback
                try:
                    __PARSED_VARS__ = self.__output_callback(output)
                    print "DEBUG: Callback Done.", __PARSED_VARS__
                except Exception as e:
                    print "ERROR: ",e

            self.__check_function_result((retcode, output), self.expect_ret)
            # If check failed, will try again
            for num in range(1, self.try_count):
                if self.check_ret_enable == True:
                    print "\nSleep %s seconds, after that, will try again ...\n" %(self.try_interval)
                    time.sleep(self.try_interval)
                    (retcode, output) = run_function(self.cmd, self.parameters)
                    self.__check_function_result((retcode, output), self.expect_ret)
                else:
                    break

            if self.__clean_up_cmd != None:
                self.clean_up()

            if self.check_ret_enable == False:
                return (retcode, output)
            else:
                raise TestCaseStepFail('Check Failed !!! @function %s)'%self.cmd)

        else:
            raise Exception("Unknow Command Type !!!")

    def add_output_callback(self, command, function_parameters=[]):
        """
        Callback has to return dict type e.g.{'uuid':'329347239',...} for later processing. Any additional step then can use: __PARSED_VARS__['uuid'] to access it
        """
        self.__output_callback = command
        #TODO: do implement
        if len(function_parameters) != 0:
            self.__output_callback_param = function_parameters
            


class TestCaseStepFail(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


