<%! import kumquat.lib.render_helper as rh %>

<div id="triplestable">
	%if c.rows :
	<table>
		<tr>
			<th>property</th>
			<th>value</th>
			<th>edit</th>
		</tr>
		% for i, row in enumerate(c.rows) :
			% if not row.get('hidden') :
				<tr id="row${i}"><td>
				<% delete = """<a href="javascript:delete_triple('%s', '%s', '%s', %d)">x</a> """ % (
					rh.jsquote(row['sub']),
					rh.jsquote(row['pred']),
					rh.jsquote(row['val']),
					i)
				%>
				${delete}
				% if isinstance(row['pred'], rh.URIRef) :
					${rh.viewurilink(row['pred'])}
				% else :
					${str(row['pred'])}
				% endif
				
				</td><td>
				% if isinstance(row['val'], rh.URIRef) :
					${rh.viewurilink(row['val'])}
				% else :
					${str(row['val'])}
				% endif
				
				</td><td>
				<a href="">edit</a>
				</td></tr>
			% endif
		% endfor
		
		<tr id="new_triple"><td>
		<input type="text" id="new_triple_property" />
		</td><td>
		<input type="text" id="new_triple_value" />
		<textarea id="new_triple_value_textarea"></textarea>
		<a id="new_triple_submit">submit</a>
		</td></tr>
	</table>
	<div id="row_count">${i}</div>
	<div id="triple_value_uri"></div>
	<div id="triple_value_uri_name"></div>
	<a href="javascript:show_add_triple()">add triple</a>
	% endif
</div>