#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4
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
MODULE_DESCRIPTION

"""

import sys

def _test(argv):
	pass # XXX


# lexer
"""

unicode		\\[0-9a-f]{1,4}
latin1		[¡-ÿ]
escape		{unicode}|\\[ -~¡-ÿ]
stringchar	{escape}|{latin1}|[ !#$%&(-~]
nmstrt		[a-z]|{latin1}|{escape}
nmchar		[-a-z0-9]|{latin1}|{escape}
ident		{nmstrt}{nmchar}*
name		{nmchar}+
d		[0-9]
notnm		[^-a-z0-9\\]|{latin1}
w		[ \t\n]*
num		{d}+|{d}*\.{d}+
string		\"({stringchar}|\')*\"|\'({stringchar}|\")*\'

%x COMMENT
%s AFTER_IDENT

%%
"/*"				{BEGIN(COMMENT);}
<COMMENT>"*/"			{BEGIN(0);}
<COMMENT>\n			{/* ignore */}
<COMMENT>.			{/* ignore */}
@import				{BEGIN(0); return IMPORT_SYM;}
"!"{w}important			{BEGIN(0); return IMPORTANT_SYM;}
{ident}				{BEGIN(AFTER_IDENT); return IDENT;}
{string}			{BEGIN(0); return STRING;}

{num}				{BEGIN(0); return NUMBER;}
{num}"%"			{BEGIN(0); return PERCENTAGE;}
{num}pt/{notnm}			{BEGIN(0); return LENGTH;}
{num}mm/{notnm}			{BEGIN(0); return LENGTH;}
{num}cm/{notnm}			{BEGIN(0); return LENGTH;}
{num}pc/{notnm}			{BEGIN(0); return LENGTH;}
{num}in/{notnm}			{BEGIN(0); return LENGTH;}
{num}px/{notnm}			{BEGIN(0); return LENGTH;}
{num}em/{notnm}			{BEGIN(0); return EMS;}
{num}ex/{notnm}			{BEGIN(0); return EXS;}

<AFTER_IDENT>":"link		{return LINK_PSCLASS_AFTER_IDENT;}
<AFTER_IDENT>":"visited	{return VISITED_PSCLASS_AFTER_IDENT;}
<AFTER_IDENT>":"active	{return ACTIVE_PSCLASS_AFTER_IDENT;}
<AFTER_IDENT>":"first-line	{return FIRST_LINE_AFTER_IDENT;}
<AFTER_IDENT>":"first-letter	{return FIRST_LETTER_AFTER_IDENT;}
<AFTER_IDENT>"#"{name}		{return HASH_AFTER_IDENT;}
<AFTER_IDENT>"."{name}		{return CLASS_AFTER_IDENT;}

":"link				{BEGIN(AFTER_IDENT); return LINK_PSCLASS;}
":"visited			{BEGIN(AFTER_IDENT); return VISITED_PSCLASS;}
":"active			{BEGIN(AFTER_IDENT); return ACTIVE_PSCLASS;}
":"first-line			{BEGIN(AFTER_IDENT); return FIRST_LINE;}
":"first-letter			{BEGIN(AFTER_IDENT); return FIRST_LETTER;}
"#"{name}			{BEGIN(AFTER_IDENT); return HASH;}
"."{name}			{BEGIN(AFTER_IDENT); return CLASS;}

url\({w}{string}{w}\)					|
url\({w}([^ \n\'\")]|\\\ |\\\'|\\\"|\\\))+{w}\)		{BEGIN(0); return URL;}
rgb\({w}{num}%?{w}\,{w}{num}%?{w}\,{w}{num}%?{w}\)	{BEGIN(0); return RGB;}

[-/+{};,#:]			{BEGIN(0); return *yytext;}
[ \t]+				{BEGIN(0); /* ignore whitespace */}
\n				{BEGIN(0); /* ignore whitespace */}
\<\!\-\-			{BEGIN(0); return CDO;}
\-\-\>				{BEGIN(0); return CDC;}
.				{fprintf(stderr, "%d: Illegal character (%d)\n",
				 lineno, *yytext);}

"""


# yacc
"""
stylesheet
 : [CDO|CDC]* [ import [CDO|CDC]* ]* [ ruleset [CDO|CDC]* ]*
 ;
import
 : IMPORT_SYM [STRING|URL] ';'		/* E.g., @import url(fun.css); */
 ;
unary_operator
 : '-' | '+'
 ;
operator
 : '/' | ',' | /* empty */
 ;
property
 : IDENT
 ;
ruleset
 : selector [ ',' selector ]*
   '{' declaration [ ';' declaration ]* '}'
 ;
selector
 : simple_selector+ [ pseudo_element | solitary_pseudo_element ]?
 | solitary_pseudo_element
 ;
	/* An "id" is an ID that is attached to an element type
	** on its left, as in: P#p007
	** A "solitary_id" is an ID that is not so attached,
	** as in: #p007
	** Analogously for classes and pseudo-classes.
	*/
simple_selector
 : element_name id? class? pseudo_class?	/* eg: H1.subject */
 | solitary_id class? pseudo_class?		/* eg: #xyz33 */
 | solitary_class pseudo_class?			/* eg: .author */
 | solitary_pseudo_class			/* eg: :link */
 ;
element_name
 : IDENT
 ;
pseudo_class					/* as in:  A:link */
 : LINK_PSCLASS_AFTER_IDENT
 | VISITED_PSCLASS_AFTER_IDENT
 | ACTIVE_PSCLASS_AFTER_IDENT
 ;
solitary_pseudo_class				/* as in:  :link */
 : LINK_PSCLASS
 | VISITED_PSCLASS
 | ACTIVE_PSCLASS
 ;
class						/* as in:  P.note */
 : CLASS_AFTER_IDENT
 ;
solitary_class					/* as in:  .note */
 : CLASS
 ;
pseudo_element					/* as in:  P:first-line */
 : FIRST_LETTER_AFTER_IDENT
 | FIRST_LINE_AFTER_IDENT
 ;
solitary_pseudo_element				/* as in:  :first-line */
 : FIRST_LETTER
 | FIRST_LINE
 ;
	/* There is a constraint on the id and solitary_id that the
	** part after the "#" must be a valid HTML ID value;
	** e.g., "#x77" is OK, but "#77" is not.
	*/
id
 : HASH_AFTER_IDENT
 ;
solitary_id
 : HASH
 ;
declaration
 : property ':' expr prio? 
 | /* empty */				/* Prevents syntax errors... */
 ;
prio
 : IMPORTANT_SYM	 		/* !important */
 ;
expr
 : term [ operator term ]*
 ;
term
 : unary_operator?
   [ NUMBER | STRING | PERCENTAGE | LENGTH | EMS | EXS
   | IDENT | hexcolor | URL | RGB ]
 ;
	/* There is a constraint on the color that it must
	** have either 3 or 6 hex-digits (i.e., [0-9a-fA-F])
	** after the "#"; e.g., "#000" is OK, but "#abcd" is not.
	*/
hexcolor
 : HASH | HASH_AFTER_IDENT
 ;




"""


if __name__ == "__main__":
	_test(sys.argv)

