#!/usr/bin/python
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../")
sys.path.append(testdir)

import testcase, common, OSConf


if __name__ == '__main__':
    user_email = os.environ["OPENSHIFT_user_email"]
    user_passwd = os.environ["OPENSHIFT_user_passwd"]
    app_type = "perl-5.10"
    app_name = "testapp"
    app_repo = "/tmp/%s_repo" %(app_name)

    common.env_setup()
    steps_list = []

    print "Running this now"
    feature = os.path.join(WORK_DIR,"cartridge-php.feature")
    cmd = "cucumber %s" % feature
    step = testcase.TestCaseStep("Add Remove Alias a PHP Application",
                                  cmd,
                                  function_parameters=[],
                                  expect_return=0,
                                  expect_string_list=["no local repo has been created"],
                                 )

    steps_list.append(step)

    case = testcase.TestCase("Add Remove Alias a PHP Application",
                             steps_list
                            )
    case.run()

