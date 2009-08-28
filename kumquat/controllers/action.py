# -*- coding: utf-8 -*-
import logging

from SimpleSPARQL import *
from rdflib import Namespace, URIRef
import re

from urllib import quote

from pylons import request, response, session, g, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from routes import url_for

from kumquat.lib.base import BaseController, render

import kumquat.lib.schema as schema

log = logging.getLogger(__name__)

n = g.n

re_uri = re.compile('[^\w\d:/\.]')

class ActionController(BaseController):
	def __init__(self) :
		# used to generate unique URIs/IDs for new objects
		self.urigen = Utils.UniqueURIGenerator(Namespace('http://theburningkumquat.com/item/'), '')

	def new_instance(self, id) :
		"""
		given the name of a type, show a form to allow an instance of that type to
		be created
		"""
		print '------------------------'
		print 'begin /view/new_instance'
		type_name = id
		type_uri = schema.name_to_uri(id)
		
		c.body = '<form action="/action/new_instance_submit">'
		c.body += '<input type="hidden" name="type_uri" value="%s" />' % type_uri
		c.body += '<table>'
		c.body += '<tr><th>property</th><th>value</th></tr>'
		for property in schema.types_properties(type_uri, ":property_type ?type", optional = False) :
			c.body += '<tr><td>'
			if property['type'] == n.bk.string :
				c.body += '%s (string)</td><td><input type="text" name="%s" />' % (property['name'], property['prop'])
			elif property['type'] == n.bk.integer :
				# TODO: restrict this to integers
				c.body += '%s (integer)</td><td><input type="text" name="%s" />' % (property['name'], property['prop'])
			elif property['type'] == URIRef('http://theburningkumquat.com/item/1239775078491') :
				c.body += '%s (text)</td><td><textarea name="%s"></textarea>' % (property['name'], property['prop'])
			elif property['name'] == 'typeof' :
				pass
			#elif property['type'] == n.bk['type'] :
				## don't display this one because, it is most likely not necessary.  Will
				## be necessary when mulitple values can be added of the same type.  This
				## makes for a more complex GUI though.
				#pass
			elif schema.is_type_of(property['type'], n.bk['type']) :
				instances = schema.instances_of(property['type'], ':name ?name')
				c.body += '%s</td><td><select name="%s">' % (property['name'], property['prop'])
				# TODO: change this to an autocomplete rather than a dropdown
				for instance in instances :
					c.body += '<option value="%s">%s' % (instance['uri'], instance['name'])
				c.body += '</select>'
			else :
				c.body += '%s (unkown property_type: %s)</td><td><input type="text" name="%s" />' % (property['name'], property['type'], property['prop'])
			c.body += '</tr>'
		c.body += '</table>'
		c.body += '<input type="submit" /><br>'
		c.body += '</form>'
		
		c.title = 'Create a new <a href="/view/name/%s">%s</a>' % (type_name, type_name)
		return render('/index.mako')

	def new_instance_submit(self, id) :
		"""
		action used by new_instance to actually create a new instance of some object
		"""
		type_uri = request.params['type_uri']
		
		query = 'INSERT {\n'
		qexists = 'SELECT ?foo WHERE {\n'
		newuri = self.urigen()
		for property in schema.types_properties(type_uri, ':property_type ?type', optional = False) :
			#print 'property',property
			if property['type'] == n.bk.string :
				query += '<%s> <%s> "%s" . \n' % (newuri, property['prop'], request.params[str(property['prop'])])
				qexists += '?foo <%s> "%s" . \n' % (property['prop'], request.params[str(property['prop'])])
			elif property['prop'] == n.bk.typeof :
				query += '<%s> <%s> <%s> . \n' % (newuri, n.bk.typeof, type_uri)
				qexists += '?foo <%s> <%s> . \n' % (n.bk.typeof, type_uri)
			elif schema.is_type_of(property['type'], n.bk['type']) :
				query += '<%s> <%s> <%s> . \n' % (newuri, property['prop'], request.params[str(property['prop'])])
				qexists += '?foo <%s> <%s> . \n' % (n.bk.typeof, type_uri)
		qexists += '} LIMIT 1'
		query += '}'
		
		existing_uri = g.sparql.doQueryString(qexists)
		
		print 'finished asking ...'
		
		if existing_uri :
			#print 'redirect_to:',str('/view/uri/' + quote(existing_uri[7:]))
			redirect_to(str('/view/uri/' + quote(existing_uri[7:])))
		else :
			print 'query:',query
			g.sparql.doQuery(query, include_prefix = False)
			print 'redirect_to:',str('/view/uri/' + quote(newuri[7:]))
			redirect_to(str('/view/uri/' + quote(newuri[7:])))

	def _sanitize_prim(self, prim) :
		if isinstance(prim, int) or isinstance(prim, float) :
			return str(prim)
		elif isinstance(prim, basestring) :
			return repr(prim)
		elif isinstance(prim, URIRef) :
			return prim.n3()
		else :
			return None
	
	def _parse_prim_escape(self, prim) :
		if prim[0] == 's' :
			print 'prim', prim, repr(str(prim[1:]))
			return repr(str(prim[1:]).replace('\\','\\\\'))
		else :
			return self._parse_prim(prim)
	
	def _parse_prim(self, prim) :
		if prim[0] == 's' :
			# need the [1:] at the end to get rid of the leading u added by repr
			return repr(unicode(prim[1:]))[1:]
		elif prim[0] == 'n' :
			return str(float(prim[1:]))
		elif prim[0] == 'i' :
			return str(int(prim[1:]))
		elif prim[0] == 'u' :
			return '<%s>' % re_uri.sub('', prim[1:])
		elif prim[0] == 'a' :
			name = schema.name_to_uri(prim[1:])
			if name :
				return '<%s>' % name
			else :
				return None
		else :
			return None

	def delete_triple(self) :
		"""
		this should probably be POSTed to to avoid complications with sending URIs 
		over the URL.
		
		incoming strings will be escaped 
		"""
		
		sub = request.params['sub']
		pred = request.params['pred']
		obj = request.params['obj']
		
		sub = self._parse_prim_escape(sub)
		pred = self._parse_prim_escape(pred)
		obj = self._parse_prim_escape(obj)
		
		if sub != None and pred != None and obj != None :
			ret = g.sparql.doQuery("DELETE { %s %s %s }" % (sub, pred, obj))
			print "DELETE { %s %s %s }" % (sub, pred, obj)
			return "DELETE { %s %s %s }:\n%s" % (sub, pred, obj, ret)
	
	def delete(self, id) :
		"""
		for now, just deletes all triples with this object as the subject.  This 
		will most likely need to evolve as more complex properties arrive
		"""
		print 'id',id
		
		name = id
		
		query = """
			PREFIX : <http://theburningkumquat.com/schema/>
			DELETE {
				?sub ?pred ?obj .
			} WHERE {
				?sub ?pred ?obj ;
				     :name "%s" .
			}""" % name
		print 'query:',query
		g.sparql.doQuery(query)
		redirect_to('/view/instances/type')
	
	def insert_triple(self) :
		sub = request.params['sub']
		pred = request.params['pred']
		obj = request.params['obj']
		
		triple_str = sub + ', ' + pred + ', ' + obj
		
		sub = self._parse_prim(sub)
		pred = self._parse_prim(pred)
		obj = self._parse_prim(obj)
		
		if sub == None :
			return 'missing subject: ' + triple_str
		
		if pred == None :
			return 'missing predicate: ' + triple_str
		
		if obj == None :
			return 'missinge object: ' + triple_str
		
		print "insert_triple", "INSERT { %s %s %s }" % (sub, pred, obj)
		g.sparql.doQuery("INSERT { %s %s %s }" % (sub, pred, obj), include_prefix = False)
		#return "INSERT { %s %s %s }:\n%s" % (sub, pred, obj, ret)
	
	def update_unique_value(self) :
		sub = request.params['sub']
		pred = request.params['pred']
		obj = request.params['obj']
		
		triple_str = sub + ', ' + pred + ', ' + obj
		
		sub = self._parse_prim(sub)
		pred = self._parse_prim(pred)
		obj = self._parse_prim(obj)
		
		if sub == None :
			return 'missing subject: ' + triple_str
		
		if pred == None :
			return 'missing predicate: ' + triple_str
		
		if obj == None :
			return 'missinge object: ' + triple_str
		
		g.sparql.doQuery("DELETE { %s %s ?x } WHERE { %s %s ?x }" % (sub, pred, sub, pred), include_prefix = False)
		g.sparql.doQuery("INSERT { %s %s %s }" % (sub, pred, obj), include_prefix = False)
		#return "INSERT { %s %s %s }:\n%s" % (sub, pred, obj, ret)
		
		
	