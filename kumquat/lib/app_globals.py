# -*- coding: utf-8 -*-
"""The application's Globals object"""
from pylons import config

from SimpleSPARQL import *
from rdflib import Namespace, URIRef

class Globals(object):
	"""Globals acts as a container for objects available throughout the
	life of the application
	"""

	def __init__(self):
		"""One instance of Globals is created during application
		initialization and is available during requests via the 'g'
		variable
		"""
		
		self.n = globalNamespaces()
		self.n.bind('bk', '<http://theburningkumquat.com/schema/>')
		self.n.bind('bkitem', '<http://theburningkumquat.com/item/>')
		
		self.sparql = SimpleSPARQL("http://localhost:2020/queryKumquat",
		                           sparul = "http://localhost:2020/updateKumquat")
		self.sparql.setNamespaces(self.n)

