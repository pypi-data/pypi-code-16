import datetime
from SeasObjects.common.RESOURCE import RESOURCE
from SeasObjects.common.Tools import Tools
from SeasObjects.model.Activity import Activity
from SeasObjects.model.Notification import Notification
from SeasObjects.seasexceptions.InsufficientDataException import InsufficientDataException

import traceback

class NotificationFactory(object):

	def __init__(self):
		pass
	
	def create(self, generatedBy):
		notification = Notification()
		if (generatedBy is None or (generatedBy is not None and generatedBy == "")):
			raise InsufficientDataException("Invalid seas:generatedBy URI.");

		g = Activity(generatedBy)
		g.clearTypes()
		notification.setGeneratedBy(g)

		# timestamp of when this message is being generated (now)
		notification.setGeneratedAt(datetime.datetime.now())
		
		return notification

	def fromString(self, data, serialization):
		try:
			return Notification().parse(Tools().getResourceByType(RESOURCE.NOTIFICATION, Tools().fromString(data, serialization)))
		except:
			print "Unable to parse Evaluation by type seas:Notification from the given string."
			traceback.print_exc()
			return None

