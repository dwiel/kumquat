import logging
import MySQLdb
import MySQLdb.cursors
import kumquat.lib.parsetext.parsetext as parsetext

from kumquat.lib.base import *

log = logging.getLogger(__name__)

class WikiController(BaseController):
	
	def __init__(self):
		self.conn = MySQLdb.connect(host = "localhost",
																user = "root",
																passwd = "badf00d",
																db = "kumquat",
																cursorclass = MySQLdb.cursors.DictCursor)
		self.cursor = self.conn.cursor()
		print 'init'
	
	def close(self):
		self.cursor.close()
		self.conn.close()
	
	def _get_page(self, title):
		self.cursor.execute("SELECT * FROM wiki WHERE title like %s ORDER BY time DESC LIMIT 1", title)
		return self.cursor.fetchone()

	def index(self):
		if 'title' not in request.params :
			title = 'index'
		else :
			title = request.params['title']
		
		page = self._get_page(title)
		
		if page :
			#c.__dict__.update(row) # Why doesn't this work?
			for k, v in page.iteritems() :
				c.__setattr__(k, v)
			c.body = parsetext.parsetext(c.body)
		else :
			redirect_to(action='edit', title=title)
		
		self.close()
		return render('/index.mako')
	
	def edit(self):
		if 'title' not in request.params :
			title = 'index'
		else :
			title = request.params['title']
		
		page = self._get_page(title)
		
		if page :
			#c.__dict__.update(row) # Why doesn't this work?
			for k, v in page.iteritems() :
				c.__setattr__(k, v)
		else :
			c.title = title
		
		self.close()
		return render('/edit.mako')
		
	def edit_submit(self):
		title = request.params['title']
		body = request.params['body']
		
		self.cursor.execute("INSERT INTO wiki (title, body) VALUES(%s, %s)", (title, body))
		
		p = {
			'title' : title,
		}
		
		self.close()
		redirect_to(action='index', **p)





















