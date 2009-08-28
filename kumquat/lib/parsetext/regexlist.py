#!/usr/bin/env python

# each tuple in relib is (regex, sub)
relib = []

# <h2>
#		lines begin with #
#		# is escaped because of re.VERBOSE
relib.append((r"^\#(?P<h2>.*?)$", "<h2>\g<h2></h2>"))

# <hr />
#		is obnoxious. The $ at the end is especially finicky, even if the \r is removed.
#		from any line with [-_]
relib.append((r"(^[-_]+\r?)$", "<hr \>"))

# <p>
#		convert lines that don't begin with [*#<] to <p>
relib.append((r"^([^\s*\*#<].+?$)", "<p>\g<1></p>"))

# <a> AUTOLINKS
#		requires a word boundary before any link
#		requires whitespace before any link that's only www
relib.append((r"(?P<url>(https?|ftp)://[^'\"\s]*)","<a href=\"\g<1>\">\g<1></a> "))
relib.append((r"(?=\s)(www\.[^'\"\s]*)","<a href=\"http://\g<1>\">\g<1></a> "))
# CUSTOM LINKS
# 		[[Something]] redirects to /view/name/something
#relib.append((r"\[\[(.*?)\]\]","LINK\g<1>LINK"))
#relib.append((r"(?<=\[\[)(?=.*?)\s(?=\]\])","_"))

def internal_link(link):
	#return "<a href=\"/view/name/"+link.lower()+"\">"+link.lower()+"</a>"
	#return "<a href=\"/view/name/%s\">%s</a>" % (link.lower(), link.lower())
	print link, link.lower()
	return '<a href="/view/name/%s">%s</a>' % (link.lower(), link.lower())

relib.append((r"\[\[([\w|,|-|\?]*?)\]\]",internal_link("\g<1>")))
#relib.append((r"\[\[([\w|,|-|\?]*?)\]\]","<a href=\"/view/name/"+"\g<1>".lower()+"\">\g<1></a>"))
#relib.append((r"\[\[([\w|,|-|\?]*?)\]\]", lambda m: "<a href=\"/view/name/%s\">%s</a>" % (m.groups(1).lower(), m.groups(1))))


# LISTS DO NOT WORK
# unordered list
# THIS PLACES <UL> AND (Kind of) works.
# When deleting unneeded uls in the second pass, we run into trouble
# when two deletions have to be done consecutively
# Potentially add \n between <ul> and \g<1> in the first pass
#relib.append((r"^((\s*)\*\s?([^\n]*)\r?.*?^(?!\2\*))", "<ul>\g<1>"))
#relib.append((r"""
#				(?<=^)(						#\1
#					(?:<ul>)?(\s+)			#\2 whitespace (?:<ul>)? might be needed
#					\*\s?				# match the rest of the line
#					.*?
#				(^<ul>(\2\s*)			#\4 redefined whitespace
#				\*\s?.*?)*?
#				)						#\1 closed
#				(?(4)					# if \4 exists...
#				<ul>(?!\4\s*\*)
#				|<ul>(?!\2\s*\*))		# else clause: the error is here
#				  """, "START\g<1>END\n"))