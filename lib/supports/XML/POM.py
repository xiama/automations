#!/usr/bin/python -i
# vim:ts=4:sw=4:softtabstop=0:smarttab
# License: LGPL
# Keith Dart <kdart@kdart.com>

"""
This module implements the XML POM -- the Python Object Model for XML. It is
something like DOM, but more Pythonic, and easier to use. These base classes
are used to build POM source files which are self-validating python-based XML
constructor objects. The major parts of the dtd2py command line tool are also
here.

"""

import sys, os, re


try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

from textutils import identifier, maketrans

DEFAULT_ENCODING = "utf-8"

def set_default_encoding(newcodec):
	global DEFAULT_ENCODING 
	DEFAULT_ENCODING = str(newcodec)

try:
	True
except NameError:
	True = 1
	False = 0


class ValidationError(ValueError):
	"""ValidationError
	This exception is raised when an attempt is made to construct an XML POM
	tree that would be invalid.

	"""
	pass
add_exception(ValidationError)

def get_getter(dtdmod):
	def _element_getter(dtdmod, nodename):
		return getattr(dtdmod, identifier(nodename))
	return curry(_element_getter, dtdmod)


#########################################################
# XML generating classes
# These classes are used to generate XML documents, similar to DOM. But, this
# interface is simpler and more Python-ic.
#########################################################
# plain text data to be added to a GenericNode.
# This class needs to support much of the ElementNode interface, but
# implemented differently.
class Text(object):
	def __init__(self, data="", encoding=None):
		self._parent = None
		self.set_text(data, encoding)
	def set_text(self, data, encoding=None):
		enc = encoding or DEFAULT_ENCODING
		self.data = unescape(POMString(data, enc))
		self.encoding = enc
	def get_text(self):
		return self.data
	def insert(self, data, encoding=None):
		self.data = unescape(POMString(data, encoding or self.encoding)) + self.data
	def add_text(self,data, encoding=None):
		self.data += unescape(POMString(data, encoding or self.encoding))
	append = add_text
	__iadd__ = add_text
	def __str__(self):
		return escape(str(self.data))
	def __unicode__(self):
		return escape(self.data)
	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%r)" % (cl.__module__, cl.__name__, escape(self.data))
	def __len__(self):
		return len(self.data)
	def __getslice__(self, start, end):
		return self.data[start:end]
	def __setslice__(self, start, end, v):
		self.data[start:end] = v
	def __delslice__(self, start, end):
		del self.data[start:end]
	def get_escape_length(self):
		return len(escape(self.data))
	def destroy(self):
		self.data = None
		self._parent = None
	def fullpath(self):
		if self._parent:
			return "%s = %r" % (self._parent.fullpath(), self.data)
		else:
			return `self.data`
	def emit(self, fo):
		fo.write( escape(self.data) )
	# dummy methods, for polymorphism with ElementNode
	def matchpath(self, pe):
		return 0
	def has_children(self):
		return 0
	def has_attributes(self):
		return 0

class Comment(Text):
	def __init__(self, data="", encoding=None):
		self.data = POMString(data, encoding or DEFAULT_ENCODING)
		self._parent = None
	def __str__(self):
		return "<!-- %s -->" % (self._fix(self.data),)
	def __unicode__(self):
		return u"<!-- %s -->" % (self._fix(self.data),)
	def emit(self, fo):
		fo.write( self.__str__() )
	def set_text(self, data):
		self.data = POMString(data)
	def get_text(self):
		return self.data
	def insert(self, data):
		self.data = POMString(data) + self.data
	def add_text(self,data, encoding=None):
		self.data += POMString(data, encoding or DEFAULT_ENCODING)
	append = add_text
	def _fix(self, data):
		data = escape(data)
		if data.find(u"--") != -1:
			data = data.replace(u"--", u"- ")
		return data

