import os
import sys
import time
import socket
import warnings
import threading

class Socket:
	def __init__(self,ip,port):
		self.ip = ip
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.ip, self.port))
	def send(self,message):
		try:
			self.sock.send(bytes(message, encoding='utf-8'))
		except:
			warnings.warn("Warning: connection tunnel has been broken. Disconnected from server.")
	def receive(self):
		try:
			data = self.sock.recv(4096).decode()
			if data == chr(402): return None
			else: return data
		except:
			warnings.warn("Warning: connection tunnel has been broken. Disconnected from server.")
			return None
	def recieve(self,conn):
		return self.receive(conn)
	def disconnect(self):
		self.sock.shutdown(2)
		self.sock.close()
	def timeout(self,n):
		try:
			self.sock.settimeout(n)
		except: raise TypeError



class Server:
	def __init__(self,ip,port):
		self.ip = ip
		self.port = port
		self.user_count = 0
		self.connections = []
		self.sock = socket.socket()
		self.stoplistening = 0
		self.nowstopped = 0
		self.listenthread = None
		self.sock.bind((self.ip, self.port))
	def send(self,conn,message):
		try:
			conn.send(bytes(message, encoding='utf-8'))
		except:
			try:
				self._connrem(conn)
			except ValueError:
				pass
			self.user_count = len(self.connections)
			warnings.warn("Warning: connection tunnel has been broken. User has disconnected.")
	def sendall(self,message):
		for conn, addr in self.connections:
			try:
				self.send(conn, message)
			except:
				try:
					self._connrem(conn)
				except ValueError:
					pass
				self.user_count = len(self.connections)
				warnings.warn("Warning: connection tunnel for " + addr[0] + " has been broken. User has disconnected.")
	def receive(self,conn):
		try:
			return conn.recv(4096).decode()
		except:
			self._connrem(conn)
			warnings.warn("Warning: connection tunnel has been broken. User has disconnected.")
			return None
	def recieve(self,conn):
		return self.receive(conn)
	def listen(self):
		try:
			self.listenthread = threading.Thread(target = self._listendaemon, args = ())
			self.listenthread.daemon = True
			self.listenthread.start()
		except:
			raise ListenThreadActive("a listen thread is already active")
			
	def stoplisten(self):
		self.stoplistening = 1
		while self.nowstopped == 0:
			pass
		self.stoplistening = 0
		self.nowstopped = 0
		self.listenthread.join()
	def autorefresh(self):
		self.conncheckthread = threading.Thread(target = self._connrefresh)
		self.conncheckthread.daemon = True
		self.conncheckthread.start()
	def timeout(self,n):
		try:
			self.sock.settimeout(n)
		except: raise TypeError
	def _listendaemon(self):
		self.sock.listen(0)
		while True:
			if self.stoplistening == 0:
				conn, addr = self.sock.accept()
				if self.stoplistening == 1:
					pass
				else:
					self.connections.append((conn, addr))
					self.user_count = len(self.connections)
			else:
				break
	def _connrem(self,conn):
		for tup in self.connections:
			if tup[0] == conn:
				self.connections.remove(tup)
	def _connrefresh(self):
		while 1:
			time.sleep(0.3)
			for conn, addr in self.connections:
				try:
					conn.send(bytes(chr(402), encoding = 'utf-8'))
				except:
					self._connrem(conn)
					self.user_count = len(self.connections)

class ListenThreadActive(Exception):
	def __init__(self, message):
		self.message = message