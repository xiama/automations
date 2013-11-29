#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""

<http://www.w3.org/TR/2000/REC-xml-20001006#sec-prolog-dtd>

XXX needs work

"""

#[28]    doctypedecl    ::=    '<!DOCTYPE' S Name (S ExternalID)? S? ('[' (markupdecl | DeclSep)* ']' S?)? '>'
#[28a]    DeclSep    ::=    PEReference | S [WFC: PE Between Declarations]
#[29]    markupdecl    ::=    elementdecl | AttlistDecl | EntityDecl | NotationDecl | PI | Comment


class Doctype(object):
	def __init__(self, name, public, system=""):
		self.name = name
		self.publicid = public
		self.system = system
	def __str__(self):
		return '<!DOCTYPE %s PUBLIC "%s" SYSTEM "%s">' % (self.name, self.publicid, self.system)

def get_doctype(name, public, system=""):
	return Doctype(name, public, system)


