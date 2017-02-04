#Using zeromq for publisher socket and it's operations
import zmq

class Publisher:

	#Creating socket and binding port
	def __init__(self, port):
		self.port = port
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PUB)
		self.socket.bind("tcp://*:%s" % self.port)

		#Create a dictionary of list to track all the notes sent
		#The topics and notes are both in the form of string
		self.topiclist = {}

	#Add new topic that can be published		
	def registerTopic(self, utopictitle):
		topictitle = str(utopictitle)
		if(topictitle not in self.topiclist):
			#Create a new list for the topic
			self.topiclist[topictitle] = []
		else:
			raise Exception("Topic is already registered")			

	#Remove a topic
	def unregisterTopic(self, utopictitle):
		topictitle = str(utopictitle)
		if(topictitle in self.topiclist):
			#Delete the topic from dictionary
			del self.topiclist[topictitle]
		else:
			raise Exception("Topic is not registered")						

	#Publish a note
	def publishNote(self, utopictitle, unote):
		topictitle = str(utopictitle)
		note = str(unote)
		if(topictitle in self.topiclist):
			#Send the notes through the socket
			self.socket.send_string("%s %s" % (topictitle, note))
			#Save the notes sent
			self.topiclist[topictitle].append(note)
		else:
			#Failed to publish if topic isn't registered
			raise Exception("Topic isn't registered")
	
	#Grab all the notes which have already been sent
	def allNotesSent(self):
		return self.topiclist	