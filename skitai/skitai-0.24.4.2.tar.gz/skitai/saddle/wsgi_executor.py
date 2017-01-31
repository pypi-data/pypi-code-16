from aquests.protocols.http import http_util
from . import cookie
from aquests.lib.reraise import reraise 
import sys
from aquests.lib.athreads import trigger
from aquests.lib.attrdict import AttrDict
from aquests.protocols.http import respcodes

def traceback ():	
	t, v, tb = sys.exc_info ()
	tbinfo = []
	assert tb # Must have a traceback
	while tb:
		tbinfo.append((
			tb.tb_frame.f_code.co_filename,
			tb.tb_frame.f_code.co_name,
			str(tb.tb_lineno)
			))
		tb = tb.tb_next

	del tb
	file, function, line = tbinfo [-1]
	return (
		"%s %s, file %s at line %s, %s" % (
			t, v, file, line, 
			function == "?" and "__main__" or "function " + function
		)
	)

		
class Executor:
	def __init__ (self, env, get_method):
		self.env = env	
		self.get_method = get_method
		self.was = None
				
	def chained_exec (self, method, args, karg):
		# recursive before, after, teardown
		# [b, [b, [b, func, s, f, t], s, f, t], s, f, t]
		
		response = None
		[before, func, success, failed, teardown] = method	
		try:
			if before:
				response = before (self.was)
				if response:
					return response
					
			if type (func) is list:
				response = self.chained_exec (func, args, karg)
					
			else:				
				response = func (self.was, *args, **karg)
				if type (response) is not list:
					response = [response]											
				
		except MemoryError:
			raise
																										
		except Exception as expt:			
			if failed:				
				response = failed (self.was, sys.exc_info ())
			if response is None:
				raise
			else:
				# filed handle exception and contents, just log
				self.was.traceback ()
							
		else:
			success and success (self.was)

		teardown and teardown (self.was)
		return response
		
	def generate_content (self, method, _args, karg):	
		karg = self.parse_kargs (karg)
		self.was.request.args = karg
		response = self.chained_exec (method, _args, karg)
		return response
	
	def parse_kargs (self, kargs):
		allkarg = AttrDict ()
		query = self.env.get ("QUERY_STRING")
		data = None
		_input = self.env ["wsgi.input"]
		if _input:
			if type (_input) is dict: # multipart
				self.merge_args (allkarg, _input)
			else:
				data = _input.read ()
		
		if kargs:
			self.merge_args (allkarg, kargs)
		if query: 
			self.merge_args (allkarg, http_util.crack_query (query))
		if data:
			self.merge_args (allkarg, http_util.crack_query (data))
			
		return allkarg
		
	def merge_args (self, s, n):
		for k, v in list(n.items ()):
			if k in s:
				if type (s [k]) is not list:
					s [k] = [s [k]]
				s [k].append (v)
			else:	 
				s [k] = v
	
	def build_was (self):
		class G:
			pass
			
		_was = self.env["skitai.was"]
		_was.env = self.env
				
		# these objects will be create just in time from _was.
		#_was.cookie = cookie.Cookie (_was.request, _was.app.securekey, _was.app.session_timeout)
		#_was.session = _was.cookie.get_session ()
		#_was.mbox = _was.cookie.get_notices ()
		#_was.g = G ()
		self.was = _was
	
	def commit (self):
		# keep commit order, session -> mbox -> cookie
		if not self.was.in__dict__ ("cookie"):		
			return			
		if self.was.in__dict__ ("session"):		
			self.was.session and self.was.session.commit ()
		if self.was.in__dict__ ("mbox"):
			self.was.mbox and self.was.mbox.commit ()
		self.was.cookie.commit ()
	
	def rollback (self):
		if not self.was.in__dict__ ("cookie"):		
			return			
		# keep commit order, session -> mbox -> cookie
		if self.was.in__dict__ ("session"):		
			self.was.session and self.was.session.rollback ()
		if self.was.in__dict__ ("mbox"):		
			self.was.mbox and self.was.mbox.rollback ()
		self.was.cookie.rollback ()
	
	def isauthorized (self, app, request):			
		try: 
			www_authenticate = app.authorize (request.get_header ("Authorization"), request.command, request.uri)
			if type (www_authenticate) is str:
				request.response ['WWW-Authenticate'] = www_authenticate
				request.response.send_error ("401 Unauthorized")
				return False				
			elif www_authenticate:
				request.user = www_authenticate
					
		except AttributeError: 
			pass
			
		return True
	
	def find_method (self, request, path, handle_response = True):
		current_app, thing, param, respcode = self.get_method (
			path, 
			request.command.upper (), 
			request.get_header ('content-type'),
			request.get_header ('authorization')
		)
		
		if respcode == 401 and self.isauthorized (current_app, request):
			# passed then be normal
			respcode = 0
		
		if handle_response:
			if respcode:
				if respcode == 301:
					request.response ["Location"] = thing
					request.response.send_error ("301 Object Moved", why = 'Object Moved To <a href="%s">Here</a>' % thing)							
				else:
					request.response.send_error ("%d %s" % (respcode, respcodes.get (respcode, "Undefined Error")))
				
		return current_app, thing, param, respcode
		
	def __call__ (self):
		request = self.env ["skitai.was"].request
		current_app, thing, param, respcode = self.find_method (request, self.env ["PATH_INFO"])
		
		if respcode: 
			# unacceptable
			return b""
		
		self.build_was ()
		self.was.subapp = current_app
		try:
			content = self.generate_content (thing, (), param)
		except:				
			self.rollback ()
			if request.response.is_responsable ():
				content = request.response ("500 Internal Server Error", exc_info = self.was.app.debug and sys.exc_info () or None)				
			del self.was.env
			del self.was.subapp
			raise
		
		self.commit ()		
		# clean was
		del self.was.env
		del self.was.subapp
		return content
		