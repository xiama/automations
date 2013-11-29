#!/usr/bin/python
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>
"""
This package actually implements the XHTML specification.

the XHTMLDocument class can be used to construct new XHTML documents.
There are many helper methods to construct a document from dtd objects.

"""

import sys
import re, HTMLParser
from htmlentitydefs import entitydefs
from textutils import identifier

TRUE = Enum(1, "true")
FALSE = Enum(0, "false")

import POM

STRICT = "strict"
TRANSITIONAL = "transitional"
FRAMESET = "frameset"
DOCTYPES = {}
DOCTYPES[STRICT] = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "xhtml1-strict.dtd">"""
DOCTYPES[TRANSITIONAL] = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "xhtml1-transitional.dtd">"""
DOCTYPES[FRAMESET] = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "xhtml1-frameset.dtd">"""

NAMESPACE = "http://www.w3.org/1999/xhtml"

# tags known to be inline - use for BeautifulWriter and other type checks
INLINE_SPECIAL = ["span", "bdo", "object", "img", "map"]
# (br is ommitted on purpose - looks better)
INLINE_FONTSTYLE = [ "tt", "i", "b", "big", "small"]
INLINE_PHRASE = [ "em", "strong", "dfn", "code", "samp", "kbd",
	"cite", "var", "abbr", "acronym", "q", "sub", "sup"]
INLINE_FORM = ["input", "select", "textarea", "label", "button"]
INLINE = ["a"] + INLINE_SPECIAL + INLINE_FONTSTYLE + INLINE_PHRASE + INLINE_FORM 

def get_dtd_module(doctype):
	modname = "xhtml1_%s" % (doctype)
	fullname = "dtds.%s" % (modname)
	try:
		return sys.modules[fullname]
	except KeyError:
		pass
	pkg = __import__(fullname)
	mod = getattr(pkg, modname)
	sys.modules[fullname] = mod
	setattr(sys.modules[__name__], modname, mod)
	return mod

# make strings into Text objects, otherwise verify Element object.
def check_object(obj):
	if type(obj) in (str, unicode):
		return POM.Text(obj)
	if isinstance(obj, POM.ElementNode):
		return obj
	raise ValidationError, "bad initializer object: should be string or ElementNode instance."

class XHTMLCOMMENT(POM.Comment):
	pass

class XHTMLElement(POM.ElementNode):
	pass

class XHTMLDocument(POM.POMDocument):
	"""XHTMLDocument(doctype)
	doctype must be one of: STRICT, TRANSITIONAL, or FRAMESET.
	"""
	def __init__(self, doctype=None, lang="en", encoding=None):
		super(XHTMLDocument, self).__init__(encoding=encoding)
		self.lang = lang
		if doctype: # implies new document 
			self.set_doctype(doctype)
			self.root = self.dtd.Html()
			self.root.set_namespace(None) # XHTML tags have no namespace	
			self.head = self.root.add(self.dtd.Head)
			self.body = self.root.add(self.dtd.Body)
	
	# helpers for adding specific elements
	def _set_title(self, title):
		ti = self.head.add(self.dtd.Title)
		ti.append(POM.Text(title))
	def _get_title(self):
		return self.getnode("/html/head/title")
	title = property(_get_title, _set_title)

	def _set_stylesheet(self, url):
		self.head.add(self.dtd.Link, rel="stylesheet", type="text/css", href=url)
	def _get_stylesheet(self):
		return self.getnode("/html/head/link")
	stylesheet = property(_get_stylesheet, _set_stylesheet)

	def set_root(self, rootnode):
		self.root = rootnode
		self.root.xmlns = NAMESPACE
		self.root.set_namespace(None)
		self.head = self.root["head"]
		self.body = self.root["body"]

	def set_doctype(self, doctype):
		self.DOCTYPE = DOCTYPES[doctype]
		self.dtd = get_dtd_module(doctype)
		self.add_dtd(self.dtd)

	def get_parser(self):
		return XHTMLParser(self)
	
	# general add methods
	def add_to_head(self, obj, **kwargs):
		if type(obj) is str:
			obj = getattr(self.dtd, obj)
		return apply(self.head.add, (obj,), kwargs)
	
	def add(self, obj, **kwargs):
		if type(obj) is str:
			obj = getattr(self.dtd, obj)
		return self.body.add(obj, **kwargs)

	def append(self, obj, **kwargs):
		if type(obj) is str:
			obj = self.get_element(obj, **kwargs)
		self.body.append(obj)
	
	def insert(self, ind, obj, **kwargs):
		if type(obj) is str:
			obj = self.get_element(obj, **kwargs)
		self.body.insert(ind, obj)

	# generic element factory
	def get_element(self, name, **kwargs):
		cl = getattr(self.dtd, name)
		inst = apply(cl, (), kwargs)
		inst.set_namespace(None)
		return inst

	def __setitem__(self, ind, obj):
		self.body[ind] = obj
	def __getitem__(self, ind):
		return self.body[ind]
	def __delitem__(self, ind):
		del self.body[ind]

	def get_para(self, **attribs):
		Para = newclass("Para", ParaMixin, self.dtd.P)
		p = Para(**attribs)
		p._init(self.dtd)
		return p

	def add_para(self, text, **attribs):
		p = self.get_para(**attribs)
		t = check_object(text)
		p.append(t)
		self.append(p)
		return p
	
	def add_header(self, level, text):
		hobj = self.get_element("H%d" % (level))
		hobj.append(POM.Text(text))
		self.body.append(hobj)

	def get_unordered_list(self, **attribs):
		Unordered = newclass("Unordered", ListMixin, self.dtd.Ul)
		ul = Unordered(**attribs)
		ul._init(self.dtd)
		return ul

	def add_unordered_list(self, items):
		ul = self.dtd.Ul()
		for item in items:
			li = ul.add(self.dtd.Li)
			li.append(check_object(item))
		self.body.append(ul)
		return ul
	
	def add_ordered_list(self, items):
		ol = self.dtd.Ol()
		for item in items:
			li = ol.add(self.dtd.Li)
			li.append(check_object(item))
		return ol

	def add_anchor(self, obj="", **attribs):
		A = apply(self.dtd.A, (), attribs)
		self.body.append(A)
		if type(obj) is str:
			A.append(POM.Text(obj))
		else:
			A.append(obj)
		return A

	def add_comment(self, text):
		comment = XHTMLCOMMENT(text)
		self.body.append(comment)

	def add_division(self, **attribs):
		div = self.dtd.Div(**attribs)
		self.body.append(div)
		return div
	
	def get_table(self, **kwargs):
		XHTMLTable = newclass("XHTMLTable", TableMixin, self.dtd.Table)
		t= XHTMLTable(**kwargs)
		t._init(self.dtd)
		return t

	def add_table(self, **kwargs):
		t  = self.get_table(**kwargs)
		self.append(t)
		return t

	def get_form(self, **kwargs):
		XHTMLForm = newclass("XHTMLForm", FormMixin, self.dtd.Form)
		# instance of new class, with mixin
		f = XHTMLForm(**kwargs)
		f._init(self.dtd)
		#f.enctype="application/x-www-form-urlencoded"
		f.enctype="multipart/form-data"
		return f

	def add_form(self, **kwargs):
		f = self.get_form(**kwargs)
		self.append(f)
		return f

	def get_area(self, **kwargs):
		Area = newclass("Area", DivMixin, self.dtd.Div)
		area = Area(**kwargs)
		area._init(self.dtd)
		return area

	def add_area(self, **kwargs):
		ar = self.get_area(**kwargs)
		self.append(ar)
		return ar


# container for inline markup
class InlineMixin(object):
	def _init(self, dtd):
		self.dtd = dtd

	def inline(self, name, obj, **attribs):
		obj = check_object(obj)
		ilmc = getattr(self.dtd, name)
		Inline = newclass("Inline", ilmc, InlineMixin)
		il = Inline(**attribs)
		il.append(obj)
		self.append(il)
		return il

	def text(self, text):
		return self.add_text(" "+str(text))

	def bold(self, obj, **attribs):
		return self.inline("B", obj, **attribs)

	def italic(self, obj, **attribs):
		return self.inline("I", obj, **attribs)

	def teletype(self, obj, **attribs):
		return self.inline("Tt", obj, **attribs)

	def big(self, obj, **attribs):
		return self.inline("Big", obj, **attribs)

	def small(self, obj, **attribs):
		return self.inline("Small", obj, **attribs)

	def em(self, obj, **attribs):
		return self.inline("Em", obj, **attribs)

	def strong(self, obj, **attribs):
		return self.inline("Strong", obj, **attribs)

	def dfn(self, obj, **attribs):
		return self.inline("Dfn", obj, **attribs)

	def code(self, obj, **attribs):
		return self.inline("Code", obj, **attribs)

	def quote(self, obj, **attribs):
		return self.inline("Q", obj, **attribs)
	Q = quote

	def sub(self, obj, **attribs):
		return self.inline("Sub", obj, **attribs)

	def sup(self, obj, **attribs):
		return self.inline("Sup", obj, **attribs)

	def samp(self, obj, **attribs):
		return self.inline("Samp", obj, **attribs)

	def kbd(self, obj, **attribs):
		return self.inline("Kbd", obj, **attribs)

	def var(self, obj, **attribs):
		return self.inline("Var", obj, **attribs)

	def cite(self, obj, **attribs):
		return self.inline("Cite", obj, **attribs)

	def abbr(self, obj, **attribs):
		return self.inline("Abbr", obj, **attribs)

	def acronym(self, obj, **attribs):
		return self.inline("Acronym", obj, **attribs)


ParaMixin = InlineMixin

class ListMixin(object):
	def _init(self, dtd):
		self.dtd = dtd
	def add_item(self, obj, **attribs):
		obj = check_object(obj)
		ilmc = getattr(self.dtd, "Li")
		Item = newclass("Item", ilmc, InlineMixin)
		il = Item(**attribs)
		il.append(obj)
		self.append(il)
		return il


# Special support methods for XHTML tables. The makes it easy to produce simple
# tables. easier to produce more complex tables. But it currently does not
# support advanced table features. It allows setting cells by row and column
# index (using a sparse table). The special emit method constructs the row
# structure on the fly.
class TableMixin(object):
	# set document dtd so methods can access it to create sub-elements
	def _init(self, dtd):
		self.dtd = dtd
		self._t_caption = None # only one
		self._headings = None
		self._t_rows = []

	def caption(self, content, **kwargs):
		# enforce the rule that there is only one caption, and it is first
		# element in the table.
		cap = self.dtd.Caption(**kwargs)
		cap.append(check_object(content))
		self._t_caption = cap

	def get_headings(self):
		return self._headings # a row (tr) object.

	def set_heading(self, col, val):
		"""Set heading at column <col> (origin 1) to <val>."""
		val = check_object(val)
		if not self._headings:
			self._headings = self.dtd.Tr()
		# auto-fill intermediate cells, if necessary.
		for inter in range(col - len(self._headings)):
			self._headings.append(self.dtd.Th())
		th = self._headings[col-1]
		th.append(val)
		return th # so you can set attributes...

	def set(self, col, row, val):
		val = check_object(val)
		for inter in range(row - len(self._t_rows)):
			self._t_rows.append( self.dtd.Tr())
		r = self._t_rows[row-1]
		for inter in range(col - len(r)):
			r.append( self.dtd.Td())
		td = r[col-1]
		td.append(val)
		return td

	def get(self, col, row):
		r = self._t_rows[row-1]
		return r[col-1]

	def delete(self, col, row):
		r = self._t_rows[row-1]
		del r[col-1]
		if len(r) == 0:
			del self._t_rows[row-1]

	def emit(self, fo):
		self._verify_attributes()
		fo.write("<%s%s%s>" % (self._get_ns(), self._name, self._attr_str()))
		if self._t_caption:
			self._t_caption.emit(fo)
		if self._headings:
			self._headings.emit(fo)
		for row in self._t_rows:
			row.emit(fo)
		fo.write("</%s%s>" % (self._get_ns(), self._name))


class FormMixin(object):
	def _init(self, dtd):
		self.dtd = dtd
	
	def get_textarea(self, text, name=None, rows=4, cols=60):
		text = check_object(text)
		textclass = newclass("TextWidget", TextareaMixin, self.dtd.Textarea)
		ta = textclass(name=name, rows=rows, cols=cols)
		ta.append(text)
		return ta

	def add_textarea(self, text, name=None, rows=4, cols=60):
		ta = self.get_textarea(text, name, rows, cols)
		self.append(ta)
		return ta
	
	def get_input(self, **kwargs):
		inputclass = newclass("InputWidget", InputMixin, self.dtd.Input)
		inp = inputclass(**kwargs)
		return inp
	
	def add_input(self, **kwargs):
		inp = self.get_input(**kwargs)
		self.append(inp)
		return inp

	def add_textinput(self, name, label=None, size=30, default=None, maxlength=None):
		if label:
			lbl = self.dtd.Label()
			setattr(lbl, "for", name) # 'for' is a keyword...
			lbl.append(check_object(label))
			self.append(lbl)
		self.append(self.dtd.Input(type="text", name=name, value=default, 
				maxlength=maxlength))

	def get_select(self, items, **kwargs):
		sl = self.dtd.Select(**kwargs)
		for item in items:
			opt = self.dtd.Option()
			opt.append(POM.Text(str(item)))
			sl.append(opt)
		return sl

	def add_select(self, items, **kwargs):
		sl = self.get_select( items, **kwargs)
		self.append(sl)
		return sl

	def add_radiobuttons(self, name, items, vertical=False):
		for i, item in enumerate(items):
			self.append(self.dtd.Input(type="radio", name=name, value=i))
			self.append(check_object(item))
			if i == 0:
				self[-2].checked = TRUE # default to first one checked
			if vertical:
				self.append(self.dtd.Br())

	def add_checkboxes(self, name, items, vertical=False):
		for i, item in enumerate(items):
			self.append(self.dtd.Input(type="checkbox", name=name, value=i))
			self.append(check_object(item))
			if vertical:
				self.append(self.dtd.Br())

	def add_fileinput(self, name="fileinput", default=None):
		self.append(self.dtd.Input(type="file", name=name, value=default))


class WidgetBase(object):
	pass

class StringWidget(WidgetBase):
	pass

class PasswordWidget(StringWidget):
	pass

class TextareaMixin(WidgetBase):
	pass

class InputMixin(WidgetBase):
	"""type = (text | password | checkbox | radio | submit | reset |
    file | hidden | image | button) """
	pass

# container for other objects (Div) for layout purposes
# Use CSS to define the area properties.
class DivMixin(object):
	def _init(self, dtd):
		self.dtd = dtd


# XHTML POM parser. This parser populates the POM with XHTML objects, so this
# HTML parser essentially translates HTML to XHTML, hopefully with good
# results.
class XHTMLParser(HTMLParser.HTMLParser):
	def __init__(self, doc):
		self.reset()
		self.topelement = None
		self.doc=doc
		self.stack = []

	def close(self):
		if self.stack:
			raise POM.ValidationError, "XHTML document has unmatched tags"
		HTMLParser.HTMLParser.close(self)
		self.doc.set_root(self.topelement)

	def parse(self, url):
		import urllib
		fo = urllib.urlopen(url)
		self.parseFile(fo)
		self.close()
		
	def parseFile(self, fo):
		data = fo.read(16384)
		while data:
			self.feed(data)
			data = fo.read(16384)
		self.close()

	def _get_tag_obj(self, tag, attrs):
		attrdict = {}
		def fixatts(t):
			attrdict[t[0]] = t[1]
		map(fixatts, attrs)
		cl = getattr(self.doc.dtd, identifier(tag))
		cl.__bases__ = (XHTMLElement,) # XXX quck hack
		obj = apply(cl, (), attrdict)
		return obj

	def handle_starttag(self, tag, attrs):
		obj = self._get_tag_obj(tag, attrs)
		if obj.CONTENTMODEL.is_empty():
			self.stack[-1].append(obj)
			return
		if not self.stack:
			obj.set_namespace(None)
		self.stack.append(obj)

	def handle_endtag(self, tag):
		"Handle an event for the end of a tag."
		obj = self.stack.pop()
		if self.stack:
			self.stack[-1].append(obj)
		else:
			self.topelement = obj
	
	def handle_startendtag(self, tag, attrs):
		obj = self._get_tag_obj(tag, attrs)
		self.stack[-1].append(obj)
		
	def handle_data(self, data):
		if self.stack:
			self.stack[-1].add_text(data)
		else:
			#print >>sys.stderr, "XHTMLParser: kruft warning: %s: %r" % (self.getpos(), data,)
			pass
	
	def handle_charref(self, name):
		print >>sys.stderr, "!!! unhandled charref:", repr(name)
	
	def handle_entityref(self, name):
		if self.stack:
			self.stack[-1].add_text(entitydefs[name])

	def handle_comment(self, data):
		self.stack[-1].append(POM.Comment(data))

	def handle_decl(self, decl):
		if decl.startswith("DOCTYPE"):
			if decl.find("Strict") > 1:
				self.doc.set_doctype(STRICT)
			elif decl.find("Frameset") > 1:
				self.doc.set_doctype(FRAMESET)
			elif decl.find("Transitional") > 1:
				self.doc.set_doctype(TRANSITIONAL)
			else:
				raise POM.ValidationError, "unknown DOCTYPE: %r" % (decl,)
		else:
			print >>sys.stderr, "!!! Unhandled decl: %r" % (decl,)

	def handle_pi(self, data):
		'xml version="1.0" encoding="ISO-8859-1"?'
		mo = re.match('xml version="([0123456789.]+)" encoding="([A-Z0-9-]+)"', data, re.IGNORECASE)
		if mo:
			version, encoding = mo.groups()
			assert version == "1.0"
			self.doc.set_encoding(encoding)
		else:
			print >>sys.stderr, "!!! Unhandled pi: %r" % (data,)


def new_document(doctype):
	doc = XHTMLDocument(doctype)
	return doc

def get_document(url):
	doc = XHTMLDocument()
	p = doc.get_parser()
	p.parse(url)
	return doc


if __name__ == "__main__":
	import os
	os.system("qaunittest xhtml")

