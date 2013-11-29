#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
Useful interactive functions for building simple user interfaces.

"""


__all__ = ['get_text', 'get_input', 'choose', 'yes_no', 'print_menu_list',
'find_source_file']

import sys, os

def get_text(prompt="", msg=None, input=raw_input):
	"""Prompt user to enter multiple lines of text."""

	print (msg or "Enter text.") + " End with ^D or a '.' as first character."
	lines = []
	while True:
		try:
			line = input(prompt)
		except EOFError:
			break
		if line == ".": #  dot on a line by itself also ends
			break
		lines.append(line)
	return "\n".join(lines)

def get_input(prompt="", default=None, input=raw_input):
	"""Get user input with an optional default value."""
	if default:
		ri = input("%s [%s]> " % (prompt, default))
		if not ri:
			return default
		else:
			return ri
	else:
		return input("%s> " % (prompt, ))

def choose(somelist, defidx=0, prompt="choose", input=raw_input):
	"""Select an item from a list."""
	assert len(list(somelist)) > 0, "list to choose from has no elements!"
	print_menu_list(somelist)
	defidx = int(defidx)
	assert defidx >=0 and defidx < len(somelist), "default index out of range."
	try:
		ri = get_input(prompt, defidx+1, input) # menu list starts at one
	except EOFError:
		return None
	if ri:
		try:
			idx = int(ri)-1
		except ValueError:
			print >>sys.stderr, "Bad selection. Type in the number."
			return None
		else:
			try:
				return somelist[idx]
			except IndexError:
				print >>sys.stderr, "Bad selection. Selection out of range."
				return None
	else:
		return None

def yes_no(prompt, default=True, input=raw_input):
	yesno = get_input(prompt, IF(default, "Y", "N"), input)
	return yesno.upper().startswith("Y")

def print_menu_list(clist, lines=20):
	"""Print a list with leading numeric menu choices. Use two columns in necessary."""
	h = max((len(clist)/2)+1, lines)
	i1, i2 = 1, h+1
	for c1, c2 in map(None, clist[:h], clist[h:]):
		if c2:
			print "%2d: %-33.33s | %2d: %-33.33s" % (i1, c1, i2, c2)
		else:
			print "%2d: %-74.74s" % ( i1, c1)
		i1 += 1
		i2 += 1

def find_source_file(modname):
	"""Find the source file for a module. Give the module, or a name of one."""
	if type(modname) is str:
		try:
			if "." in modname:
				modname = __import__(modname, globals(), locals(), ["*"])
			else:
				modname = __import__(modname)
		except ImportError:
			return None
	try:
		basename, ext = os.path.splitext(modname.__file__)
	except AttributeError: # C modules don't have a __file__ attribute
		return None
	testfile = basename + ".py"
	if os.path.isfile(testfile):
		return testfile
	return None


def _test(argv):
	import string
	l = list(string.ascii_letters)
	c = choose(l)
	print c
	print find_source_file("cliutils")
	print yes_no("testing")

if __name__ == "__main__":
	import sys
	_test(sys.argv)

