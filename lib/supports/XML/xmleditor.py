#!/usr/bin/env python
"""
The xmleditor module defines a GUI tool to edit an XML tree. Changes are
automatically saved. 

xmledit = XMLEditor(xmlfile)
mainloop()

"""

# modified from the pygtk ide/browse module.

import os
from gtk import *

import xmltools

class BrowseTreeItem(GtkTreeItem):
	def __init__(self, name, dict=None, disp=None):
		GtkTreeItem.__init__(self, name)
		self.name = name
		self.dict = dict
		self.disp = disp
		self.exp_id = self.connect("expand", self.sig_expand)
	def init_subtree(self):
		if type(self.dict) is type(self.__dict__):
			self.subtree = GtkTree()
			self.subtree.set_selection_mode(SELECTION_BROWSE)
			self.subtree.connect("select_child", self.subsel_child)
			self.set_subtree(self.subtree)
			self.subtree.show()
	def subsel_child(self, _t, _c):
		if self.disp: 
			key = _c.children()[0].get()
			value = self.dict[key]
			if type(value) is not type(self.__dict__):
				print xmltools.node2path(value)
				if value.childNodes: # has a value 
					self.disp.set_text(str(value.childNodes[0].nodeValue))
				else:
					self.disp.set_text("")
				# stash the node in the Entry in case it is edited
				self.disp.set_data("node", value)
			else:
				self.disp.set_text("")
				self.disp.set_data("node", None)
	def sig_expand(self, _t):
		keys = self.dict.keys()
		keys.sort()
		for key in keys:
			dict = None
			try:
				dict = self.dict[key]
			except TypeError:
				pass
			item = BrowseTreeItem(key, dict, self.disp)
			self.subtree.append(item)
			item.init_subtree()
			item.show()
		self.disconnect(self.exp_id)

class BrowseVariables(GtkVBox):
	def sig_entry_activate(self, disp): # change value
		node = disp.get_data("node")
		if node:
			if node.childNodes: 
				textnode = node.childNodes[0] # minidom has a strange API...
				textnode.deleteData(0, textnode.length)
				textnode.appendData(disp.get_text())
			else: # no existing value node, so add one
				node.appendChild(xmltools.minidom.Text(disp.get_text()))
			self.dom.set_dirty()
	def __init__(self, dom):
		GtkVBox.__init__(self)
		self.set_spacing(2)
		self.dom = dom

		self.sw = GtkScrolledWindow()
		self.sw.set_usize(300, 200)
		self.sw.set_policy(POLICY_AUTOMATIC, POLICY_AUTOMATIC)
		self.pack_start(self.sw)
		self.sw.show()

		self.disp = GtkEntry()
		self.disp.set_editable(TRUE)
		self.disp.connect("activate", self.sig_entry_activate)
		self.pack_start(self.disp, expand=FALSE)
		self.disp.show()

		self.root_tree = GtkTree()
		self.sw.add_with_viewport(self.root_tree)
		self.root_tree.show()

		self.browse = BrowseTreeItem(os.path.basename(dom.filename), dom.get_xml_dict(), self.disp)
		self.root_tree.append(self.browse)
		self.browse.init_subtree()
		self.browse.show()


class BrowseWindow(GtkWindow):
	def __init__(self, dom):
		GtkWindow.__init__(self)
		self.set_title("Browse Window")

		box = GtkVBox()
		self.add(box)
		box.show()

		browse = BrowseVariables(dom)
		browse.set_border_width(10)
		box.pack_start(browse)
		browse.show()
		
		separator = GtkHSeparator()
		box.pack_start(separator, expand=FALSE)
		separator.show()

		box2 = GtkVBox(spacing=10)
		box2.set_border_width(10)
		box.pack_start(box2, expand=FALSE)
		box2.show()

		button = GtkButton("Close/Save")
		box2.pack_start(button)
		button.set_flags(CAN_DEFAULT)
		button.grab_default()
		button.show()
		self.close_button = button


class XMLEditor(object):
	def _cleanup(self, button):
		if self.doc.dirty:
			self.doc.write()
		mainquit()
	def __init__(self, xmlfile):
		self.doc = xmltools.XMLDocument(xmlfile)
		self.win = BrowseWindow(self.doc)
		self.win.set_title(os.path.basename(xmlfile).title())
		self.win.connect("destroy", mainquit)
		self.win.connect("delete_event", mainquit)
		self.win.close_button.connect("clicked", self._cleanup)
		self.win.show()
	
	def run(self):
		mainloop()

def run_editor(filename):
	xmledit = XMLEditor(filename)
	xmledit.run()


if __name__ == '__main__':
	import sys
	run_editor(sys.argv[1])

