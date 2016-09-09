import zlib
import sys
import threading
import os
import stat
import logging
import Queue
import random, time
from socket import *
from os import kill, getpid

from request import Request
import util



def monitorQuit():
	'''
	Watches for user inputting 'exit' on terminal to kill server
	'''
	while 1:
		sent = raw_input()
		if sent == 'exit':
			os.kill(os.getpid(), 9)


def request(sock, addr):
	'''
	Receives request from client socket and returns response back to the socket
	'''
	recv = sock.recv(1024)
	print 'received', recv
	recv = recv.split()

	'''
	Request method - recv[0]
	URL path       - recv[1]
	HTTP Version   - recv[2]
	'''
	method, filename, http_version = recv[:3]

	# Check for malformed request by checking request type and HTTP version
	if recv == [] or method not in util.req_methods \
				  or http_version not in ['HTTP/1.1', 'HTTP/1.0']:
		sock.close()
	else:
		print 'creating req object'
		r = Request(filename, method)
		r.do_request()
		sock.sendall(r.data)
		sock.close()
		
def main():
	'''
	Sets up the socket for listening at host and port.
	Also creates a thread monitoring for program termination.
	'''
	logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

	host = 'localhost'
	port = 9002
	if len(sys.argv) >= 2:
		port = int(sys.argv[1])

	# Create the socket
	try:
		sock = socket(AF_INET, SOCK_STREAM) # Create the socket with TCP protocol
	except error as msg:
		print "Error: could not create socket. Exiting...\n{}".format(msg)
		logging.error('Could not create socket')
		sys.exit(1)

	# Bind to host and port
	try:
		sock.bind((host, port)) # Bind the port to the socket.
		sock.listen(20) # Listen on the given port, and the size of queue is 20.
	except error as msg:
		print "Error: could not bind or listen. Exiting...\n{}".format(msg)
		logging.error('Could not bind or listen')
		sock.close()

	# If the socket cannot be opened, quit the program.
	if sock is None:
		print "Error: cannot open socket. Exiting...\n"
		sys.exit(1) 

	# Monitor thread will wait for the 'quit' signal
	monitor = threading.Thread(target=monitorQuit, args=[])
	monitor.start()

	print 'Server is listening on http://{}:{}'.format(host, port)
	logging.info('Server has started')

	'''
	for i in range(10):
		Worker().start()

	for i in range(10):
		Dispatcher().start()
	'''


	# Keep accepting client connections, generating a new thread for each connection
	while 1:
		client, addr = sock.accept()
		server = threading.Thread(target=request, args=[client, addr[0]])
		server.start()

		'''
		A smarter way to use threading in a server:
		
		* N worker threads takes requests for files and inserts them into a queue
		* M dispatcher threads take a request off the queue and serve the request

		The queue is therefore a critical section and we need a mutex lock on it

		This would be a more efficient use of resources rather than spawning multiple threads or a single thread
		'''

dispatcher_queue = []
request_queue = Queue.Queue() # Synchronized queue

class Dispatcher(threading.Thread):
	'''
	Worker thread takes a request and puts it into the request queue
	'''

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		'''
		Insert request into the queue 
		'''
		global request_queue
		while 1:
			num = random.choice(range(5))
			request_queue.put(num)
			print 'Dispatched', num
			time.sleep(random.random())


class Worker(threading.Thread):
	'''
	Get a request from the queue and serve it
	'''

	def __init__(self):
	    threading.Thread.__init__(self)

	def run(self):
		'''
		Serve the request and pass it back to the client
		'''
		global request_queue
		while 1:
			num = request_queue.get()
			print 'Served request', num
			request_queue.task_done()
			time.sleep(random.random())

if __name__ == '__main__':
	main()








