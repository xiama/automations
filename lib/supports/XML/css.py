#! /usr/bin/env  python

"""

css.py
-----------

Provides a CSS class, which reads in a css specification in
file or string form and wraps it in a dictionary-like object.
See the class documentation for more info.

Copyright 2000 by Matthew C. Gushee

The author hereby grants permission to use, redistribute, or
modify this program for any purpose, on condition that the
above copyright notice and this statement be retained without
alteration. This program carries no warranty of any kind.

Please send comments and questions to <mgushee@havenrock.com>.

"""

import string, re, copy, os
from UserDict import UserDict

class CSS(UserDict):
    """

    A dictionary-like wrapper for CSS style specifications.

    
    Usage:

        mycss = CSS('./mystyle.css')
        mycss = CSS(css_data)

    Instances may be created based on CSS files, or on data
    in CSS or Python dictionary form. See __init__ method
    documentation for details.


    Public methods:

    getspec    Return style data for a particular context.

    setspec    Define style data for a particular context.

    merge      Assimilate data from another CSS instance.

    remove     Remove specified data from the current instance.


    Additionally, the CSS class overloads the + and - operators to
    provide a convenient means of adding and subtracting data, e.g.:

        this_style = this_style + that_style

    (that_style may be a CSS class instance or a dictionary in the
    same form as CSS.data) If the two objects have any keys in common,
    the values in the right-hand object take precedence. Thus, the
    above operation may overwrite data in this_style. If you want to
    preserve all existing data while adding new data, simply reverse
    the order:
    
        this_style = that_style + this_style

    The following removes all data contained in that_style from
    this_style:

        this_style = this_style - that_style

    You can even empty all the data by doing this:
    
        this_style = this_style - this_style


    Parsed style data is stored as a dictionary in the form:

        {<selector>: {<prop-name>: <prop-value>, ...}, ...}
    
    <selector> is a string representing a CSS selector (an
    element name, class name, or ID), or a tuple of such strings.
    
    <prop-name> is a string representing a style property name.

    <prop-value> is a string representing a property value, or
    a list of such strings (as in the case of font families:
    ['Helvetica', 'Arial', 'Geneva', 'sans-serif']).

    Note that if a stylesheet contains a group of properties with
    multiple selectors, the CSS instance will have one key for each
    of these selectors. E.g.,

    .MainMenu, .WhatsNew, H5 { spam: eggs }

    ... becomes

    {'.MainMenu': {'spam': 'eggs'}, '.WhatsNew', {'spam': 'eggs'},
    H5 {'spam': 'eggs'}}

    Hierarchical selectors, on the other hand, are parsed into tuples.
    For example:

    .BodyText A { spam: eggs }

    ... becomes

    {('.BodyText', 'A'): {'spam': 'eggs'}}

    In this documentation, I use the term 'context' to refer to a
    single or hierarchical selector *in the form* used by the CSS
    class methods -- a string like 'BODY', or a sequence like
    ('TABLE', 'A'), or ['.Menu', 'UL']. Although the methods are
    currently written to accept context arguments in list form, I
    may at some point decide to restrict them to tuples.
    
    
    The current version of this class will probably fail to parse
    most stylesheets containing syntax errors. It makes no attempt
    to validate the stylesheet, however, so any data following CSS
    syntax will work.

    """

    ## capture a specification group -- e.g., a group of style
    ## properties pertaining to a particular context
    specgroup = re.compile(r"([^{}]+){([^{}]+)}")
    ## weed out supposed property definitions that are empty
    ## or missing the required colon.
    bogus = re.compile(r"^[^:]*$")

    def __init__(self, datasrc, defaultcontext=None):
        """
        Arguments:
        
        datasrc -- The data source for this instance. May be given in
        any of three forms: (1) the name of a CSS file, (2) a string
        containing style data in CSS syntax, or (3) a dictionary in
        the same form as self.data

        defaultcontext -- (OPTIONAL) The default context from which
        others inherit properties. If your stylesheet is for an
        ordinary web page, for example, you might use "BODY" as a
        default context. Must be present in the data source.

        """
        UserDict.__init__(self)
        if type(datasrc) is type({}):
            self.data = datasrc
        else:
            if os.path.isfile(datasrc):
                cssdata = self._readin(datasrc)
            elif type(datasrc) is type(''):
                cssdata = datasrc
            else:
                raise RuntimeError, 'Invalid data type: %s' % type(datasrc)
            self._parse(cssdata)
        self.defaultcontext = defaultcontext

    def __add__(self, other):
        if ((type(other) is type(self) and
            other.__class__ is self.__class__) or
            type(other) is type({})):
            return CSS(self.merge(other))
        elif os.path.isfile(other) or type(other) is type({}):
            temp = CSS(other)
            newcss = CSS(self.merge(temp))
            del(temp)
            return newcss
        else:
            raise RuntimeError, 'Invalid data type: %s' % type(other)

    def __radd__(self, other):
        if os.path.isfile(other) or type(other) is type({}):
            temp = CSS(other)
            newcss = CSS(self.merge(temp, 1))
            del(temp)
            return newcss
        else:
            raise RuntimeError, 'Invalid data type: %s' % type(other)

    def __sub__(self, other):
        if ((type(other) is type(self) and
            other.__class__ is self.__class__) or
            type(other) is type({})):
            return CSS(self.remove(other))
        elif os.path.isfile(other) or type(other) is type({}):
            temp = CSS(other)
            newcss = CSS(self.remove(temp))
            del(temp)
            return newcss
        else:
            raise RuntimeError, 'Invalid data type: %s' % type(other)

    def __rsub__(self, other):
        if os.path.isfile(other) or type(other) is type({}):
            temp = CSS(other)
            newcss = CSS(self.remove(temp, 1))
            del(temp)
            return newcss
        else:
            raise RuntimeError, 'Invalid data type: %s' % type(other)

    def _error(self, strict, errmsg=''):
        if strict:
            raise RuntimeError, errmsg
        else:
            return 0

    def _readin(self, file):
        try:
            f = open(file, 'r')
        except IOError:
            print 'Unable to read file %s' % file
        css = f.read()
        f.close()
        return css

    def _parse(self, cssdata):
        propdict = {}
        while cssdata:
            spec = self.specgroup.match(cssdata)
            if spec is None:
                break
            selectors, stylegroup = spec.groups()
            ## Parse the styles first. That way, if there are
            ## multiple identifiers, we don't have to redo
            ## the styles for each one.
            for style in string.split(stylegroup, ';'):
                if self.bogus.match(style):
                    break
                style = string.split(style, ':')
                prop = string.strip(style[0])
                val = string.split(style[1], ',')
                if len(val) < 2:
                    propdict[prop] = string.strip(val[0])
                else:
                    propdict[prop] = []
                    for item in val:
                        propdict[prop].append(string.strip(item))
            for sel in string.split(selectors, ','):
                sel = string.strip(sel)
                ## Hierarchical selector, e.g. .Body P
                hiersel = string.split(sel)
                if len(hiersel) > 1:
                    sel = tuple(hiersel)
                if not self.has_key(sel):
                    self[sel] = {}
                for prop, val in propdict.items():
                    if not self[sel].has_key(prop):
                        self[sel][prop] = val
            cssdata = cssdata[spec.end():]

    def getspec(self, context=None, strict=0, inherit=1,
                usecurrent=[], set={}):
        """
        Return dictionary of style properties for a given context.

        Arguments (all optional):

        context -- (A dictionary key representing the context where
        this style spec will apply). If omitted, self.defaultcontext
        will be used.

        strict -- (boolean) If true, any properties having values of
        None, and any context names that do not exist in self.data,
        will cause errors. If false, values of None will be returned,
        and non-existent context names will be silently ignored.

        inherit -- (boolean) If true, the returned data will include
        inherited properties. If false, only properties explicitly
        defined for this context will be returned. If true and
        'usecurrent' is empty , all properties applying to this
        context, whether explicitly defined or inherited, will be
        returned.

        usecurrent -- (list of property names) If any names are
        listed, only the listed properties will be returned, using
        inherited values for those not explicitly defined in this
        context.

        set -- (dictionary of property names and values) Sets
        properties to the specified values. This argument overrides
        existing values. If a 'set' argument is supplied, 'inherit'
        is false, and 'usecurrent' is omitted, the method will simply
        return the value of 'set'.

        """
        spec = {}
        base = self.defaultcontext or ''
        if type(context) is type(''):
            context = [context]
        elif type(context) is type(()):
            if self.data.has_key(context):
                context = list(context) + [context]
            else:
                context = list(context)
        if inherit:
            if base and context[0] != base:
                context.insert(0, base)
        else:
            context = context[-1]        
        if usecurrent or not inherit:
            inheritall = 0
        else:
            inheritall = 1
            context = context or base
        if usecurrent:
            ## Work down from current context to default
            context.reverse()
            found = []
            for prop in usecurrent:
                for layer in context:
                    if self.data.has_key(layer):
                        propdict = self.data[layer]
                        if propdict.has_key(prop):
                            spec[prop] = propdict[prop]
                            found.append(prop)
                            break
                    elif strict:
                        raise RuntimeError, "Invalid selector: '%s'." % layer
            for prop in usecurrent:
                if prop not in found:
                    spec[prop] = None
        if inheritall:
            ## Work up from default context
            for layer in context:
                if self.data.has_key(layer):
                    for prop in self.data[layer].keys():
                        spec[prop] = self.data[layer][prop]
                elif strict:
                    raise RuntimeError, "Invalid selector: '%s'." % layer
        if set:
            for prop in set.keys():
                spec[prop] = set[prop]
        if strict:
            for prop in spec.keys():
                if spec[prop] is None:
                    raise RuntimeError, "Property not found: '%s'." % prop
        return spec            
        
    def setspec(self, context=None, strict=0, inherit=1,
                keeponly=[], set={}):
        """
        Define style properties for a particular context.

        [ DON'T USE THIS YET! Something is screwy in the way this
        method calls self.getspec(). To be fixed soon. ]

        Arguments (all optional):

        context -- (A dictionary key representing the context where
        this style spec will apply). The key may, but need not, be
        present in the instance data. If omitted, self.defaultcontext
        will be used.

        strict -- (boolean) See getspec documentation.

        inherit -- (boolean) If true, any existing properties applying
        to the given context, but not specified in 'set', will be
        retained, including inherited properties. If false, the new
        settings will include only the properties explicitly defined
        for the context.

        keeponly -- (list of property names) If empty, all existing
        properties will be retained. If any property names are listed,
        only the properties listed here or in 'set' will be kept; all
        others will be removed.

        set -- (dictionary of property names and values) Sets
        properties to the specified values. This argument overrides
        inherited values.
        
        """
        if context is None:
            try:
                ## MakeError is undefined, so raises exception
                context = self.defaultcontext | MakeError
            except:
                raise RuntimeError, 'No context for style spec.'
        if not self.data.has_key(context):
            self.data[context] = {}
        if keeponly:
            newspec = self.getspec(context, strict,
                                   usecurrent=keeponly, set=set)
        elif inherit:
            newspec = self.getspec(context, strict, set=set)
        elif set:
            newspec = set
        else:
            newspec = self.getspec(context)
        for prop in set.keys():
            self.data[context] = newspec


    def merge(self, cssobj, selfish=0):
        """
        Assimilate data from another CSS instance.

        Arguments:

        cssobj -- a CSS class instance

        selfish -- (optional, boolean) In case of conflicts, this
        argument specifies whether new or existing data takes
        precedence. If false, new data (specified in 'cssobj')
        will take precedence; if true, all existing data will
        be preserved.

        """
        if selfish:
            ## Dunno why I was getting errors with this ...
            ## result = copy.deepcopy(cssobj)
            result = {}
            for k in cssobj.keys():
                result[k] = copy.copy(cssobj[k])
            newdata = self.data
        else:
            ## result = copy.deepcopy(self.data)
            result = {}
            for k in self.data.keys():
                result[k] = copy.copy(self.data[k])            
            newdata = cssobj
        for k in newdata.keys():
            if result.has_key(k):
                for l in newdata[k].keys():
                    result[k][l] = newdata[k][l]
            else:
                result[k] = newdata[k]
        return result

    def remove(self, cssobj, selfish=0):
        """
        Remove specified data from the current instance.

        cssobj -- a CSS class instance

        selfish -- (optional, boolean) If true, the contents
        of self.data will be removed from cssobj.data. If false,
        the contents of cssobj.data will be removed from
        self.data.
        
        """
        if selfish:
            result = copy.deepcopy(cssobj)
            rmdata = self.data
        else:
            result = copy.deepcopy(self.data)
            rmdata = cssobj        
        for k in rmdata.keys():
            if result.has_key(k):
                for m in rmdata[k].keys():
                    if result[k].has_key(m):
                        del result[k][m]
            if not result[k]:
                del result[k]
        return result

            
if __name__ == '__main__':
    import sys, os
    cssfile = raw_input('What file would you like to parse?\n> ')
    cssfile = string.strip(cssfile)
    if string.find(cssfile, '~/') == 0:
        try:
            cssfile = os.path.join(os.environ['HOME'], cssfile[2:])
        except:
            print """This system appears not to support filenames beginning
with '~'. Please try again using the full path.
"""
            sys.exit()
    try:
        mycss = CSS(cssfile)
        print """'%s' successfully parsed. Data is as follows:

%s
        """ % (cssfile, mycss)
    except:
        print """Failed to parse '%s.' Please check for CSS syntax
errors. If your CSS file is correct, please send a
detailed bug report to <mgushee@havenrock.com>, including
a copy of '%s'.
        """
