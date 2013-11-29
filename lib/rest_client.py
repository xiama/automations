#!/usr/bin/python

from StringIO import StringIO
from urllib import urlencode
import pycurl
import common

#
# Valid return outputs are:
# 1. http_code
# 2. http_output
#
class RHC:

    def __init__(self, path, output = "http_code", format = "application/xml"):
        server = common.get_instance_ip()
        (username, password) = common.get_default_rhlogin()

        self.output = output
        self.curl = pycurl.Curl()

        print "Configuring URL..."
        self.curl.setopt(pycurl.URL, "https://%s/broker/rest/%s" % (server, path))

        print "Configuring Verbosity..."
        self.curl.setopt(pycurl.VERBOSE, 1)

        print "Configuring HTTP Basic Auth..."
        self.curl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)

        print "Configuring Username and Password..."
        self.curl.setopt(pycurl.USERPWD, "%s:%s" % ( username, password ))

        print "Configuring SSL_Verify_Peer option..."
        self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)

        if output == "http_output":
            print "Configuring the writer function..."
            self.b = StringIO()
            self.curl.setopt(pycurl.WRITEFUNCTION, self.b.write)
    
        print "Configuring HTTP headers %s..." % ( format )
        self.curl.setopt(pycurl.HTTPHEADER, [ "Accept: %s" % ( format )])

    def set_option(self, option, value):
        self.curl.setopt(option, value)
    
    def perform(self):
        print "Performing..."
        self.curl.perform()

    def get_output(self):
        """
        This function returns the required output. 
        Currently the following output types are supported:

        http_code = The HTTP return code
        http_output = The content itself

        Reuiered output type is configured in the constructor.
        """
            
        if self.output == "http_code":
            return self.curl.getinfo(pycurl.HTTP_CODE)
        elif self.output == "http_output":
            return self.b.getvalue()

#
# RHC REST - GET
#
def rhc_rest_get(path, output = "http_code", format = "applicaiton/xml"):
    curl = RHC(path, output, format)
    curl.perform()

    return curl.get_output()

#
# RHC REST - POST
#
def rhc_rest_post(path, output = "http_code", format = "application/json", data = dict()):
    # Init
    curl = RHC(path, output, format)

    print "Configuring POST..."
    curl.set_option(pycurl.POST, 1)

    print "Configuring POST fields..."
    curl.set_option(
        pycurl.POSTFIELDS,
        urlencode(data)
    )

    curl.perform()

    return curl.get_output()

def scale_up(domain, application):
    return rhc_rest_post(
        "domains/%s/applications/%s/events" % ( domain, application ),
        output = "http_code",
        format = "application/xml",
        data = { "event" : "scale-up" }
    )

def scale_down(domain, application):
    return rhc_rest_post(
        "domains/%s/applications/%s/events" % ( domain, application ),
        output = "http_code",
        format = "application/xml",
        data = { "event" : "scale-down" }
    )

def add_alias(domain, application, alias):
    return rhc_rest_post(
        "domains/%s/applications/%s/events" % ( domain, application), 
        output = "http_code",
        format = "application/xml",
        data = { "event" : "add-alias", "alias" : alias }
    )

def remove_alias(domain, application, alias):
    return rhc_rest_post(
        "domains/%s/applications/%s/events" % ( domain, application ), 
        output = "http_code", 
        format = "application/xml",
        data = { "event" : "remove-alias", "alias" : alias }
    )
