# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

""" Simple web server for the Kervi application """
import os
import time
import kervi.utility.nethelper as nethelper
import kervi.spine as spine

try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except:
    from http.server import SimpleHTTPRequestHandler

try:
    from BaseHTTPServer import HTTPServer
except:
    from http.server import HTTPServer

import threading
import kervi_ui

#try:
from socketserver import ThreadingMixIn
class _HTTPServer(ThreadingMixIn, HTTPServer):
    pass
# except:
#     print("ThreadingMixIn not found, use single thread web server")
#     class _HTTPServer(HTTPServer):
#         def __init__(self, addres, handler):
#             HTTPServer.__init__(self, addres, handler)

SERVER = None
ASSET_PATH = ""
def start(ip_address, http_port, ws_port):
    global SERVER
    kervipath = os.path.dirname(kervi_ui.__file__)
    docpath = os.path.join(kervipath, "web/dist")

    js_file = open(docpath+"/global.js", "w")
    js_file.write("kerviSocketAddress='" + str(ip_address) + ":" + str(ws_port) + "';")
    js_file.close()

    #cwd = os.getcwd()
    os.chdir(docpath)
    SERVER = _HTTPServer((ip_address, http_port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=SERVER.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(2)
    #os.chdir(cwd)

def stop():
    print("stop web server")
    SERVER.shutdown()
