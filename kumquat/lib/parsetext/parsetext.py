#!/usr/bin/env python

from pylons import g
import re
from cgi import escape
import kumquat.lib.refn as refn

def parsetext(text):
	# Escape <,>,& from text for HTML
	pre = re.compile(r'<code>(.*?)</code>', re.M | re.S)
	text = pre.split(text)
	for i in range(len(text)):
		text[i] = escape(text[i])
		if i%2==0 :
			for regex, replace in g.regexes:
				text[i] = refn.sub(regex, replace, text[i])
		else :
			text[i] = '<pre>'+text[i]+'</pre>'
	return ''.join(text)
	