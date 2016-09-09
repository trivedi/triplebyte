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
		sock.sendall(r.do_request())
		sock.close()
		

def create_socket(hostname, port):
	'''
	Returns a socket object listening on http://@hostname:@port
	'''
	# Create the socket
	try:
		sock = socket(AF_INET, SOCK_STREAM) # Create the socket with TCP protocol
	except error as msg:
		print "Error: could not create socket. Exiting...\n{}".format(msg)
		logging.error('Could not create socket. Terminated server.')
		sys.exit(1)

	# Bind to host and port
	try:
		sock.bind((hostname, port)) # Bind the port to the socket.
		sock.listen(20) # Listen on the given port, and the size of queue is 20.
	except error as msg:
		print "Error: could not bind or listen. Exiting...\n{}".format(msg)
		logging.error('Could not bind or listen. Terminated server.')
		sock.close()

	# If the socket cannot be opened, quit the program.
	if sock is None:
		print "Error: cannot open socket. Exiting...\n"
		logging.error('Could open socket. Terminated server.')
		sys.exit(1)

	return sock


def main():
	'''
	Sets up the socket for listening at host and port.
	Also creates a thread monitoring for program termination.
	'''
	logging.basicConfig(filename='server.log',level=logging.DEBUG,format='%(asctime)s %(message)s')

	hostname = 'localhost'
	port = 9002
	if len(sys.argv) >= 2:
		port = int(sys.argv[1])

	
	# Monitor thread will wait for the 'quit' signal
	monitor = threading.Thread(target=monitorQuit, args=[])
	monitor.start()


	'''
	# Keep accepting client connections, generating a new thread for each connection
	while 1:

		client, addr = sock.accept()
		server = threading.Thread(target=request, args=[client, addr[0]])
		server.start()
	'''


	sock = create_socket(hostname, port)
	print 'Server is listening on http://{}:{}'.format(hostname, port)
	logging.info('Server has started on http://{}:{}'.format(hostname, port))


	# Create and run dispatcher threads
	for i in range(10):
		Dispatcher(i, sock).start()
		logging.info('Dispatcher Thread-%d created' % i)


	# Create and run worker threads
	for i in range(10):
		Worker(i).start()
		logging.info('Worker Thread-%d created' % i)


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

	def __init__(self, id, sock):
		threading.Thread.__init__(self)
		self.setName('Dispatcher-%d' % id)
		self.sock = sock

	def run(self):
		'''
		Insert client connections into the queue 
		'''
		global request_queue
		# Keep accepting client connections and put client sockets into request queue
		while 1:
			client, addr = self.sock.accept()
			request_queue.put((client, addr))
			print 'Dispatched connection from', addr
			time.sleep(random.random())




class Worker(threading.Thread):
	'''
	Get a request from the queue and serve it
	'''

	def __init__(self, id):
	    threading.Thread.__init__(self)
	    self.setName('Worker-%d' % id)


	def run(self):
		'''
		Serve the request and pass it back to the client
		'''
		global request_queue
		# Get a client connection from the queue and serve its request
		while 1:
			client_conn = request_queue.get()
			self.serve(client_conn[0], *client_conn[1])
			print 'Served request from', client_conn[1]
			request_queue.task_done()
			time.sleep(random.random())



	def serve(self, client_sock, addr, port):
		'''
		Receives request from client socket and returns response back to the socket
		'''
		recv = client_sock.recv(1024)
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
			client_sock.sendall(r.do_request())
			client_sock.close()
			




if __name__ == '__main__':
	main()








