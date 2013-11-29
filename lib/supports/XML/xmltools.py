#!/usr/bin/python -i

"""
Some convenience classes and functions for dealing with XML files.

"""

import sys
from xml.dom import minidom

class XMLDocument(object):
	"""
XMLDocument(docname)
A wrapper class for the xml.minidom.Document. This delegates to that
class, and also adds functionality more convenient for automation
purposes.
	"""
	def __init__(self, filename=None):
		if filename is not None:
			self.get_document(filename)
		else:
			self.document = None
			self.filename = None
		self.dirty = 0
		self.xmldict = None # cache the xml dictionary if we use it once
	
	def set_dirty(self, val=1):
		self.dirty = val

	def get_document(self, filename):
		self.document = minidom.parse(filename)
		self.filename = filename
		self.dirty = 0
		return self.document

	def write_xmlfile(self, filename=None):
		if filename is None:
			filename = self.filename
		fo = open(filename, "w")
		self.document.writexml(fo)
		fo.close()
		self.dirty = 0

#	def __del__(self):
#		if self.filename and self.dirty:
#			self.write_xmlfile()

	read = get_document
	write = write_xmlfile

	def writexml(self, writer):
		self.document.writexml(writer)

	# dictionaries have a more convenient access to nodes. 
	def get_xml_dict(self):
		if self.xmldict:
			return self.xmldict
		# else
		xmldict = {}
		_get_dict_helper(self.document.childNodes[0], 
				node2string(self.document.childNodes[0]), xmldict)
		self.xmldict = xmldict
		return xmldict

	def get_path(self, node, choplevel=0):
		return node2path(node, choplevel)

	def get_node(self, path):
		"""
get_node(path)
Find a particular node, given a pathname. 

		"""
		xmldict = self.get_xml_dict()
		nodelist = path.split("/")
		if not nodelist[0]: # remove leading empty string, if present
			del nodelist[0]
		for nodename in nodelist[:-1]:
			dictval = xmldict.get(nodename, None)
			if dictval is None:
				raise ValueError, "XMLDocument.get_node: element not found: %s" % nodename
			if type(dictval) is type(self.__dict__): # check for nested DictType
				xmldict = dictval
			else:
				raise ValueError, "XMLDocument.get_node: Non-terminal node"
		try:
			return xmldict[nodelist[-1]]
		except KeyError:
			raise ValueError, "XMLDocument.get_node: element not found: %s" % (nodelist[-1])

		
	def set(self, path, value):
		node= self.get_node(path)
		if hasattr(node, "childNodes"):
			if node.childNodes: 
				textnode = node.childNodes[0] # minidom has a strange API...
				textnode.deleteData(0, textnode.length)
				textnode.appendData(str(value))
			else: # no existing value node, so add one
				node.appendChild(minidom.Text(str(value)))
			self.dirty = 1
		else:
			raise ValueError, "XMLDocument.set: invalid path"
	
	def dump_paths(self, fo):
		def cb(node):
			fo.write("%s = %s\n" % (node2path(node), node2string(node)))
		node_walker(self.document, cb)
		# XXX this needs work


#########################################################
# Utility functions
#########################################################

def node2string(node):
	if node.nodeType == minidom.Node.ELEMENT_NODE:
		if node.hasAttributes():
			s = map(lambda i: "@%s='%s'" % (i[0],i[1]), node._get_attributes().items())
			return "%s[%s]" % (node.tagName, " and ".join(s))
		else:
			return node.tagName
	elif node.nodeType == minidom.Node.TEXT_NODE:
		return str(node.data)
	elif node.nodeType == minidom.Node.DOCUMENT_NODE:
		return "" # the document is the root
	else:
		return str(node)


def node_walker(startnode, callback, stoptype=minidom.Node.TEXT_NODE):
	for node in startnode.childNodes:
		if node.nodeType == stoptype:
			callback(node)
		elif node.nodeType == minidom.Node.ELEMENT_NODE:
			node_walker(node, callback, stoptype)


def node2path(node, choplevel=0):
	s = [node2string(node)]
	while node.parentNode:
		node = node.parentNode
		s.insert(0, node2string(node))
	return "/".join(s[choplevel:])
	

### internal helper functions

def _find_node_helper(node, name):
	ellist = node.getElementsByTagName(name)
	return ellist

def _getElementsByTagNameHelper(parent, name, rc):
	for node in parent.childNodes:
		if node.nodeType == Node.ELEMENT_NODE and \
			(name == "*" or node.tagName == name):
			rc.append(node)
		_getElementsByTagNameHelper(node, name, rc)
	return rc

# recursive function to help build nested dictionaries
def _get_dict_helper(parent, name, dict):
	newdict = {}
	for node in parent.childNodes:
		if node.nodeType == minidom.Node.ELEMENT_NODE:
			nodename = node2string(node)
			newdict[nodename] = node
			_get_dict_helper(node, nodename, newdict)
	if newdict:
		dict[name] = newdict
	return dict



# self test
if __name__ == "__main__":
	import sys
	argc = len(sys.argv)
	if argc < 2:
		print """xmltools <xmlfile> [<pathname>] [<newvalue>]
		if <xmlfile> given, print path names for file.
		if <pathname> also given, print value of that node.
		if <newvalue> also given, write new file with node changed to that value.
		"""
		sys.exit(1)
	doc = XMLDocument(sys.argv[1])
	if argc == 2:
		doc.dump_paths(sys.stdout)
	elif argc == 3:
		node = doc.get_node(sys.argv[2])
		print node
	elif argc >= 4:
		doc.set(sys.argv[2], sys.argv[3])
		doc.write_xmlfile()



