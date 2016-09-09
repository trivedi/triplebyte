
# HTTP request methods
req_methods = {
	'GET',
	'HEAD'
}

# HTTP response codes
resp_codes = {
	200: '200 OK',
	400: '400 Bad Request',
	401: '401 Unauthorized',
	403: '403 Forbidden',
	404: '404 Not Found',
	405: '405 Method Not Allowed'
}

# Content-Type
content_type = {
	'text' : 'text/plain',
	'html' : 'text/html',
	'css' : 'text/css',
	'gif' : 'image/gif',
    'jpg' : 'image/jpeg',
    'jpeg' : 'image/jpeg',
    'png': 'image/png',
    'pdf' : 'application/pdf',
    'mp3' : 'audio/mpeg'
}

def get_content_type(filename):
	'''
	Returns the content-type that goes in the header based on @filename's extension
	'''
	ext = filename[filename.rfind('.')+1:] # rfind returns the last index of specified substring
	print filename
	print ext
	return content_type.get(ext, 'xxx')