class ASIS(object):
	"""Holder for pre-made markup that may be inserted into POM tree. It is a
	text leaf-node only. You can cache pre-constructed markup and insert it
	into the POM to speed up some page emission.  """
	def __init__(self, data, encoding=None):
		self._parent = None
		self.set_text(data, encoding)
	def set_text(self, data, encoding=None):
		enc = encoding or DEFAULT_ENCODING
		self.data = POMString(data, enc)
		self.encoding = enc
	def get_text(self):
		return self.data
	def insert(self, data, encoding=None):
		raise NotImplementedError
	def add_text(self,data, encoding=None):
		raise NotImplementedError
	append = add_text
	__iadd__ = add_text
	def __str__(self):
		return str(self.data)
	def __unicode__(self):
		return self.data
	def __repr__(self):
		cl = self.__class__
		return "%s.%s()" % (cl.__module__, cl.__name__)
	def __len__(self):
		return len(self.data)
	def __getslice__(self, start, end):
		return self.data[start:end]
	def __setslice__(self, start, end, v):
		self.data[start:end] = v
	def __delslice__(self, start, end):
		del self.data[start:end]
	def get_escape_length(self):
		return len(self.data)
	def destroy(self):
		self.data = None
		self._parent = None
	def fullpath(self):
		if self._parent:
			return "%s = %r" % (self._parent.fullpath(), self.data)
		else:
			return `self.data`
	def emit(self, fo):
		fo.write( self.data )
	# dummy methods, for polymorphism with ElementNode
	def matchpath(self, pe):
		return 0
	def has_children(self):
		return 0
	def has_attributes(self):
		return 0


# abstract base class for generic XML node generation. 
# Create an XML node by subclassing this and defining allowed attribute names
# in ATTLIST. CONTENTMODEL holds the content specification from the DTD.
# Use the dtd2py program to convert a DTD to a python module that has classes
# for element types. Use that python dtd as a paramter for the POMDocument,
# below.

class ElementNode(object):
	ATTLIST = None
	CONTENTMODEL = None
	_name = None
	_namespace = None
	_acquired = {"_namespace":None } # default acquired values
	def __init__(self, **attribs):
		self._attribs = {}
		for key, value in attribs.items():
			if self._validate_attribute(key, value):
				self._attribs[key] = value
			else:
				raise ValidationError, "invalid attribute name for this element"
		self._children = []
		self._parent = None

 	# check if attribute name is defined for this element
	def _validate_attribute_name(self, name):
		if self.ATTLIST:
			for xmlattr in self.ATTLIST:
				if name == xmlattr.name:
					return True
		return False

	def _validate_attribute(self, name, value):
		if self.ATTLIST:
			for xmlattr in self.ATTLIST:
				if name == xmlattr.name:
					return xmlattr.verify(value)
		return False
	
	def _verify_attributes(self):
		if not self.ATTLIST:
			return None
		for attr in self.ATTLIST:
			aval = self._attribs.get(attr.name, None)
			if aval is None:
				if attr.a_decl == REQUIRED:
					raise ValidationError, "required attribute not present: " + attr.name
			else:
				attr.verify(aval)

	def _get_attribute(self, name):
		if not self.ATTLIST:
			return None
		try:
			return self._attribs[name]
		except KeyError:
			# might be implied, fixed, or enum...
			for xmlattr in self.ATTLIST:
				if name == xmlattr.name:
					if xmlattr.a_decl == IMPLIED:
						return ""
					elif xmlattr.a_decl == FIXED:
						return xmlattr.default
					elif xmlattr.a_decl == DEFAULT: # an enum type
						return xmlattr.default
		return None
		
	def get_parent(self):
		return self._parent
	
	def reparent(self, newparent):
		if self._parent:
			i = self._parent.index(self)
			del self._parent[i]
		newparent.append(self)
	
	def detach(self):
		self._parent = None

	def destroy(self):
		"""destroy() Remove this node and all child node references."""
		# remove parent _children list reference
		if self._parent:
			i = self._parent.index(self)
			del self._parent[i]
		self._parent = None
		for n in self._children:
			n.detach()
		self._children = None
	
	def set_namespace(self, ns):
		self._namespace = ns

	def index(self, obj):
		objid = id(obj)
		i = 0
		for o in self._children:
			if id(o) == objid:
				return i
			i += 1
		raise ValueError, "ElementNode: Object not contained here."

	def append(self, obj):
		"""Append an existing DTD object instance."""
		obj._parent = self
		self._children.append(obj)
	
	def extend(self, objlist):
		for obj in objlist:
			self.append(obj)

	def insert(self, index, obj):
		obj._parent = self
		self._children.insert(index, obj)

	def add(self, klass, **kwargs):
		"""Add an element class from a dtd module."""
		obj = apply(klass, (), kwargs)
		self.append(obj)
		return obj

	def get_children(self):
		return self._children[:]

	def __iter__(self):
		return iter(self._children)

	def add_text(self, text, encoding=None):
		"Adding text to elements is so common, there is a special method for it."
		if self.has_children() and isinstance(self._children[-1], Text):
			self._children[-1].add_text(text, encoding)
		else:
			t = Text(text, encoding)
			self.append(t)
	
	def replace_text(self, text):
		if self._children:
			del self._children[-1]
		self.append(Text(text))

	def __len__(self):
		return len(self._children)
	
	# The truth is, we exist.
	def __nonzero__(self):
		return True

	def hasAttributes(self):
		return len(self._attribs)
	has_attributes = hasAttributes
	
	def has_attribute(self, name):
		if name in self._attribs.keys():
			return True
		else:
			return False

	def attributes(self):
		return map(lambda o: o.name, self.ATTLIST)

	def has_children(self):
		return len(self._children)

	def set_attribute(self, name, val):
		"""set_attribute(name, value)
		This exists to set attributes that have names with characters that make
		it an illegal Python identifier.  """
		if self._validate_attribute(name, val):
			self._attribs[name] = val

	def get_attribute(self, name):
		"""get_attribute(name)
		Use this method to get attributes that have names with characters that make
		it an illegal Python identifier.  """
		return self._get_attribute(name)

	def __setattr__(self, name, value):
		if self._validate_attribute(name, value):
			self._attribs[name] = value
		else:
			self.__dict__[name] = value

	# this plus the _parent and _acquired attributes implement "acquisiton", 
	# or run-time inheritance.
	def __getattr__(self, name):
		defval = self._get_attribute(name)
		if defval is not None:
			return defval
		try:
			return self._acquire(name)
		except:
			pass
		raise AttributeError, "AttributeError: %s has no attribute '%s'" % (self._name, name)

	def _acquire(self, name):
		if self._parent:
			try:
				return self._parent.__dict__[name]
			except KeyError:
				pass
			return self._parent._acquire(name)
		else:
			try:
				return self._acquired[name]
			except KeyError:
				pass
		raise AttributeError

	def __delattr__(self, name):
		del self._attribs[name]

	def _find_index(self, index):
		if type(index) is str:
			for i in xrange(len(self._children)):
				if self._children[i].matchpath(index):
					return i
			raise IndexError, "no elements match"
		else:
			return index

	def __getitem__(self, index):
		if type(index) is str:
			el =  self.get_element(index)
			if el is None:
				raise IndexError, "no item matches"
			else:
				return el
		else:
			return self._children[index]
	
	def __setitem__(self, index, obj):
		index = self._find_index(index)
		obj._parent = self
		self._children[index] = obj
	
	def __delitem__(self, index):
		index = self._find_index(index)
