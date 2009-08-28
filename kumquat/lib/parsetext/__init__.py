# -*- coding: utf-8 -*-
""" ParseText lib, __init__.py
Defines and compiles a dictionary of regexes and their corresponding substitutions.
Notes:
	HTML entities are escaped in parsetext.py
	Unexpected results have occurred when using the $ operator, notably in <hr />
"""
#!/usr/bin/env python

from pylons import g
import re
import kumquat.lib.refn as refn

g.regexes = []

# each tuple in relib is (regex, sub)
relib = []





# <h2>
#		lines begin with #
#		# is escaped because of re.VERBOSE
#relib.append((r"^\#(.*?)$", "<h2>\g<1></h2>"))  # Simple h2 replace
relib.append((r"^(\#{1,5})(.*?)(?:\1\r)?$", lambda x: '<h%d>%s</h%d>' % (len(x[0])+1, x[1], len(x[0])+1)))
#		\1: The hashes
#		\2: The line to be headered





# <hr />
#		is obnoxious. The $ at the end is especially finicky, even if the \r is removed.
#		from any line with [-_]
relib.append((r"(^(?:-+|_+)\r?)$", "<hr />"))




# LISTS

def lists (text) :
	prefix = re.match('[\r\n]*', text).group()
	text = text.lstrip('\r\n')
	level = re.match('[ \t]*', text).group()
	testfix = re.match('[\r\n]*', text).group()
	
	regex = re.compile('(?:\n?(?:%s)\*([^\n]*))((?:\n?(?:%s)[ \t]+\*[^\n]*)+)?' % (level, level),re.S | re.M)
	# \1: List items on the same level
	# \2: Sublists
	#
	# Note: re.VERBOSE cannot be used, as level is rendered directly, and verbose ignores newlines
	# Regex explained in verbose:
	#(?:
	#	\n?					# Newline to ensure the start of a line
	#	(?:%s)				# Level whitespace
	#	\*([^\n]*)		# \1: Match and CAPTURE the item
	#)
	#(					# \2: Open \2, sublists.
	#	(?:					# See comments from above...
	#		\n?
	#		(?:%s)[ \t]+	# Identify an item that starts with more than level whitespace
	#		\*[^\n]*
	#	)+					# Include all list items within the sublist
	#)?					# \2: Close
	
	print regex
	
	def listitems(list) :
		if (isinstance(list[1], basestring)) :
			list[0] = '<li>'+list[0]+lists(list[1])+'</li>'
			return list[0]
		else :
			list[0] = '<li>'+list[0]+'</li>'
			return list[0]
			
	
	text = refn.sub(regex, listitems, text)
	
	text = prefix+'<ul>'+text+'</ul>'
	return text

#relib.append((r"([\r\n]*(?:\n?[ \t]*\*[^\n]*)+?)(?=\r\n\r\n|\Z)", lists))
relib.append((r"([\r\n]*(?:\n?[ \t]*\*[^\n]*)+?)(?=\r\n\s*[^\*]|\Z)", lists))
#		[\r\n]* before the first bullet




# <p> <br />
#		convert lines that don't begin with [*#<] to <p>
#		handles <br /> within paragraphs
relib.append((r"""
			^(					# 1: Everything but the startline and \n at the end
				(?:				# Start line
					[^\s\*\#<]	# Start with anything but \s,*,#,<
					[^\n]*?		# Capture the line
					\n?			# Allow for only ONE newline at a time
				)+$				# Repeat line until an endline
			)					# 1: Close
			  """, lambda x: '<p>%s</p>' % x.replace("\n","<br />")))

#		handles <br /> outside of paragraphs
relib.append((r"""
			(?:						# Exceptions
				(?<=<hr\ />)
			)(\r?\n)^\r?$			# 1: Newline before <br />
			  """, "\g<1><br />"))

#relib.append((r"<hr\ />","<br />"))



#
#	LINKS: ALL KINDS
#		<a></a>

# Custom Links
# 		[[Something]] redirects to /view/name/something
#		Replaces " "  with "_" in the link only
relib.append((r"\[\[([\w|,|-|\?|\ ]*?)\]\]", lambda x: '<a href="/view/name/%s">%s</a>' % (x.lower().replace(" ","_"), x.lower())))

# Autolinks
#		requires a word boundary before any link
#		requires whitespace before any link that's only www
#relib.append((r'\[([\w|,|-|\?|\ ]*?)\]:?\ ?((https?|ftp)://[^\'"\s]*)','<a href="\g<2>">\g<1></a>'))
#relib.append((r'\[([\w|,|-|\?|\ ]*?)\]:?\ ?(?=\s)(www\.[^\'"\s]*)','<a href="http://\g<2>">\g<1></a>'))

def links (text) :
	d = {}
	lre = re.compile('''
			(?:<br\ />)?		# Lines that start with [tag]
			\[([^\n\[]+?)\]		# 1: [tag]
			\ ?[:\-]?\ ?		# Space before link
			(					# 2: link
				(?:https?|ftp)://
				[^'"\s]*
			)
			''', re.M | re.S | re.X)
	iter = lre.findall(text)
	for m in iter :
		d[m[0]] = m[1]
	text = lre.sub('', text)
	tags = re.compile('\[([^\n\[]+)(?!<br\ />)\]', re.M | re.S | re.X).split(text)
	for i in range(len(tags)) :
		if i%2==1 :
			if tags[i] in d :
				tags[i] = '<a href="%s">%s</a>' % (d[tags[i]], tags[i])
			else :
				tags[i] = '['+tags[i]+']'
	return ''.join(tags)
	
relib.append((r'(.*)',links))
relib.append((r'(?<!<a\ href=")((https?|ftp)://[^\'"\s]*)','<a href="\g<1>">\g<1></a>'))
relib.append((r'(?<=\s)(www\.[^\'"\s]*)','<a href="http://\g<1>">\g<1></a>'))




for item in relib:
	g.regexes.append((re.compile("%s" % item[0],re.S | re.M | re.X), item[1]))