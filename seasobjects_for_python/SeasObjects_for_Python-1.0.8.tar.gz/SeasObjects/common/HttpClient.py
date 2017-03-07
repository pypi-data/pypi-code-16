import urllib, urllib2
from urlparse import urlparse
import sys
import traceback

class HttpClient(object):
	SEAS_METHOD_REQUEST = "Request"
	SEAS_METHOD_RESPONSE = "Response"
	SEAS_METHOD_COMMAND = "Command"
	
	def __init__(self):
		pass
	
	def sendPost(self, server_uri, payload, content_type = "text/turtle", accept_type = "text/turtle", **otherHeaders):
		'''
		return two items: response message body, and content-type header
		'''		
		response = ""
		contentType = ''
		headers = { "content-type" : content_type, 'accept': accept_type }
		for name, value in otherHeaders.items():
			headers[name] = value
		try:
			req = urllib2.Request(server_uri, payload, headers)
			# use a 5s timeout
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				data = filehandle.read()
				response = data
				contentType = filehandle.info().getheader('Content-Type')		
		except urllib2.HTTPError, e:
			print 'HTTPError --- ', str(e.reason),' Code: ', str(e.code)
			# raise this error up in order to handle it.
			raise e
		except urllib2.URLError:
			traceback.print_exc()
 			 		
 		return response, contentType

	def sendGet(self, server_uri):
		response = ""
		try:
			req = urllib2.Request(server_uri)
			# use a 5s timeout
			filehandle = urllib2.urlopen(req, timeout = 5)
			if filehandle is not None:
				data = filehandle.read()
				response = data
		except:
			print "Failed in contacting", server_uri
			print sys.exc_info()[1]
 			response = None
 		finally:
 			return response
 		
		return response
	