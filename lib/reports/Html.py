#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
Report object that creats XHTML format reports. 

"""

import sys
import reports

import XML.XHTML as XHTML

def escape(s):
	s = s.replace("&", "&amp;") # Must be first
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	s = s.replace('"', "&quot;")
	return s

class HTMLFormatter(reports.NullFormatter):
	MIMETYPE = "text/html"
	_MSGTYPESUB = {
		"PASSED":'<font color="green">PASSED</font>',
		"FAILED":'<font color="red">FAILED</font>',
		"ERROR":'<font color="red">ERROR</font>',
		"COMPLETED":'<font color="green">COMPLETED</font>',
		"INCOMPLETE":'<font color="yellow">INCOMPLETE</font>',
		"ABORTED":'<font color="yellow">ABORTED</font>',
		"INFO":"INFO",
		"DIAGNOSTIC":'<font color="brown">DIAGNOSTIC</font>',
	}

	def title(self, title):
		s = ["<br><h1>"]
		s.append(escape(title))
		s.append("</h1>\n")
		return "".join(s)

	def heading(self, text, level=1):
		s = []
		s.append("\n<h%s>" % (level,))
		s.append(escape(text))
		s.append("</h%s>\n" % (level,))
		return "".join(s)

	def paragraph(self, text):
		return "<p>%s</p>\n" % (escape(text),)

	def message(self, msgtype, msg, level=1):
		msg = str(msg)
		msgtype = self._MSGTYPESUB.get(msgtype, msgtype)
		if msg.find("\n") > 0:
			return "%s: <pre>%s</pre><br>\n" % (msgtype, escape(msg))
		else:
			return '<font face="courier" size="-1">%s: %s</font><br>\n' % (msgtype, escape(msg))

	def text(self, text):
		return "<pre>\n%s\n</pre>\n" % (text,)

	def url(self, text, url):
		return '<a href="%s">%s</a>\n' % (url, text)

	def summary(self, text):
		sum = "<pre>\n%s\n</pre>\n" % (text,)
		return sum.replace("PASSED", self._MSGTYPESUB["PASSED"])
	def section(self):
		return "<hr>\n"

	def page(self):
		return "<br><hr><br>\n"

	def initialize(self):
		return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Final//EN">
<html>
  <head>
	<title>Test Results</title>
  </head>
<body>
"""
	def finalize(self):
		return "\n</body>\n</html>\n"



class XHTMLFormatter(reports.NullFormatter):
	MIMETYPE = "text/html"
	_MSGTYPESUB = {
		"PASSED":     '<span class="passed">PASSED</span>',
		"FAILED":     '<span class="failed">FAILED</span>',
		"COMPLETED":  '<span class="completed">COMPLETED</span>',
		"ERROR":      '<span class="error">ERROR</span>',
		"INCOMPLETE":    '<span class="incomplete">INCOMPLETE</span>',
		"ABORTED":    '<span class="aborted">ABORTED</span>',
		"INFO":       '<span class="info">INFO</span>',
		"DIAGNOSTIC": '<span class="diagnostic">DIAGNOSTIC</span>',
	}

	def initialize(self):
		return """<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">
<html>
  <head>
   <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <title>Test Results</title>
   <style type="text/css">
body {background: white; color: black;
    margin: .25in; border: 0; padding: 0;
    font:13px/1.45 sans-serif; 
}
a:link {
    background-color: transparent;
}
a:visited	{
    background-color: transparent;
}
a:active	{
    background-color: transparent;
}
a:hover {
    background-color: transparent;
    text-decoration:underline;
}
img {
    border:0;
}
h1, h2, h3, h4, h5, h6 {
    font-family: Arial, sans-serif;
    color: #333;
    background: transparent;
    margin-bottom:0;
    padding:0;
}
h1 {
    font-size: 135%;
    padding: 0;
    padding-top: 10px;
    margin-bottom: 0;
}
h2 {
    font-size:	115%;
    text-decoration: underline;
    padding: 0;
    padding-bottom: 10px;
    margin-bottom: 0;
    margin-left: .5in;
}
h3, h4, h5 {
    font-size: 1.0em;
}
p {
   margin: 0;
   padding: 0;
   margin-left: .5in;
   font-family: monospace;
}

span.passed {
    color: green;
    font-weight: bold;
}
span.failed {
    color: red;
    font-weight: bold;
}
span.completed {
    color: green;
    font-weight: bold;
}
span.incomplete {
    color: yellow;
}
span.aborted {
    color: yellow;
}
span.diagnostic {
}
span.error {
    color: red;
    font-weight: bold;
}
span.info {
}

   </style>
  </head>
  <body>
"""

	def finalize(self):
		return "\n  </body>\n</html>\n"

	def page(self):
		return "<br><hr><br>\n"

	def title(self, title):
		s = ["<h1>"]
		s.append(escape(title))
		s.append("</h1>\n")
		return "".join(s)

	def heading(self, text, level=1):
		s = []
		s.append("\n<h%s>" % (level,))
		s.append(escape(text))
		s.append("</h%s>\n" % (level,))
		return "".join(s)

	def paragraph(self, text):
		return "<p>%s</p>\n" % (escape(text),)

	def message(self, msgtype, msg, level=1):
		msg = str(msg)
		msgtype = self._MSGTYPESUB.get(msgtype, msgtype)
		if msg.find('\n') > 0:
            if msgtype.find('ERROR') > 0:
                return "<p><span class=\"error\">%s:\n<code>%s</code>\n</span></p>" % (msgtype, \
                    msg.replace('\n', '<br/>'))
            else:
                 return "<p>%s:\n<code>%s</code>\n</p>" % (msgtype, \
                    msg.replace('\n', '<br/>'))
                
		else:
            if msgtype.find('ERROR') > 0:
                return "<p><span class=\"error\">%s: %s</span></p>\n" % (msgtype, escape(msg))

            else:
                return '<p>%s: %s</p>\n' % (msgtype, escape(msg))

	def text(self, text):
		return "<pre>%s</pre>\n" % (text,)

	def url(self, text, url):
		return '<p>%s: <a href="%s">%s</a></p>\n' % (text, url, url)

	def summary(self, text):
		sum = "<pre>%s</pre>\n" % (text,)
		sum =  sum.replace("PASSED", self._MSGTYPESUB["PASSED"])
		sum =  sum.replace("FAILED", self._MSGTYPESUB["FAILED"])
		return sum
	def section(self):
		return "<hr>\n"



if __name__ == "__main__":
	report = reports.get_report((None, "-", "text/html",))
	report.initialize()
	report.info("Some self test info.")
	report.passed("yippee!")
    report.error("ERROR\n2nd line\n")
	report.finalize()

# End of file
