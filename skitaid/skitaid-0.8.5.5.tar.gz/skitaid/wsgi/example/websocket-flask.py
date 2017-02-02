from flask import Flask, render_template, request
from skitai.saddle import jinjapatch
import skitai

app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.jinja_env = jinjapatch.overlay (__name__)

@app.route ("/echo")
def echo ():
	if "websocket_init" in request.environ:
		request.environ ["websocket_init"] = (skitai.WS_SIMPLE, 60, ("message", "client_id", "event"))
		return ""
	
	request.environ ["websocket"].send ('1st: ' + request.args.get ("message", ""))
	return "2nd: " + request.args.get ("message", "")

@app.route ("/chat")
def chat ():
	if "websocket_init" in request.environ:
		request.environ ["websocket_init"] = (skitai.WS_GROUPCHAT, 60, ("message", "client_id", "event", "room_id"))
		return ""

	event = request.args.get ("event")
	client_id = request.args.get ("client_id", "")
	message = request.args.get ("message", "")
	
	if event == skitai.WS_EVT_ENTER:
		return "Client %s has entered" % client_id
	if event == skitai.WS_EVT_EXIT:
		return "Client %s has leaved" % client_id
	return "Client %s Said: %s" % (client_id, message)
				
@app.route ("/")
def websocket ():
	mode = request.args.get('mode', '')
	if mode == "talk":
		mode += "?name=Hans"
	elif mode == "chat":	
		mode += "?room_id=1"
	elif mode == "multi":	
		mode += "?room_id=2"
	return render_template ("websocket-flask.html", path = mode)
	
if __name__ == "__main__":
	import skitai
	skitai.run (
		address = "0.0.0.0",
		port = 5000,
		mount = ("/websocket", app)
	)
	