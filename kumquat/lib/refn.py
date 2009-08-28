#!/usr/bin/env python


import re

def sub (regex, replace, text) :
	
	# If regex is a string, compile it
	if isinstance(regex, basestring) :
		# By default, regex is compiled with MULTILINE, DOTALL, and VERBOSE
		regex = re.compile(regex, re.S | re.M | re.X)
	
	
	# Use hasattr(o, '__call__') instead of callable(o)
	#	Callable is removed in python 3.0	
	if hasattr(replace, '__call__') :
		
		# Calculate the number of capture groups
		# (plus one non-matching group, which is always starts at index 0)
		num_groups = regex.groups + 1
		
		# Make sure there is at least one capturing group
		if num_groups > 1 :
			temp = regex.split(text)
			for i in range(len(temp)/num_groups):
				
				# If there is only one capturing group, pass its value
				if num_groups == 2 :
					input = temp[i*num_groups+1]
					
				# If there are multiple capturing groups, pass a list of values
				else :
					input = []
					for j in range(1, num_groups):
						input.append(temp[i*num_groups+j])
						temp[i*num_groups+j] = ''
						
				temp[i*num_groups+1] = replace(input)
			text = ''.join(temp)
	else :
		print regex.findall(text)
		text = regex.sub(replace, text)
	return text