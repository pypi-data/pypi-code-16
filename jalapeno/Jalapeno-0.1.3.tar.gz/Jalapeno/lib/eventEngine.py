from queue import Empty
from multiprocessing import Process,Queue
from threading import Thread

class eventEngine():

	def __init__(self):
		self.__eventQueue = Queue()
		self.__commander = Queue()
		self.__response ={'Stop':self.Stop,
							'Killer':self.Killer}
		self.__active = False
		self.__threads = {}
		self.__procs = {}
		self.test = []
		# self.__handlers = {}

	def __Run(self):
		while self.__active:
			print('Engine is ALive...\b',self.__procs)
			try:
				command = self.__commander.get(block=True,timeout=1)
				if command == 'Stop':
					self.__response[command]()
				elif command == 'Killer':
					self.__response[command]('APP')

			except Empty:
				pass
			try:
				event = self.__eventQueue.get(block=True,timeout=1)
				self.__EventProcess(event)
			except Empty:
				pass

	def __EventProcess(self,event):
		if event.type_ == 'Proc':
			starter = Process(target = event.func,args=(self.Listen,))
			self.__procs[event.name]=starter
		elif event.type_ == "Thread":
			starter = Thread(target = event.func)
			self.__threads[event.name]=starter
		starter.start()
		if event.join == True:
			self.__threads[event.name].join()
			del self.__threads[event.name]
		# if event.type_ in self.handlers:
		# 	for handlers in self.__handlers[event.type_]:
		# 		handler(event)

	def Start(self):
		self.__active = True
		self.__Run()

	def Stop(self):
		print(self.__procs)
		self.__active = False
		for each in list(self.__threads.values())+list(self.__procs.values()):
			try:
				each.terminate()
				each.join()
			except:
				print(each.pid,"Terminate error")
				each.join()
				pass
	def Killer(self,event_name):
		
		self.__procs[event_name].terminate()
		self.__procs[event_name].join()
		del self.__procs[event_name]
	def Listen(self,command=None,event=None,kill=None):
		if command:
			self.__commander.put(command)
		if event:
			self.__eventQueue.put(event)
		if kill:
			self.__commander.put('Killer') #####


class Event():

	def __init__(self,name,type_,func,join = False):
		self.name = name
		self.type_  = type_
		self.func = func
		if self.type_ == "Thread" or join == True:
			self.join = True
		else:
			self.join = False

























