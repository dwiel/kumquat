<%inherit file="base.mako" />

<%def name="title()">
The Burning Kumquat: ${c.title}
</%def>

<form action="/search/basic" method="get">
<input type="text" name="query" />
<input type="submit" value="Search" />
</form>
<br>
<br>

<h1>
	<div id="title" style="float:left;margin-right:0.5em">${c.title_header or c.title}</div>
</h1>
<div id="title-edit">
	${c.title_edit}
</div>
<div style="clear:both"></div>
<br>
<div id="pbody">
${c.body}
</div>
