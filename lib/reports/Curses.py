#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
# 
#

"""
Report object that connects to CLI CursesIO object.

"""

import sys

import reports
import cursesio

class CursesReport(reports.NullReport):
    def __init__(self, ui=None):
        self._ui = ui or cursesio.get_curses_ui()

    def write(self, text):
        return self._ui.write(text)
    def writeline(self, text=""):
        return self._ui.writeline(text)
    def writelines(self, lines):
        return self._ui.writelines(lines)

	def initialize(self, *args): pass
	def logfile(self, filename): pass
	def finalize(self): pass
	def add_title(self, title): pass
	def add_heading(self, text, level=1): pass
	def add_message(self, msgtype, msg, level=1):
        self._ui.write("%s%s: %s\n" % ("  "*(level-1), msgtype, msg))
# XXX
	def add_summary(self, text): pass
	def add_text(self, text): pass
	def add_url(self, text, url): pass
	def passed(self, msg=NO_MESSAGE): pass
	def failed(self, msg=NO_MESSAGE): pass
	def incomplete(self, msg=NO_MESSAGE): pass
	def abort(self, msg=NO_MESSAGE): pass
	def info(self, msg): pass
	def diagnostic(self, msg): pass
	def newpage(self): pass
	def newsection(self): pass



def _test(argv):
    pass # XXX

if __name__ == "__main__":
    _test(sys.argv)
