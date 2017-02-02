from skitai.saddle import Saddle
import time

app = Saddle (__name__)
app.debug = True
app.use_reloader = True

class Authorizer:
	def __init__ (self):
		self.tokens = {
			"12345678-1234-123456": ("hansroh", ["user", "admin"], 0)
		}
		
	# For Token
	def handle_token (self, request, callback):
		username, roles, expires = self.tokens.get (request.token)
		if expires and expires < time.time ():
			# remove expired token
			self.tokens.popitem (request.token)
			return callback (request)
		callback (request, username, roles)
	
	# For JWT Claim
	def handle_claim (self, request, callback):
		claim = request.claim		
		expires = claim.get ("expires", 0)
		if expires and expires < time.time ():
			return callback (request)
		callback (request, claim.get ("user"), claim.get ("roles"))
		
	
@app.startup
def startup (wasc):
	wasc.handler.set_auth_handler (Authorizer ())
	
@app.route ("/")
def index (was):
	return "<h1>Skitai App Engine: API Gateway</h1>"


if __name__ == "__main__":
	import skitai
	
	skitai.run (
		clusters = {
			"@pypi": ("https", "pypi.python.org")
		},
		mount = [
			('/', app),
			('/lb', '@pypi')			
		],
		enable_gw = True,
		gw_auth = True,
		gw_secret_key = "8fa06210-e109-11e6-934f-001b216d6e71"
	)
	