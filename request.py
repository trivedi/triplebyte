import zlib
import logging
import os
import util
import codecs


class Request:
	'''
	Object for all HTTP requests
	'''
	def __init__(self, filename, method, root='/website'):
		print 'filename', filename
		
		# Routing scheme requires that everything be in absolute path format
		if filename == '/' or filename.endswith(root):
			self.filename = util.create_path(root, '/index.html')
		elif not filename.startswith('/website'):
			self.filename = util.create_path(root, filename)
		else:
			self.filename = util.create_path(filename)

		print 'modified filename:', self.filename
		self.method = method
		self.methods = {
			'GET' : self.do_get,
			'HEAD' : self.do_head
		}
		self.status = self.get_status()
		self.data = None
		logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

	def get_status(self):
		'''
		Returns the HTTP status for the specified file
		'''
		if os.path.exists(self.filename):
			if os.stat(self.filename).st_mode == 33188:
				# group has read access => 200
				return 200
			else:
				# group does not have read access => 403
				return 403
		else:
			# Page doesn't exist => 404
			return 404

	def do_request(self):
		'''
		Executes the HTTP method and returns the results as a string
		'''
		self.data = self.methods.get(self.method)()
		return self.data

	def do_get(self):
		'''
		Invokes HTTP GET and returns the source code for @self.filename as a string
		'''		
		# Get the header for the requested file
		header = self.do_head()

		filename = self.filename
		# Serve templated files in case there isn't an OK HTTP response
		if self.status != 200:
			filename = util.create_path('/resp_files', '/'+str(self.status)+'.html')

		with open(filename, 'rb') as f:
			src = f.read()
			# src = zlib.compress(f.read())

		logging.info('"%s %s" %s', self.method, self.filename, self.status)

		# Return the file requested (with the appropriate header)
		return header + '\r\n' + src # extra header needed to separate from body per HTTP standards (RFC 2616)
	
	def do_head(self):
		'''
		Invokes HTTP HEAD and returns the header for @self.filename as a string
		'''
		crlf = '\r\n'

		# Build the header
		header = 'HTTP/1.1 ' + util.resp_codes.get(self.status, '') + crlf
		header += 'Content-Type: ' + util.get_content_type(self.filename) + '; charset=UTF-8' + crlf
		# header += 'Content-Encoding: gzip' + crlf
		return header
	





