#!/usr/bin/python
# -*- coding: ascii -*-
# vim:ts=4:sw=4:softtabstop=0:smarttab
# 
#	 Copyright (C) 1999-2004  Keith Dart <kdart@kdart.com>
#
#	 This library is free software; you can redistribute it and/or
#	 modify it under the terms of the GNU Lesser General Public
#	 License as published by the Free Software Foundation; either
#	 version 2.1 of the License, or (at your option) any later version.
#
#	 This library is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#	 Lesser General Public License for more details.

"""
Helpers and tools for dictionary objects.

"""

class AttrDictWrapper(object):
	"""Wraps any mapping object with the ability to get to its contents using
	attribute access syntax (dot). Note that you cannot have any contained keys
	that match an attribute name."""
	def __init__(self, mapping=None):
		self.__dict__["_mapping"] = mapping or {}

	# attribute-style access 
	def __getattribute__(self, key):
		try:
			return super(AttrDictWrapper, self).__getattribute__(key)
		except AttributeError:
			try:
				return self.__dict__["_mapping"].__getattribute__( key)
			except AttributeError:
				try:
					obj = self.__dict__["_mapping"].__getitem__(key)
					if hasattr(obj, "keys"):
						return self.__class__(obj) # wrap the returned mapping object also
					else:
						return obj
				except KeyError, err:
					raise AttributeError, "no attribute or key '%s' found (%s)." % (key, err)

	def __setattr__(self, key, obj):
		if self.__class__.__dict__.has_key(key): # property access
			object.__setattr__(self, key, obj)
		else:
			return self.__dict__["_mapping"].__setitem__(key, obj)

	def __delattr__(self, key):
		try: # to force handling of properties
			self.__dict__["_mapping"].__delitem__(key)
		except KeyError:
			object.__delattr__(self, key)

	def __getitem__(self, key):
		obj = self._mapping[key]
		if hasattr(obj, "keys"):
			return self.__class__(obj) # wrap the returned mapping object also
		else:
			return obj

	def __delitem__(self, key):
		del self._mapping[key]

	def __setitem__(self, key, obj):
		self._mapping[key] = obj

	
class AttrDict(dict):
	"""A dictionary with attribute-style access. It maps attribute access to
	the real dictionary.  """
	def __init__(self, init={}):
		dict.__init__(self, init)

	def __getstate__(self):
		return self.__dict__.items()

	def __setstate__(self, items):
		for key, val in items:
			self.__dict__[key] = val

	def __repr__(self):
		return "%s(%s)" % (self.__class__.__name__, dict.__repr__(self))

	def __setitem__(self, key, value):
		return super(AttrDict, self).__setitem__(key, value)

	def __getitem__(self, name):
		return super(AttrDict, self).__getitem__(name)

	def __delitem__(self, name):
		return super(AttrDict, self).__delitem__(name)

	__getattr__ = __getitem__
	__setattr__ = __setitem__

	def copy(self):
		ch = AttrDict(self)
		return ch


def _test(argv):
	ld = {"one":1, "two":2, "three":3}
	gd = {"gbone":1, "gbtwo":2, "gbthree":3}
	lw = AttrDictWrapper(ld)
	lw.four = gd
	print lw.one
	print lw.two
	print lw.four.gbone
	print lw.four["gbtwo"]

	d = AttrDict()
	d.one = "one"
	print d
	print d.get
	print d.one
	print d["one"]
	d["two"] = 2
	print d.two
	print d["two"]



if __name__ == "__main__":
	import sys
	_test(sys.argv)

