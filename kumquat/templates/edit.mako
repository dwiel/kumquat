<%inherit file="base.mako" />

<%def name="title()">
 The Burning Kumquat: Wiki (edit): ${c.title}
</%def>

<%def name="sidebar()">
</%def>

<h1>Editing: ${c.title}</h1>
<form name="edit" action="edit_submit" type="post">
	<input type="hidden" name="title" value="${c.title}">
	<div id="pbody">
		<textarea name="body" class="span-17" style="height: 400px;">${c.body}</textarea>
	</div>
	<input type="submit" value="Save">
</form>