#		self._children[index].destroy()
		del self._children[index]

	def __repr__(self):
		attrs = map(lambda t: '%s=%r' % t, self._attribs.items())
		cl = self.__class__
		return "%s.%s(%s)" % (cl.__module__, cl.__name__, ", ".join(attrs))

	def __str__(self):
		self._verify_attributes()
		if not self.CONTENTMODEL or self.CONTENTMODEL.is_empty():
			return self._empty_str()
		else:
			return self._non_empty_str()
	
	def _get_ns(self):
		return IF(self._namespace, "%s:" % self._namespace, "")

	def _non_empty_str(self):
		s = ["<%s%s%s>" % (self._get_ns(), self._name, self._attr_str())]
		map(s.append, map(str, self._children))
		s.append("</%s%s>" % (self._get_ns(), self._name))
		return "".join(s)

	def _empty_str(self):
		return "<%s%s%s />" % (self._get_ns(), self._name, self._attr_str())
	
	def _attr_str(self):
		attrs = map(lambda t: ' %s="%s"' % t, map(lambda t: (t[0], escape(str(t[1]))), filter(lambda t: t[1] is not None, self._attribs.items())))
		return "".join(attrs)

	def emit(self, fo):
		self._verify_attributes()
		if not self.CONTENTMODEL or self.CONTENTMODEL.is_empty():
			fo.write(self._empty_str())
		else:
			fo.write("<%s%s%s>" % (self._get_ns(), self._name, self._attr_str()))
			map(lambda o: o.emit(fo), self._children)
			fo.write("</%s%s>" % (self._get_ns(), self._name))

	# methods for node path manipulation
	def pathname(self):
		"""pathname() returns the ElementNode as a string in xpath format."""
		if self._attribs:
			s = map(lambda i: "@%s='%s'" % (i[0],i[1]), self._attribs.items())
			return "%s[%s]" % (self.__class__.__name__, " and ".join(s))
		else:
			return self.__class__.__name__

	def fullpath(self):
		"""fullpath() returns the ElementNode's full path as a string in xpath format."""
		if self._parent:
			base = self._parent.fullpath()
		else:
			base = ""
		return "%s/%s" % (base, self.pathname() )

	def matchpath(self, pathelement):
		if "[" not in pathelement:
			return pathelement == self._name
		else:
			xpath_re = re.compile(r'(\w*)(\[.*])')
			mo = xpath_re.match(pathelement)
			if mo:
				name, match = mo.groups()
				match = match.replace("@", "self.")
				match = match.replace("=", "==")
				return (name == self._name and eval(match[1:-1]))
			else:
				raise ValueError, "Invalid path element"

	def find_elements(self, pathelement):
		rv = []
		for child in self._children:
			if child.matchpath(pathelement):
				rv.append(child)
		return rv
	
	def get_element(self, pathelement):
		for child in self._children:
			if child.matchpath(pathelement):
				return child
		return None

	def elements(self, elclass):
		"""Return iterator that iterates over list of elements matching elclass"""
		return NodeIterator(self, elclass)

	def _find_node(self, eltype, collect=None):
		if collect is None:
			collection = []
		else:
			collection = collect # should be a list
		for el in self._children:
			if el.has_children():
				el._find_node(eltype, collection)
			if isinstance(el, eltype):
				collection.append(el)
		return collection

	def find(self, elclass, **attribs):
		for obj in self._children:
			if isinstance(obj, elclass):
				if self._attribs_match(obj, attribs):
					return obj
		return None

	def getall(self, elclass, depth=0, collect=None):
		if collect is None:
			rv = []
		else:
			rv = collect # should be a list
		for el in self._children:
			if isinstance(el, elclass):
				rv.append(el)
			if depth > 0:
				el.getall(elclass, depth-1, rv)
		return rv

	def _attribs_match(self, obj, attribdict):
		for tname, tval in attribdict.items():
			try:
				if getattr(obj, tname) != tval:
					return 0
			except AttributeError:
				return 0
		return 1

	# XPath-like functions
	def comment(self):
		return self._find_node(Comment)

	def text(self):
		return self._find_node(Text)

	def processing_instruction(self):
		return self._find_node(ProcessingInstruction)
	
	def node(self):
		return self._find_node(ElementNode)


