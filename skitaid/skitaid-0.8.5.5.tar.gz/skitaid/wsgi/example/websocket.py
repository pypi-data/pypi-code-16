from skitai.saddle import Saddle
import skitai

app = Saddle (__name__)

app.debug = True
app.use_reloader = True
app.jinja_overlay ()

@app.route ("/echo")
def echo (was, message, client_id, event):
	if was.wsinit ():
		#return was.wsconfig (skitai.WS_SIMPLE, 60, skitai.WS_MSG_JSON)			
		return was.wsconfig (skitai.WS_SIMPLE, 60)
	if event == skitai.WS_EVT_ENTER:
		return "Welcome Client %s" % client_id
	if event: # ignore the other events
		return
				
	was.websocket.send ("You said," + message)
	was.websocket.send ("acknowledge")	

@app.route ("/talk")
def talk (was, name = "Hans Roh"):
	if was.wsinit ():
		return was.wsconfig (skitai.WS_DEDICATE, 60)		
	
	while 1:
		m = was.websocket.getwait (10)
		if m is None:
			break		
		if m.lower () == "bye":
			was.websocket.send ("Bye, have a nice day." + m)
			was.websocket.close ()
			break
		elif m.lower () == "hello":
			was.websocket.send ("Hello, " + name)				
		else:	
			was.websocket.send ("You Said:" + m)

@app.route ("/chat")
def chat (was, message, client_id, event, room_id):
	if was.wsinit ():
		return was.wsconfig (skitai.WS_GROUPCHAT, 60)
	if event == skitai.WS_EVT_ENTER:
		return "Client %s has entered" % client_id
	if event == skitai.WS_EVT_EXIT:
		return "Client %s has leaved" % client_id
	return "Client %s Said: %s" % (client_id, message)
			
@app.route ("/")
def websocket (was, mode = "echo"):
	if mode == "talk":
		mode += "?name=Hans"
	elif mode == "chat":	
		mode += "?room_id=1"
	return was.render ("websocket.html", path = mode)
	
if __name__ == "__main__":
	import skitai
	skitai.run (
		address = "0.0.0.0",
		port = 5000,
		mount = ("/websocket", app)
	)
	