#!/usr/bin/env python

"""
Attila Nagy
anagy@redhat.com
Apr 30, 2012

"""
import os, sys

WORK_DIR = os.path.dirname(os.path.abspath(__file__))
testdir = os.path.normpath(WORK_DIR + "/../../../")
sys.path.append(testdir)

import common
import rhtest
from quick_start_test import QuickStartTest
import fileinput
import re


class QuickStartRedis(QuickStartTest):

    def __init__(self, config):
        rhtest.Test.__init__(self, config)
        self.config.application_type = common.app_types["ruby"]
        self.config.application_embedded_cartridges = [  ]
        self.config.summary = "[Runtime][rhc-cartridge]quick-start example: Redis"
        self.config.git_upstream_url = "git://github.com/openshift/redis-openshift-example.git"
        self.config.random_value = common.getRandomString()
        self.config.page = "redis-read" # means '/'
        self.config.page_pattern = self.config.random_value

    def post_configuration_steps(self):
        
        try:
            for line in fileinput.input("./%s/config.ru" % ( self.config.application_name ), inplace = True):
                if re.search(r'map.+health.+do', line):
                    print "require 'redis'\n"
                    print "map '/redis-write' do"
                    print "    redis_write = proc do |env|"
                    print "        redis = Redis.new(:path => '/tmp/redis.sock')"
                    #print "        redis = Redis.new(:path => ENV['OPENSHIFT_HOMEDIR'] + '%s' + '/tmp/redis.sock')" %(self.config.application_type)
                    print "        redis.set 'myword', '%s'" % self.config.random_value
                    print "        [ 200, { 'Content-Type' => 'text/plain' }, ['DB_OPERATION_SUCCESS']]"
                    print "    end"
                    print "    run redis_write"
                    print "end"
                    print 
                    print "map '/redis-read' do"
                    print "    redis_read = proc do |env|"
                    print "        redis = Redis.new(:path => '/tmp/redis.sock')"
                    #print "        redis = Redis.new(:path => ENV['OPENSHIFT_HOMEDIR'] + '%s' + '/tmp/redis.sock')" %(self.config.application_type)
                    print "        myword = redis.get 'myword'"
                    print "        [ 200, { 'Content-Type' => 'text/plain' }, [ myword ]]"
                    print "    end"
                    print "    run redis_read"
                    print "end"
                    print
                print line,
        except Exception as e:
            fileinput.close()
            print type(e)
            print e.args
            self.fail("Configuration of the test-application must be successful")
        finally:
            fileinput.close()

        #
        # Creating Gemfile
        #
        Gemfile = open(self.config.application_name + "/Gemfile", "w")
        Gemfile.write('source "http://rubygems.org/"\n')
        Gemfile.write('gem "rack"\n')
        Gemfile.write('gem "thread-dump"\n')
        Gemfile.write('gem "redis"\n')
        Gemfile.close()

        Gemfile_lock = open(self.config.application_name + "/Gemfile.lock", "w")
        Gemfile_lock.write("GEM\n")
        Gemfile_lock.write("  remote: http://rubygems.org/\n")
        Gemfile_lock.write("  specs:\n")
        Gemfile_lock.write("    rack (1.4.1)\n")
        Gemfile_lock.write("    redis (3.0.1)\n")
        Gemfile_lock.write("    thread-dump (0.0.5)\n")
        Gemfile_lock.write("\n")
        Gemfile_lock.write("PLATFORMS\n")
        Gemfile_lock.write("  ruby\n")
        Gemfile_lock.write("\n")
        Gemfile_lock.write("DEPENDENCIES\n")
        Gemfile_lock.write("  rack\n")
        Gemfile_lock.write("  redis\n")
        Gemfile_lock.write("  thread-dump\n")
        Gemfile_lock.close()


        configuration_steps = [
            "cd %s" % self.config.application_name,
            #"bundle",
            "git add .",
            "git commit -a -m testing",
        ]

        ret_code = common.command_get_status(" && ".join(configuration_steps))
        self.assert_equal(ret_code, 0, "Configuration must be successfull")

    def post_deployment_steps(self):
        ret_code = common.check_web_page_output(
            self.config.application_name,
            "redis-write",
            "DB_OPERATION_SUCCESS"                                    
        )
        self.assert_equal(ret_code, 0, "Writing to Redis DB must be successful")

class OpenShiftTestSuite(rhtest.TestSuite):
    pass

def get_suite(conf):
    suite = OpenShiftTestSuite(conf)
    suite.add_test(QuickStartRedis)
    return suite

def run(conf):
    suite = get_suite(conf)
    suite()
