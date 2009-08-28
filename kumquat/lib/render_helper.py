# -*- coding: utf-8 -*-

from rdflib import URIRef
from urllib import quote
import kumquat.lib.schema as schema
from pylons import g

n = g.n

def viewnamelink(name) :
	if name == None :
		name = "None"
	return '<a href="/view/name/%s">%s</a>' % (quote(name), name)

def viewurilink(uri) :
	"""
	given a uri, return a url to view it
	"""
	name = schema.uri_to_name(uri)
	if name :
		url = '/view/name/' + quote(name)
	elif uri[:7] == "http://" :
		url = '/view/uri/' + uri[7:]
	else :
		url = '/view/uri?id=' + uri
	
	return '<a href="%s">%s</a>' % (url, name or n.shorten(uri))

def jsquote(prim) :
	"""
	prepend u, n or s to a string as a way to type the primitive.  Undone in 
	action._parse_prim as the values are sent in as parameters.
	"""
	if isinstance(prim, URIRef) :
		return 'u' + str(prim)
	elif isinstance(prim, float) :
		return 'f' + str(prim)
	elif isinstance(prim, int) :
		return 'i' + str(prim)
	elif isinstance(prim, basestring) :
		return 's' + prim.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
	else :
		return None
