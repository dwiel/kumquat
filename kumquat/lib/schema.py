# -*- coding: utf-8 -*-

from pylons import g
n = g.n

"""
This library has functions which provide common views into the schema/database
"""

def name_to_uri(name) :
	return g.sparql.doQueryString("""
	PREFIX : <http://theburningkumquat.com/schema/>
	SELECT ?uri WHERE {
		?uri :name "%s" .
	}""" % name)

def uri_to_name(uri) :
	return g.sparql.doQueryString("""
	PREFIX : <http://theburningkumquat.com/schema/>
	SELECT ?name WHERE {
	<%s> :name ?name .
	}""" % uri)

def expand_clauses(base, extra_clauses) :
	"""
	if base = '?uri' and extra_clauses = [':name ?name', ':type ?type'] would return:
	'?uri :name ?name . ?uri :type ?type'
	"""
	if not isinstance(extra_clauses, list) :
		extra_clauses = [extra_clauses]
	return ''.join(['%s %s . ' % (base, clause) for clause in extra_clauses if clause])

def is_type_of(uri, type) :
	return g.sparql.ask("<%s> bk:typeof <%s>" % (uri, type), include_prefix = True)

def instances_of(type, extra_clauses = "") :
	return g.sparql.doQueryRows("""
	PREFIX : <http://theburningkumquat.com/schema/>
	SELECT * WHERE {
		?uri :typeof <%s> .
		%s
	}""" % (type, expand_clauses('?uri', extra_clauses)))

def types_properties(types, extra_clauses = "", optional = True) :
	"""
	given a list of types or a single type, return a list of dictionaries
	representing its properties.  Each dictionary has:
		'prop' : the URI of the property
		'name' : the name of the property
		'unique' : [does not always exist] boolean if this property should only
			have one value
	extra_clauses should be in the form:
		":property_type ?type" or a list of these types of strings
	"""
	if isinstance(types, list) :
		return reduce(list.__add__, [types_properties(x, extra_clauses, optional) for x in types], [])
	if optional :
		query = """
			PREFIX : <http://theburningkumquat.com/schema/>
			SELECT * WHERE {
				{ <%s> :has_property ?prop . }
					UNION
				{ <%s> :optionally_has_property ?prop . }
				?prop :name ?name .
				optional {
					?prop :unique ?unique .
				} .
				%s
			}
		""" % (types, types, expand_clauses('?prop', extra_clauses))
	else :
		query = """
			PREFIX : <http://theburningkumquat.com/schema/>
			SELECT * WHERE {
				<%s> :has_property ?prop .
				?prop :name ?name .
				optional {
					?prop :unique ?unique .
				} .
				%s
			}
		""" % (types, expand_clauses('?prop', extra_clauses))
	#print 'properties_query', query
	properties = g.sparql.doQueryRows(query)
	#print 'properties',properties
	
	# avoid infinite recursion
	if types != n.bk['type'] :
		query = """
		PREFIX : <http://theburningkumquat.com/schema/>
		SELECT ?type WHERE {
			<%s> :typeof ?type
		}
		""" % types
		subtypes = g.sparql.doQueryList(query)
		#print 'subtypes',subtypes
		new_properties = map(lambda x:types_properties(x, extra_clauses, optional), subtypes)
		#print 'new_properties',new_properties
		if new_properties :
			properties += reduce(list.__add__, new_properties)
		#print 'properties',properties
	
	# for now, just get rid of duplicate properties.  If for example a vegetable 
	# is a type and a topic and topic is a type, the properties of type are 
	# included twice.
	
	new_properties = []
	for property in properties :
		if property['prop'] not in (p['prop'] for p in new_properties) :
			new_properties.append(property)
	
	return new_properties