class NodeIterator(object):
	def __init__(self, node, elclass):
		self.node = node
		self.elclass = elclass
		self.i = 0

	def __iter__(self):
		return self

	def next(self):
		while 1:
			try:
				n = self.node[self.i]
			except IndexError:
				raise StopIteration
			self.i += 1
			if isinstance(n, elclass):
				break
		return n


def find_nodes(node, elclass):
	if isinstance(node, elclass):
		yield node
	for child in node.get_children():
		for cn in find_nodes(child, elclass):
			yield cn
	return


class Fragments(ElementNode):
	"""Fragments is a special holder class to hold 'loose' markup fragments.
	That is, bits of markup that don't have a common container (e.g. not in
	root element).  It is invisible."""
	def __str__(self):
		s = []
		map(s.append, map(str, self._children))
		return "".join(s)

	def emit(self, fo):
		map(lambda o: o.emit(fo), self._children)


class POMString(unicode):
	def __new__(cls, arg, enc=None):
		if type(arg) is unicode:
			return unicode.__new__(cls, arg)
		if not enc:
			enc = sys.getdefaultencoding()
		return unicode.__new__(cls, arg, enc)


class POMTimeStamp(long):
	pass


class BeautifulWriter(object):
	"""A wrapper for a file-like object that is itself a file-like object. It
	is basically a shim. It attempts to beautify the XML stream emitted by the
	POM tree. Pass one of these to the emit method if you want better looking
	output."""
	def __init__(self, fo, inline=[]):
		self._fo = fo # the wrapped file object
		self._inline = list(inline) # list of special tags that are inline
		self._level = 0
		self._tagre = re.compile(r"<([-a-zA-Z0-9_:]+)") # start tag
	def __getattr__(self, name):
		return getattr(self._fo, name)

	def write(self, data):
		if data.endswith("/>"):
			self._fo.write("\n"+"  "*self._level)
			return self._fo.write(data)
		if data.startswith("</"):
			self._level -= 1
			self._fo.write("\n"+"  "*self._level)
			return self._fo.write(data)
		mo = self._tagre.search(data)
		if mo:
			if str(mo.group(1)) in self._inline:
				return self._fo.write(data)
			else:
				self._fo.write("\n"+"  "*self._level)
				self._level += 1
				return self._fo.write(data)
		return self._fo.write(data)


