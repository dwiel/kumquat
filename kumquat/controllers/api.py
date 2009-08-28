# -*- coding: utf-8 -*-
import logging

from rdflib import URIRef

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to

from kumquat.lib.base import BaseController, render
import kumquat.lib.schema as schema

log = logging.getLogger(__name__)

from pylons import g
n = g.n

class ApiController(BaseController):
	
	def types_properties_autocomplete(self) :
		"""
		given a list of types and a optionally substr to search for in properties,
		return possible type names each on their own line.
		TODO: don't show properties which are unique and already have a value.
		"""
		types_str = request.params['types']
		if 'q' in request.params :
			property_substr = request.params['q']
		else :
			property_substr = ''
		
		types = types_str.split(', ')
		
		properties = schema.types_properties(types, ':input_type ?input_type')
		
		def prop_str(prop) :
			if prop['input_type'] == n.bk.suggest :
				input_type = 'suggest'
			elif prop['input_type'] == n.bk.plain :
				input_type = 'plain'
			elif prop['input_type'] == URIRef('http://theburningkumquat.com/item/1240190068661') :
				input_type = 'textarea'
			elif prop['input_type'] == URIRef('http://theburningkumquat.com/item/1240715819851') :
				input_type = 'integer'
			return '%s|%s' % (prop['name'], input_type)
		
		return '\n'.join(set([prop_str(prop) for prop in properties if property_substr in prop['name']]))

	def existing_values_autocomplete(self) :
		property_name = request.params['property_name']
		if 'q' in request.params :
			search_substr = request.params['q']
		else :
			search_substr = ''
		
		def format_str(val) :
			return '%s|%s' % (val['name'], val['uri'])
		
		return '\n'.join([format_str(val) for val in g.sparql.doQueryRows("""
			PREFIX : <http://theburningkumquat.com/schema/>
			SELECT ?uri ?name WHERE {
				?prop :name "%s" ;
				      :property_type ?type .
				?uri :typeof ?type ;
				     :name ?name .
			}""" % property_name) if search_substr in val['name']])


