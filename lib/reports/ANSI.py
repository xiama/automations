#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
A standard formatter enhanced to support ANSI terminal color output.

"""

import reports

RESET = "\x1b[0m"
RED = "\x1b[31;01m"
YELLOW = "\x1b[33;01m"
GREEN = "\x1b[32;01m"
BLUE = "\x1b[34;01m"
WHITE = "\x1b[01m"


class ANSIFormatter(reports.StandardFormatter):
	MIMETYPE = "text/ansi"
	_TRANSLATE = {
		"PASSED":GREEN+'PASSED'+RESET,
		"FAILED":RED+'FAILED'+RESET,
		"ABORTED":YELLOW+'ABORTED'+RESET,
		"INCOMPLETE":YELLOW+'INCOMPLETE'+RESET,
		"ABORT":YELLOW+'ABORT'+RESET,
		"INFO":"INFO",
		"DIAGNOSTIC":WHITE+'DIAGNOSTIC'+RESET,
	}

	def message(self, msgtype, msg, level=1):
		msgtype = self._TRANSLATE.get(msgtype, msgtype)
		return "%s%s: %s\n" % ("  "*(level-1), msgtype, msg)

	def summary(self, text):
		text = text.replace("PASSED", self._TRANSLATE["PASSED"])
		text = text.replace("FAILED", self._TRANSLATE["FAILED"])
		text = text.replace("INCOMPLETE", self._TRANSLATE["INCOMPLETE"])
		text = text.replace("ABORTED", self._TRANSLATE["ABORTED"])
		return text


def _test(argv):
	pass # XXX

if __name__ == "__main__":
	import sys
	_test(sys.argv)