# base class for whole POM documents, including Header.
class POMDocument(object):
	DOCTYPE = "\n"
	XMLHEADER = '<?xml version="1.0" encoding="%s"?>\n' %(DEFAULT_ENCODING,) # default
	def __init__(self, dtd=None, encoding=None):
		self.dtds = []
		self._getters = []
		self.root = None
		self.parser = None
		self.dirty = 0
		if encoding:
			self.set_encoding(encoding)
		if dtd:
			self.add_dtd(dtd)

	def __str__(self):
		return self.XMLHEADER + self.DOCTYPE + str(self.root) + "\n"

	def emit(self, fo):
		fo.write(self.XMLHEADER)
		fo.write(self.DOCTYPE)
		fo.write("\n")
		self.root.emit(fo)
		fo.write("\n")

	def set_dirty(self, val=1):
		self.dirty = val

	def set_root(self, root):
		"""Forcibly set the root document. Be careful with this."""
		if isinstance(root, ElementNode):
			self.root = root
		else:
			raise ValueError, "root document must be POM ElementNode."

	def add_dtd(self, dtdmod):
		self.dtds.append(dtdmod)
		self._getters.append(get_getter(dtdmod))

	def get_elementnode(self, name):
		for getter in self._getters:
			try:
				return getter(name)
			except AttributeError:
				continue
	
	def set_encoding(self, encoding):
		# verify encoding is valid
		import codecs
		try:
			codecs.lookup(encoding)
		except codecs.LookupError, err:
			raise ValueError, err.args[0]
		self.XMLHEADER = '<?xml version="1.0" encoding="%s"?>\n' %(encoding,)
		self.encoding = encoding
	
	def set_doctype(self, doctype):
		self.DOCTYPE = str(doctype)

	def get_parser(self, handlerclass=None):
		self.parser = get_parser(self.dtds, handlerclass or ObjectParserHandler, self._callback)
		return self.parser
	
	def del_parser(self):
		self.parser = None

	def _callback(self, doc):
		self.root = doc
		self.dirty = 0
	
	def parse(self, url, handlerclass=None):
		if not self.parser:
			self.get_parser(handlerclass or ObjectParserHandler)
		self.parser.parse(url)
		self.del_parser()

	def parseFile(self, fo, handlerclass=None):
		if not self.parser:
			self.get_parser(handlerclass or ObjectParserHandler)
		self.parser.parseFile(fo)
		self.del_parser()

	def parseString(self, string, handlerclass=None):
		if not self.parser:
			self.get_parser(handlerclass or ObjectParserHandler)
		self.parser.parseFile(StringIO(string))

	def write_xmlfile(self, filename=None):
		filename = filename or self.filename
		if filename:
			fo = open(os.path.expanduser(filename), "w")
			try:
				self.emit(fo)
			finally:
				fo.close()
		self.dirty = 0
	writefile = write_xmlfile

	def writefileobject(self, fo):
		self.emit(fo)

	def get_document(self, filename):
		self.get_parser()
		self.parse(filename)
		self.filename = filename
	
	def getnode(self, path):
		"""getnode(path) Returns an ElementNode addressed by the path."""
		elements = path.split("/")
		while not elements[0]: # eat empty first element
			elements.pop(0)
		node = self.root
		pathelement = elements.pop(0)
		if node.matchpath(pathelement):
			while elements:
				pathelement = elements.pop(0)
				node = node.get_element(pathelement)
				if node is None:
					raise IndexError, "path element not found"
			return node
		else:
			raise IndexError, "first path element not found"

	def setnode(self, path, text):
		node = self.getnode(path)
		node.replace_text(text)
	
	def delnode(self, path):
		els = path.split("/")
		path, endnode = "/".join(els[:-1]), els[-1]
		node = self.getnode(path)
		del node[endnode]
	
	def addnode(self, basepath, newnode):
		node = self.getnode(basepath)
		node.append(newnode)

	def add_text(self, basepath, text, encoding=None):
		node = self.getnode(basepath)
		node.add_text(text, encoding or self.encoding)

	def _write_text(self, fo, node):
		for n in node:
			if isinstance(n, Text):
				fo.write(n.fullpath())
				fo.write("\n")
			else:
				self._write_text(fo, n)
		
	def write_paths(self, fileobject):
		realfile = 0
		if type(fileobject) is str:
			fileobject = open(fileobject, "w")
			realfile = 1
		self._write_text(fileobject, self.root)
		if realfile:
			fileobject.close()

