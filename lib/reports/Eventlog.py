#!/usr/bin/python
# vim:ts=4:sw=4:softtabstop=0:smarttab
# 
#    Copyright (C) 1999-2004  Keith Dart <kdart@kdart.com>
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.

"""
A report type the produces an event log with time stamps.

"""

import reports
import timelib
now = timelib.time


class LogFormatter(reports.StandardFormatter):
	MIMETYPE = "text/plain"

	def message(self, msgtype, msg, level=1):
		return "%s:%s: %s\n" % (now(), msgtype, msg)

	# no summary for logs
	def summary(self, text):
		return "%s:%s:\n" % (now(), "SUMMARY")


