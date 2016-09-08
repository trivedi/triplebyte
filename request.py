class Request:

	def __init__(self, filename, method):
		self.filename = filename
		self.method = method
		self.methods = {
			'GET' : self.do_get,
			'HEAD' : self.do_head
		}
		self.data = None

	def do_request(self):
		return self.methods.get(self.method)(self.filename)

	def do_get(self, filename):
		print filename
		print 'DOING GET'

		status = None

		if filename == '/':
			status = 200
			filename = 'resp_codes/index.html'
		elif os.path.exists(filename):
			if os.state(filename).st_mode == 33188:
				# group has read access => 200
				status = 200
			else:
				# group does not have read access => 403
				status = 403
		else:
			# Page doesn't exist => 404
			status = 404
		
		# Get the header for the requested file
		header = self.do_head(filename, status)

		with open(filename, 'r') as f:
			src = '\n'.join(f.readlines())

		# Return the file requested (with the appropriate header)
		return header + src
	
	def do_head(self, filename, status):
		'''
		Returns the header for @filename
		'''
		print filename
		print 'DOING HEAD'	
		crlf = '\r\n\r\n'

		# Build the header
		return 'HTTP/1.1 ' + util.resp_codes.get(status, '') + crlf
	
	'''
	# Requesting the header and source
	if not head:
		with open(filename, 'r') as f:
			src = '\n'.join(f.readlines())
		data = header + src

	return data
	'''




def get_src(filename, status, head):
	crlf = '\r\n\r\n'

	header = 'HTTP/1.1 ' + util.resp_codes.get(status, '') + crlf
	data = header
	
	# Requesting the header and source
	if not head:
		with open(filename, 'r') as f:
			src = '\n'.join(f.readlines())
		data = header + src

	return data