# parses XML files into a POM object model. A callback function is then called 
# with this object model as a paramter.
class ObjectParserHandler(object):
	def __init__(self, callback, module=None):
		self.stack = []
		self.msg = None
		self.callback = callback # gets called when message fully parsed. The
		                         # argument is the toplevel message object.
		self.modules = []
		if module is not None:
			if type(module) is list:
				self.modules.extend(module)
			else:
				self.modules.append(module)

	def add_module(self, module):
		self.modules.append(module)

	def _get_class(self, name):
		klass = None
		for mod in self.modules:
			try:
				klass = getattr(mod, identifier(name)) # name dtd compiler translated to
			except AttributeError:
				continue
			if klass:
				return klass
		raise AttributeError

	def startDocument(self):
		self.stack = []

	def endDocument(self):
		if self.stack: # stack should be empty now
			raise ValidationError, "unbalanced document!"
		self.callback(self.msg)
		self.msg = None

	def startElement(self, name, atts):
		"Handle an event for the beginning of an element."
		try:
			klass = self._get_class(name)
		except AttributeError:
			raise ValidationError, "Undefined element tag: "+name
		attr = {} # atts is a instance with unicode keys.. must convert to str..
		def fixatts(t):
			attr[str(t[0])] = unescape(str(t[1]))
		map(fixatts, atts.items())
		obj = apply (klass, (), attr)
		self.stack.append(obj)

	def endElement(self, name):
		"Handle an event for the end of an element."
		obj = self.stack.pop()
		if self.stack:
			self.stack[-1].append(obj)
		else:
			self.msg = obj

	def characters(self, ch, start, length):
		if self.stack:
			text = ch[start:start+length]
			text = text.strip()
			if text:
				self.stack[-1].append(Text(text))
		
	def ignorableWhitespace(self, ch, start, length):
		pass
	def processingInstruction(self, target, data):
		"Handle a processing instruction event."
		print "unhandled processing instruction:", target, data
	def setDocumentLocator(self, locator):
		"Receive an object for locating the origin of SAX document events."
		pass


def _default_parser_callback(obj):
	obj.emit(sys.stdout)

def get_parser(dtdmodules, handlerclass=ObjectParserHandler, callback=_default_parser_callback):
	from xml.sax import saxexts
	handler = handlerclass(callback, dtdmodules)
	parser  = saxexts.make_parser()
	parser.setDocumentHandler(handler)
	return parser

def parseString(string, dtdmodules, handlerclass=ObjectParserHandler, callback=_default_parser_callback):
	parser = get_parser(dtdmodules, handlerclass, callback)
	parser.parseFile(StringIO(string))

def get_dtd_compiler(fo, mixinmodule=None):
	global sourcegen
	import sourcegen
	from xml.parsers.xmlproc.dtdparser import DTDParser
	generator = sourcegen.get_sourcefile(fo)
	dh = DTDConsumerForSourceGeneration(generator, mixinmodule)
	parser = DTDParser()
	parser.set_dtd_consumer(dh)
	return parser


# xml helper classes, used in both generation and operation
# The are instantiated during compilation to generate themselves. 
# Then, when imported by the user from the dtds package, are used normally.
class ContentModel(object):
	"""Represents and validates a content model.  """
	def __init__(self, rawmodel=None):
		self.model = rawmodel # XXX

	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%r)" % (cl.__module__, cl.__name__, self.model)

	def is_empty(self):
		return not self.model


class _ContentModelGenerator(object):
	"""_ContentModelGenerator(rawmodel)
	The DTD parser generated and final content model are so different that a
	different content model generator is used for this object.

	"""
	def __init__(self, rawmodel=None):
		tm_type = type(rawmodel)
		if tm_type is str:
			if rawmodel == "EMPTY":
				self.model = EMPTY
			elif rawmodel == "#PCDATA":
				self.model = PCDATA
			elif rawmodel == "ANY":
				self.model = ANY
			else:
				raise ValidationError, "ContentModelGenerator: unknown special type"
		elif tm_type is tuple:
			self.model = (ANY,) # rawmodel # XXX
		elif tm_type is type(None):
			self.model = None
		else:
			raise RuntimeError, "unknown content model format"

	def __repr__(self):
		return "%s.%s(%r)" % (ContentModel.__module__, ContentModel.__name__, self.model)


class Enumeration(list):
	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%s)" % (cl.__module__, cl.__name__, list.__repr__(self))
	def __str__(self):
		return "(%s)" % ", ".join(map(repr, self))

class AttributeList(list):
	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%s)" % (cl.__module__, cl.__name__, list.__repr__(self))
	def __str__(self):
		return " ".join(map(str, self))

class _AttributeType(str):
	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%s)" % (cl.__module__, cl.__name__, self)

class IDREFS(AttributeList):
	def add_ref(self, value):
		self.data.append(IDREF(value))

class ENTITIES(AttributeList):
	pass
class NMTOKENS(AttributeList):
	pass

class CDATA(_AttributeType):
	pass
class ID(_AttributeType):
	pass
class IDREF(_AttributeType):
	pass
class NMTOKEN(_AttributeType):
	pass
class ENTITY(_AttributeType):
	pass


