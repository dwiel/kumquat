<%!
	import kumquat.lib.render_helper as rh
	import kumquat.lib.schema as schema
	from kumquat.lib.base import g
%>

<%
	type_uri = schema.name_to_uri(type_name)
	properties = schema.types_properties(type_uri)
	
	if type_name != 'type' :
		hidden_properties = ['typeof', 'name', 'has property', 'optionally_has_property']
	else :
		hidden_properties = ['name']
	
	properties = [p for p in properties if p['name'] not in hidden_properties]
	
	property_selects = ' '.join(['?' + p['name'].replace(' ', '_') for p in properties])
	property_clauses = ''.join(['OPTIONAL { ?uri <%s> ?%s . } ' % (p['prop'], p['name'].replace(' ', '_')) for p in properties])
	
	# in general, would it help or hurt here to include the extra info that:
	# 	?type :typeof :type ?
	query = """
	PREFIX : <http://theburningkumquat.com/schema/>
	SELECT ?name %s WHERE {
		?uri :typeof ?type ;
				 :name ?name .
		%s
		?type :name "%s" .
	}""" % (property_selects, property_clauses, type_name)
	
	property_names = ['name'] + [p['name'] for p in properties]
%>

<div id="types" value="${type_uri}"></div>

<br>
<a href="/action/new_instance/${type_name}">new</a><br><br>
<a href="javascript:add_column()">add column</a>
<table class="sortable" id="instances">
	<tr>
		<th>
		${'</th><th>'.join(property_names)}
		</th>
	</tr>
% for i, obj in enumerate(sorted(g.sparql.doQueryRows(query))) :
	<tr id="row${i}">
	% for k in property_names :
		<td>
		% if k in obj :
			<% v = obj[k] %>
			%	if k == 'name' :
				%	if v != None :
					${rh.viewnamelink(v)}
				% endif
			%	elif type(v) == rh.URIRef :
					${rh.viewnamelink(schema.uri_to_name(v))}
			% else :
					${v}
			% endif
		% endif
		</td>
	% endfor
	</tr>
% endfor
</table>
