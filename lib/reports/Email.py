#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
Report objects that sends a text email.

"""

import sys, os
import reports
NO_MESSAGE = reports.NO_MESSAGE

from cStringIO import StringIO

import ezmail

class ReportMessage(ezmail.MIMEMultipart.MIMEMultipart, ezmail.AutoMessageMixin):
	def __init__(self, From=None, To=None):
		ezmail.MIMEMultipart.MIMEMultipart.__init__(self)
		ezmail.AutoMessageMixin.__init__(self, From, To)

class EmailReport(reports.NullReport):
	"""Create an a report that is emailed, rather than written to a file. 
	EmailReport(
		[formatter="text/plain"],  # formatter type
		[recipients=None],         # list of recipients, or None. If none the
		                           # message is mailed to self (From address).
		[From=None],               # Address for From field. If None the current user is used.
		)

	"""
	def __init__(self, formatter="text/plain", recipients=None, From=None):
		self._logfile = None
		self._message = ReportMessage()
		self._message.From(From)
		self._message.To(recipients)
		self._formatter, ext = reports.get_formatter(formatter)

	filename = property(lambda s: None)
	filenames = property(lambda s: [])
	mimetype = property(lambda s: s._formatter.MIMETYPE)

	def initialize(self):
		self._fo = StringIO()
		self.write(self._formatter.initialize())

	def logfile(self, lf):
		self._logfile = str(lf)

	def write(self, text):
		self._fo.write(text)

	def writeline(self, text):
		self._fo.write(text)
		self._fo.write("\n")

	def finalize(self):
		"""finalizing this Report sends off the email."""
		self.write(self._formatter.finalize())
		report = ezmail.MIMEText.MIMEText(self._fo.getvalue(), self._formatter.MIMETYPE.split("/")[1])
		report["Content-Disposition"] = "inline"
		self._message.attach(report)
		if self._logfile:
			try:
				lfd = file(self._logfile).read()
			except:
				pass # non-fatal
				print >>sys.stderr, "could not read or attach log file: %r" % (self._logfile,)
			else:
				logmsg = ezmail.MIMEText.MIMEText(lfd)
				logmsg["Content-Disposition"] = 'attachment; filename=%s' % (os.path.basename(self._logfile), )
				self._message.attach(logmsg)
		ezmail.mail(self._message)

	def add_title(self, title):
		self._message.add_header("Subject", title)
		self.write(self._formatter.title(title))

	def add_heading(self, text, level=1):
		self.write(self._formatter.heading(text, level))

	def add_message(self, msgtype, msg, level=1):
		self.write(self._formatter.message(msgtype, msg, level))

	def add_summary(self, text):
		self.write(self._formatter.summary(text))

	def passed(self, msg=NO_MESSAGE):
		self.add_message("PASSED", msg)

	def failed(self, msg=NO_MESSAGE):
		self.add_message("FAILED", msg)

	def incomplete(self, msg=NO_MESSAGE):
		self.add_message("INCOMPLETE", msg)

	def abort(self, msg=NO_MESSAGE):
		self.add_message("ABORTED", msg)

	def info(self, msg):
		self.add_message("INFO", msg)

	def diagnostic(self, msg):
		self.add_message("DIAGNOSTIC", msg)

	def add_text(self, text):
		self.write(self._formatter.text(text))

	def add_url(self, text, url):
		self.write(self._formatter.url(text, url))

	def newpage(self):
		self.write(self._formatter.newpage())

	def newsection(self):
		self.write(self._formatter.section())



if __name__ == "__main__":
	rpt = EmailReport("text/plain", recipients=["kdart@kdart.com"])
	rpt.initialize()
	rpt.add_title("Email report self test.")
	rpt.info("Some non-useful info. 8-)")
	rpt.finalize()