PCDATA = Text
ANY = True
EMPTY = None

# enumerations
AT_CDATA = 1
AT_ID = 2
AT_IDREF = 3
AT_IDREFS = 4
AT_ENTITY = 5
AT_ENTITIES = 6
AT_NMTOKEN = 7
AT_NMTOKENS = 8

REQUIRED = 11   # attribute is mandatory
IMPLIED = 12    # inherited from environment if not specified
DEFAULT = 13    # default value for enumerated types (added by parser)
FIXED = 14      # always the same, fixed, value.

_ATTRTYPEMAP = {
	"CDATA": AT_CDATA,
	"ID": AT_ID,
	"IDREF": AT_IDREF,
	"IDREFS": AT_IDREFS,
	"ENTITY": AT_ENTITY,
	"ENTITIES": AT_ENTITIES,
	"NMTOKEN": AT_NMTOKEN,
	"NMTOKENS": AT_NMTOKENS
}

_ATTRCLASSMAP = {
	AT_CDATA: CDATA,
	AT_ID: ID,
	AT_IDREF: IDREF,
	AT_IDREFS: IDREFS,
	AT_ENTITY: ENTITY,
	AT_ENTITIES: ENTITIES,
	AT_NMTOKEN: NMTOKEN,
	AT_NMTOKENS: NMTOKENS
}

_DEFAULTMAP = {
	u'#REQUIRED': REQUIRED,
	u'#IMPLIED': IMPLIED,
	u'#DEFAULT': DEFAULT,
	u'#FIXED': FIXED,
}

class XMLAttribute(object):
	def __init__(self, name, a_type, a_decl, a_def=None):
		self.name = str(name)
		a_type_type = type(a_type)
		#a_decl_type = type(a_decl)
		if a_type_type is unicode: # from the parser
			self.a_type = _ATTRTYPEMAP.get(str(a_type), a_type)
#		elif a_type_type is tuple or a_type_type is list:
#			self.a_type = a_type # XXX
		elif a_type_type is int: # from the generated file
			self.a_type = _ATTRCLASSMAP.get(a_type, a_type)
		elif a_type_type is list:
			self.a_type = Enumeration(map(str, a_type))
		else:
			self.a_type = a_type
		# declaration
		# convert string to int value when generating, just use the int when imported from Python dtd format.
		self.a_decl = _DEFAULTMAP.get(a_decl, a_decl)
		self.default = a_def
		# save the type to speed verify
		self.a_type_type = type(self.a_type)

	def __repr__(self):
		cl = self.__class__
		return "%s.%s(%r, %r, %r, %r)" % (cl.__module__, cl.__name__, self.name, self.a_type, self.a_decl, self.default)

	def verify(self, value):
		if issubclass(type(self.a_type), list):
			if value not in self.a_type:
				raise ValidationError, "Enumeration has wrong value. %s is not one of %r." % (value, self.a_type)
		elif self.a_decl == FIXED:
			if value != self.default:
				raise ValidationError, "Bad value for FIXED attributed. %r must be %r." % (value, self.default)
		return True


