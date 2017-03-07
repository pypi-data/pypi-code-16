#!/usr/bin/python
#from web.wsgiserver import CherryPyWSGIServer
#CherryPyWSGIServer.ssl_certificate = "/home/pi/myserver.crt"
#CherryPyWSGIServer.ssl_private_key = "/home/pi/myserver.key"
import sys
import web
import threading
import json
_shutdown=False
_ver="141"
urls = (
	'/', 'index',
	'/iForge', 'iforge',
	'/kill', 'kill',
	'/ping', 'ping'
)

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.
    app = web.application(urls, globals())
    app.run()

if __name__ == "__main__":
    main()

class index:
    def GET(self):
        print "index print output"
        return "Welcome to the iForge Pi version!"

class myThread (threading.Thread):
    def __init__(self, threadName, code):
        threading.Thread.__init__(self)
        self.name = threadName
        self.code = code
        self.shutdown = False
        
    def run(self):
        global _shutdown
        print "Starting thread"
        print "\n printing debug info"
        print "\n end debug info"
        while not _shutdown:
            exec(self.code,globals(),locals())
            time.sleep(.01)
        print "Exiting thread"
		
class iforge:
    def GET(self):
        return "You have found the code executor function"
		
    def POST(self):
        global _shutdown
        cleanup()
        
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json')
        request=web.input()
        code=request.code
        #line below is the problem. change second argument to globals once and then back to locals and it will work
        try:
			exec (code,globals(),globals())
			msg="code is now successfully running on your pi"
        except:
			msg="An error of type: " + str(sys.exc_value) + " occured."
        reply={'message':msg}
        return json.dumps(reply)
class ping:	
    def POST(self):
        cleanup()
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Content-Type', 'application/json')
        request=web.input()
        reply={'message':'Successfully reached a version of piForge',
        'ver':_ver}
        return json.dumps(reply)

class kill:
    def GET(self): 
        import sys 
        sys.exit(0)

		
def cleanup():
	global _shutdown
	threads=threading.enumerate()
	_shutdown=True
	for t in threads:
		print t.name
		if t.name[:3] == "if_":
			t.join(2)
	_shutdown=False
	return

