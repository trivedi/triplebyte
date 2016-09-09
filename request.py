import zlib
import logging
import os
import util
import codecs
import datetime


class Request:
	'''
	Object for all HTTP requests
	'''
	def __init__(self, filename, method, root='/website'):
		print 'filename', filename

		# Routing scheme requires that everything be in absolute path format
		if filename == '/' or filename.endswith(root):
			self.__filename = util.create_path(root, '/index.html')
		elif not filename.startswith('/website'):
			self.__filename = util.create_path(root, filename)
		else:
			self.__filename = util.create_path(filename)

		print 'modified filename:', self.__filename
		self.__method = method
		self.__methods = {
			'GET' : self.do_get,
			'HEAD' : self.do_head
		}
		self.__status = self.get_status()
		self.__content = None
		logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

	def get_status(self):
		'''
		Returns the HTTP status for the specified file
		'''
		if os.path.exists(self.__filename):
			if os.stat(self.__filename).st_mode == 33188:
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
		logging.info('"%s %s" %s', self.__method, self.__filename, self.__status)
		resp = self.__methods.get(self.__method)()
		return resp

	def do_get(self):
		'''
		Invokes HTTP GET and returns the source code for @self.__filename as a string
		'''		
		# Get the header for the requested file
		# Content of file will come from do_head because of finding the content-length
		header = self.do_head()

		# Return the file requested (with the appropriate header)
		return header + self.__content # extra header needed to separate from body per HTTP standards (RFC 2616)
	
	def do_head(self):
		'''
		Invokes HTTP HEAD and returns the header for @self.__filename as a string
		'''
		crlf = '\r\n'
		self.__content = self.get_content() # save the content of in case GET is next

		# Build the header
		header = 'HTTP/1.1 ' + util.resp_codes.get(self.__status, '') + crlf
		header += 'Content-Type: ' + util.get_content_type(self.__filename) + '; charset=UTF-8' + crlf
		header += 'Content-Length: %d' % len(self.__content) + crlf
		header += 'Server: Nishad HTTP (Unix)' + crlf
		header += 'Date: ' + datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S CST') + crlf
		# header += 'Content-Encoding: gzip' + crlf
		return header + crlf # end of header denoted by empty field

	def get_content(self):
		'''
		Return content of @self.__filename
		'''
		# Serve templated files in case there isn't an OK HTTP response
		if self.__status != 200:
			self.__filename = util.create_path('/resp_files', '/'+str(self.__status)+'.html')

		with open(self.__filename, 'rb') as f:
			src = f.read()
			# src = zlib.compress(f.read())
		return src





