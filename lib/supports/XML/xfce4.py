#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# 
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
Tools for working with the xfce4 environment.


"""

import dtds.xfdesktop_menu

import POM

class XFCE4Menu(POM.POMDocument):
	DOCTYPE = "<!DOCTYPE xfdesktop-menu>\n"

	def emit(self, fo):
		pp = POM.BeautifulWriter(fo)
		super(XFCE4Menu, self).emit(pp)

	def add_submenu(self, **attribs):
		return self.root.add_submenu(**attribs)

	def add_title(self, **attribs):
		self.root.add_title(**attribs)

	def add_app(self, **attribs):
		self.root.add_app(**attribs)

	def add_separator(self):
		self.root.add_separator()

	def add_include(self, **attribs):
		self.root.add_include(**attribs)

	
class MenuMixin(object):
	def add_title(self, **attribs):
		title = dtds.xfdesktop_menu.Title(**attribs)
		self.append(title)
	
	def add_app(self, **attribs):
		app = dtds.xfdesktop_menu.App(**attribs)
		self.append(app)

	def add_separator(self):
		self.append(dtds.xfdesktop_menu.Separator())
	
	def add_include(self, **attribs):
		pass

	def add_submenu(self, **attribs):
		Menu = newclass("Menu", MenuMixin, dtds.xfdesktop_menu.Menu)
		menu = Menu(**attribs)
		self.append(menu)
		return menu
	


# factory for menu files
def new_menu():
	doc = XFCE4Menu(dtds.xfdesktop_menu)
	RootMenu = newclass("RootMenu", MenuMixin, dtds.xfdesktop_menu.Xfdesktop_menu)
	root = RootMenu()
	doc.set_root(root)
	return doc

def open_menu(filename):
	fo = file(filename)
	doc = XFCE4Menu(dtds.xfdesktop_menu)
	doc.parseFile(fo)
	fo.close()
	return doc


