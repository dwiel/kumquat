# -*- coding: utf-8 -*-
import logging

from rdflib import URIRef
from webhelpers import markdown

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort, redirect_to
from routes import url_for

from urllib import quote

from kumquat.lib.base import BaseController, render, g
import kumquat.lib.schema as schema
import kumquat.lib.render_helper as rh

n = g.n

log = logging.getLogger(__name__)

class ViewController(BaseController):
	def __init__(self) :
		pass
	
	def _renderItem(self, subquery, object) :
		"""
		render a single item, called by both name and id, depending how the item
		is looked up
		"""
		
		if 'name' in object :
			title = object['name']
			name = object['name']
		else :
			title = object.values()[0]
			name = None
		
		# pull all triples with this item as the subject
		query = """
		PREFIX : <http://theburningkumquat.com/schema/>
		SELECT ?sub ?pred ?val WHERE {
		%s .
		?sub ?pred ?val .
		}""" % subquery
		rows = g.sparql.doQueryRows(query)
		
		if len(rows) == 0 :
			c.body = "Can't find " + title
			c.title = "Error:"
			return render('/index.mako')

		# extract a list of the predicated, types and valid properties
		preds = [str(row['pred']) for row in rows]
		types = [str(row['val']) for row in rows if row['pred'] == n.bk['typeof']]
		properties = schema.types_properties(types)
		
		body = ""
		post_body = ""
		if name :
			body += '<a href="/action/delete/%s">delete</a> ' % name
		
		# special case for items which are types
		if str(n.bk['type']) in types :
			if name :
				body += '<a href="/action/new_instance/%s">create new %s</a> ' % (name, name)
				body += '<a href="/view/instances/%s">show all instances</a> ' % name
				post_body = '<div class="module-title">instances of %s:</a></div>' % name
				post_body += render('/instances.mako', type_name = name)
		
		#body += triples
		body += '<div id="subject_name">%s</div>' % title
		body += """<a href="javascript:toggle_uri()">uri</a> """
		body += '<div id="uri">'
		body += rows[0]['sub']
		body += '</div>'
		body += '<br><br>'
		
		for row in rows :
			# if predicate is a description
			if row['pred'] == URIRef('http://theburningkumquat.com/item/1239866285061') :
				md = markdown.Markdown()
				body += '<div id="description">%s</div><a id="description-edit">edit</a><br><br>' % md.convert(row['val'])
				body += '<div id="description_raw" value="%s" />' % row['val']
				row['hidden'] = True
			elif row['pred'] == URIRef('http://theburningkumquat.com/item/1244598466111') :
				# TODO: make this really work.  since different div names from description its not the same
				md = markdown.Markdown()
				body += '<div id="note">%s</div><a id="note-edit">edit</a><br><br>' % md.convert(row['val'])
				body += '<div id="note_raw" value="%s" />' % row['val']
				row['hidden'] = True
			elif row['pred'] == n.bk.name :
				row['hidden'] = True
		
		if name and str(n.bk['property']) in types :
			query = """
				PREFIX : <http://theburningkumquat.com/schema/>
				SELECT ?name WHERE {
					?x ?prop ?y ;
					   :name ?name .
					?prop :name "%s"
				} LIMIT 10""" % name
			instances = g.sparql.doQueryList(query)
			body += '<br><br><div>some objects with this property:<ul>'
			for instance in instances :
				body += '<li>%s' % rh.viewnamelink(instance)
			body += '</ul></div>'
		
		# used to determine which properties are valid
		body += '<div id="types" value="%s" />' % ', '.join(types)
		
		body += """
		<script>
		$(document).ready(function () {
			$('#row_count').hide();
			$('#description').editable(function (value, settings) {
					$.post('/action/update_unique_value', {
						sub : 'u%s',
						pred : 'uhttp://theburningkumquat.com/item/1239866285061',
						obj : 's' + value,
					});
					return value;
				}, { 
					event      : 'edit',
					onblur     : 'ignore',
					type       : 'textarea',
					rows       : 50,
					cols       : 60,
					cancel     : 'Cancel',
					submit     : 'OK',
					indicator  : '<img src="/img/indicator.gif">',
					data       : function (value) { return $('#description_raw').attr('value'); },
			});
			$('#description-edit').bind('click', function() {
				$('#description').trigger('edit');
			});
			
			$('#title').editable(function (value, settings) {
					$.post('/action/update_unique_value', {
						sub : 'u%s',
						pred : 'uhttp://theburningkumquat.com/schema/name',
						obj : 's' + value,
					});
					return value;
				}, {
					event : 'edit',
					onblur : 'submit',
					indicator  : '<img src="/img/indicator.gif">',
			});
			$('#title-edit').bind('click', function() {
				$('#title').trigger('edit');
			});
		});
		</script>
		""" % (rows[0]['sub'], rows[0]['sub'])
		
		# setup the template info
		c.rows = rows
		c.body = body
		c.post_body = post_body
		c.title = title
		c.title_edit = '<a id="title-edit">edit</a>'
		c.jsincludes = ['dbops.js', 'jquery-autocomplete.js', 'jquery.jeditable.mini.js', 'page-view.js', 'sorttable.js']
		c.cssincludes = ['autocomplete.css']
		
		return render('/index.mako')
	
	def name(self, id) :
		"""
		preffered action to view an item.  It isn't the 'fastest' since it requires
		a lookup of the name, but it is much person/search engine friendly
		"""
		subquery = '?sub :name "%s"' % id
		
		return self._renderItem(subquery, {'name' : id})
		
	def uri(self, id) :
		"""
		if an item has no name, it can be reffered to be uri.  The http:// must 
		stripped out due to the way pylons parsing URLs ... They look dirty anyway
		"""
		uri = 'http://' + id
		name = schema.uri_to_name(uri)
		if name :
			redirect_to('/view/name/' + name)
		
		subquery = 'FILTER( regex(str(?sub), "^%s$") )' % uri
		
		if name :
			object = {'name' : name}
		else :
			object = {'id' : uri[7:]}
		
		return self._renderItem(subquery, object)
	
	def instances(self, id) :
		"""
		renders a list of all instances of a given type.  id should be the name of
		the type
		"""
		type = id
		
		## in general, would it help or hurt here to include the extra info that:
		## 	?type :typeof :type ?
		#query = """
		#PREFIX : <http://theburningkumquat.com/schema/>
		#SELECT ?name WHERE {
			#?uri :typeof ?type ;
			     #:name ?name .
			#?type :name "%s" .
		#}""" % type
		#c.body = '<a href="/action/new_instance/%s">new</a><br><br>' % type
		#c.body += '<ul>'
		#for name in sorted(g.sparql.doQueryList(query)) :
			#c.body += '<li>' + rh.viewnamelink(name)
		#c.body += '</ul>'
		
		c.jsincludes = ['sorttable.js', 'instances.js', 'jquery-autocomplete.js']
		c.cssincludes = ['autocomplete.css']
		
		c.body = render('/instances.mako', type_name = id)
		c.title = 'All %ss' % type
		c.title_header = 'All <a href="/view/name/%s">%s</a>s' % (type, type)
		return render('/index.mako')