# this DTD parser consumer generates the Python source code from the DTD. 
class DTDConsumerForSourceGeneration(object):
	def __init__(self, generator, mixins=None):
		self.generator = generator
		self.elements = {}
		self.parameter_entities = {}
		self.general_entities = {}
		self.mixins = mixins # should be a module object

	def dtd_start(self):
		print "Starting to parse DTD...",
		self.generator.add_comment("This file generated by a program. do not edit.")
		self.generator.add_import(sys.modules[__name__])
		if self.mixins:
			self.generator.add_import(self.mixins)

	def dtd_end(self):
		print "done parsing. Writing file."
		self.generator.write()

	def new_element_type(self, elem_name, elem_cont):
		"Receives the declaration of an element type."
		try:
			element = self.elements[elem_name]
		except KeyError:
			parents = [ElementNode]
			mixinname = "%sMixin" % ( elem_name )
			if self.mixins and hasattr(self.mixins, mixinname):
				parents.insert(0, getattr(self.mixins, mixinname))
			# class name is capitalized to avoid clashes with Python key words.
			ch = self.generator.add_class(identifier(elem_name), tuple(parents))
			ch.add_attribute("_name", elem_name)
			ch.add_attribute("CONTENTMODEL", _ContentModelGenerator(elem_cont))
			self.elements[elem_name] = ch
			
	def new_attribute(self, elem, attr, a_type, a_decl, a_def):
		"Receives the declaration of a new attribute."
		try:
			element = self.elements[elem]
		except KeyError:
			raise ValidationError, "attribute defined before element!"
		try:
			attlist = element.get_attribute("ATTLIST")
		except KeyError:
			element.add_attribute("ATTLIST", AttributeList())
			attlist = element.get_attribute("ATTLIST")
		attlist.append(XMLAttribute(attr, a_type, a_decl, a_def))

	def handle_comment(self, contents):
		"Receives the contents of a comment."
		self.generator.add_comment(contents)

	def new_parameter_entity(self,name,val):
		"Receives internal parameter entity declarations."
		# these are handled internally by the DTD parser. but.. save it anyway.
		self.parameter_entities[name] = val
	
	def new_external_pe(self, name, pubid, sysid):
		"Receives external parameter entity declarations."
		# these are handled internally by the DTD parser.
	
	def new_general_entity(self,name,val):
		"Receives internal general entity declarations."
		self.general_entities[name] = val
		# XXX do we need to handle this?
		#print "XXX general entity:"
		#print name, val

	def new_external_entity(self, ent_name, pub_id, sys_id, ndata):
		"""Receives external general entity declarations. 'ndata' is the
		empty string if the entity is parsed."""
		# XXX do we need to handle this?
		print "XXX external entity:"
		print ent_name, pub_id, sys_id, ndata

	def new_notation(self,name,pubid,sysid):
		"Receives notation declarations."
		# XXX do we need to handle this?
		print "XXX unhandled notation:",
		print name, pubid, sysid

	def handle_pi(self, target, data):
		"Receives the target and data of processing instructions."
		# XXX do we need to handle this?
		print "XXX unhandled PI:",
		print target, data

#########################################################
# Utility functions
#########################################################

def get_mod_file(sourcefilename):
	"""get_mod_file(sourcefilename)
	Converts a file name into a file name inside the dtds package. This file
	name is the destination for generated python files.
	"""
	import dtds
	modname = os.path.splitext(os.path.split(sourcefilename)[1])[0]
	return os.path.join(dtds.__path__[0], modname.translate(maketrans("-. ", "___"))+".py")


def _find_element(elname, modules):
	for mod in modules:
		try:
			return getattr(mod, elname)
		except AttributeError:
			continue
	return None

def _construct_node(name, modules):
	if "[" not in name:
		nc = _find_element(name, modules)
		if nc is None:
			raise ValidationError, "no such element name in modules"
		return nc() # node
	else:
		xpath_re = re.compile(r'(\w*)(\[.*])')
		mo = xpath_re.match(name)
		if mo:
			attdict = {}
			ename, attribs = mo.groups()
			nc = _find_element(ename, modules)
			if nc is None:
				raise ValidationError, "no such element name in modules"
			attribs = attribs[1:-1].split("and") # chop brackets and split on 'and'
			attribs = map("".strip, attribs) # strip whitespace
			for att in attribs:                  # dict elememnts are name and vaue
				name, val = att.split("=")
				attdict[name[1:]] = val[1:-1]
		return apply(nc, (), attdict)


def make_node(path, modules, value=None):
	"""make_Node(path, modules, [value])
	Makes a node or an XML fragment given a path, element module list, and an
	optional value.
	"""
	if type(modules) is not list:
		modules = [modules]
	pathelements = path.split("/")
	if not pathelements[0]: # delete possible empty root node
		del pathelements[0]
	rootnode = current = _construct_node(pathelements[0], modules)
	for element in pathelements[1:]:
		new = _construct_node(element, modules)
		current.append(new)
		current = new
	current.set_inline()
	if value is not None:
		current.add_text(value)
	return rootnode
	
def unescape(s):
	if '&' not in s:
		return s
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
#	s = s.replace("&apos;", "'")
	s = s.replace("&quot;", '"')
	s = s.replace("&amp;", "&") # Must be last
	return s

def escape(s):
	s = s.replace("&", "&amp;") # Must be first
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
#	s = s.replace("'", "&apos;")
	s = s.replace('"', "&quot;")
	return s

# self test
if __name__ == "__main__":
	pass
	# note: running this script as __main__ will not generate valid source code. 
	# Use the dtd2py script for that.
	#dtdp = get_dtd_compiler(sys.stdout)
	#dtdp.parse_resource(FILE)
#	outfile.close()
#	print Comment("some ------- comment-")
#	print repr(POMString(u'This is a test.'))
#	print repr(POMString(u'This is a test.', 'utf-8'))
#	print repr(POMString('This is a test.', 'utf-8'))
#	import dtds.xhtml1_strict
#	doc = POMDocument(dtds.xhtml1_strict)
#	doc.set_root(doc.get_elementnode("html")())
#	print doc

