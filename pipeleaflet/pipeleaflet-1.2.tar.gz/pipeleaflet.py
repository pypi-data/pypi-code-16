import os
import json
from IPython.display import IFrame
from multiprocessing import Process
import future
import sys
import random
import time
import subprocess

if (sys.version_info > (3, 0)):
	import http.server as SimpleHTTPServer
	import socketserver as SocketServer

else:
	import SocketServer
	import SimpleHTTPServer




# sets up a localhost
def localhost_thing():
	subprocess.call(["//anaconda/bin/freeport","8000"])
	PORT = 8000


	Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

	httpd = SocketServer.TCPServer(("", PORT), Handler)

	print("serving at port", PORT)
	httpd.serve_forever()

def make_starting_block():
	string = '''
<html>
<head>
<meta charset=utf-8 />
<title>PipeLeaflet</title>
<meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
<script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>

 <script src="https://unpkg.com/leaflet@1.0.0-rc.3/dist/leaflet.js"></script>
 <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.0-rc.3/dist/leaflet.css" />
 <div id="map"></div>

<style>
  body { margin:0; padding:0; }
  #map { position:absolute; top:0; bottom:0; width:100%; }
</style>
</head>
<body>
<style>
table, th, td {
    border: 1px solid black;
}
</style>

<script>
var map = L.map('map');

map.setView([39.9,-79.9], 4);
mapLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>';
L.tileLayer(
	'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '&copy; ' + mapLink + ' Contributors',
		maxZoom: 15,
	}).addTo(map);
map.setMaxZoom(20)
'''
	return string


	
# the function actually used to make the styles table
# headers for each geojson property parsed in here 
# html table code comes out 
def make_rows(headers):
	'''
	newheaders = []
	for row in headers:
		string = "features.properties['%s']" % row
		newheaders.append(string)
	headers = newheaders
	'''
	varblock = []
	# makes a list of rows from a given input header
	for row in headers:
		row1 = row
		row2 = row
		if row == headers[0]:
			newrow = """            var popupText = "<table><tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
		else:
			newrow = """            var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
		varblock.append(newrow)
		if row == headers[-1]:
			newrow = """            var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+</td></tr></table>"; """ % (row1,row2)
	total = ''
	for row in varblock:
		total += row	

	return total

# given a point dictrow checks to see
# if 'opacity' is in dict if it is replaces it 
# correct label
def lint_opacity(dictrow): 
	newdictrow = {}
	for row in dictrow.keys():
		if row == 'opacity':
			newdictrow['fillOpacity'] = dictrow['opacity']
		else:
			newdictrow[row] = dictrow[row]
	return newdictrow

# analyzes each figure given in dictrow
# determines if given figure is header value or actual value
def analyze_dictrow(dictrow):
	for row in dictrow.keys():
		keyrow = row
		if row == 'color':
			if not '#' in str(dictrow[row]):
				dictrow[keyrow] = "feature.properties['%s']" % dictrow[row]
		elif row == 'radius':
			stringrow = str(dictrow[row])
			bool = False
			for row in stringrow:
				if not str(row) in '0123456789':
					bool = True
			if bool == True:
				dictrow[keyrow] = "feature.properties['%s']" % stringrow
		elif row == 'fillOpacity':
			if not '.' in str(dictrow[row]):
				dictrow[keyrow] = "feature.properties['%s']" % stringrow
		elif row == 'opacity':
			if not '.' in str(dictrow[row]):
				dictrow[keyrow] = "feature.properties['%s']" % stringrow
		elif row == 'weight':	
			stringrow = str(dictrow[keyrow])
			bool = False
			for row in stringrow:
				if not str(row) in '0123456789':
					bool = True
			if bool == True:
				dictrow[keyrow] = "feature.properties['%s']" % stringrow
		elif row == 'zooms':
			intbool = True
			if isinstance(dictrow[keyrow],list):
				teststring = dictrow[keyrow][0]
				testlist = dictrow[keyrow]
				for row in str(teststring):
					if len(str(teststring)) >= 3:
						intbool = False
				if intbool == False:
					headerbool = True
					dictrow[keyrow] = ["layer.feature.properties['%s']" % testlist[0],"layer.feature.properties['%s']" % testlist[1]]					
			else:
				# this argument is for if you want window dependent styling but 
				# dont want to putin specific zoom values
				if dictrow[keyrow] == True:
					dictrow[keyrow] = [0,20]
	return dictrow

# gets the style strings needed to create the bindings
# can either 1 or two strings
def get_style_strings(element,dictrow):
	colorkey = False
	if colorkey == False and not dictrow == False:
		# linting dictrow before hard comparisons are done
		dictrow = safe_dict_options(dictrow,element)
		dictrow = analyze_dictrow(dictrow)
		if element == 'Point':
			if 'properties' in dictrow['color']:
				string1 = "{color: %s}" % dictrow['color']
			else:
				string1 = "{color: '%s'}" % dictrow['color']
			string2 = "{radius: %s, fillOpacity: %s}" % (dictrow['radius'],dictrow['fillOpacity'])
			return string1,string2
		else:
			if 'properties' in dictrow['color']:
				string = '{"color": %s,"weight": %s,"opacity": %s}' % (dictrow['color'],dictrow['weight'],dictrow['opacity'])
			else:
				string = '{"color": "%s","weight": %s,"opacity": %s}' % (dictrow['color'],dictrow['weight'],dictrow['opacity'])
			return string
	elif not colorkey == False:
		if element == 'Point':
			keystring = "feature.properties['%s']" % colorkey
			string1 = "{color: %s}" % keystring
			string2 = '{radius: 2, fillOpacity: 0.85}'
			return string1,string2
		else:
			keystring = "feature.properties['%s']" % colorkey
			string = '{"color": %s,"weight": 3,"opacity": 1.0}' % keystring
			return string
	else:
		if element == 'Point':
			string1 = "{color: '#0078FF'}"
			string2 = '{radius: 2, fillOpacity: 0.85}'
			return string1,string2
		else:
			return '{"color": "#0078FF","weight": 3,"opacity": 1.0}'


# returns base option sets for a given feature type
def get_base_template(featuretype):
	if featuretype == 'Point':
		return {'radius': 2, 'fillOpacity': 0.85,"color": "#0078FF","zooms":False,"bounds":False}
	else:
		return {"color": "#0078FF","weight": 3,"opacity": 1.0,"zooms":False,"bounds":False}


# a list of dictionaries will be given for controlling options
# these can handle fields or raw values 
# if any feature other than color  needs to be changed a base dict 
# will be instanitated and over written with inputs that have been given
# this allows for hard stylling changes like at inputs or headers if you really want to
def safe_dict_options(optiondictrow,featuretype):
	# getting base feature type
	basedict = get_base_template(featuretype)

	# running option dictrow through opacity switch 
	# if featuretype is Point
	if featuretype == 'Point':
		optiondictrow = lint_opacity(optiondictrow)

	# iterating through each value in basedict overwriting 
	# for present values
	newdict = basedict
	for row in basedict.keys():
		try:
			value = optiondictrow[row]
			newdict[row] = value
		except KeyError:
			pass
	return newdict


# makes an entire block of javascript so that a geojson file is displayed
def make_block(filename,count,element,dictrow,text):
	if element == 'Point':
		# getting style string and creating zoom block from the dictrow
		string1,string2 = get_style_strings(element,dictrow)
		zoomblock = make_zoom_block(dictrow,element)	
		block = '''
$.getJSON('http://localhost:8000/%s',function(data) { addDataToMap%s(data,map); });
	function addDataToMap%s(data, map) {
		var dataLayer = L.geoJson(data, {
			style: function(feature) {
				return %s;
			},
		    pointToLayer: function(feature, latlng) {
		        return new L.CircleMarker(latlng, %s);
		    },
			onEachFeature: function(feature, layer) {            %s; 	
		            layer.bindPopup(popupText, {autoPan:false, maxHeight:500, maxWidth:350} ); 
	        }});
	    dataLayer.addTo(map);
		map.fitBounds(dataLayer.getBounds())
		%s
		};
		''' % (filename,count,count,string1,string2,text,zoomblock)

	else:
		# getting style string and creating zoom block from the dictrow
		string = get_style_strings(element,dictrow)
		zoomblock = make_zoom_block(dictrow,element)	
		block = '''
$.getJSON('http://localhost:8000/%s',function(data) { addDataToMap%s(data,map); });
	function addDataToMap%s(data, map) {
		var dataLayer = L.geoJson(data, {
			style: function(feature) {
				return %s
			},
			onEachFeature: function(feature, layer) {            %s; 	
		            layer.bindPopup(popupText, {autoPan:false, maxHeight:500, maxWidth:350} ); 
	        }});
	    dataLayer.addTo(map);
		map.fitBounds(dataLayer.getBounds())
		%s
		};''' % (filename,count,count,string,text,zoomblock)
	return block


# creates the zoom block which will be parsed into make_block
def make_zoom_block(dictrow,element):
	# analyzing dictrow 
	dictrow = safe_dict_options(dictrow,element)
	dictrow = analyze_dictrow(dictrow)
	
	# getting zoom bounds from dictionary row
	zoombounds = dictrow['zooms']
	boundsbool = dictrow['bounds']

	if zoombounds == False:
		return ''
	else:
		if not boundsbool == False:		
			zoomstring = '''
\t\tmap.on('dragend',function(e) {
\t\t	var outerbounds = [[map.getBounds()._southWest.lng,map.getBounds()._northEast.lat],[map.getBounds()._northEast.lng,map.getBounds()._southWest.lat]]
\t\t	var outerbounds = L.bounds(outerbounds[0],outerbounds[1]);
\t\t	dataLayer.eachLayer(function(layer) {
\t\t		if (((outerbounds.contains(layer.feature.properties['bounds']) == true)||(outerbounds.intersects(layer.feature.properties['bounds']) == true))&&((map.getZoom() >= %s)&&(map.getZoom() <= %s))) { 
\t\t			layer.addTo(map) 
\t\t			console.log('added')
\t\t		}
\t\t		else {
\t\t			console.log('eadadfa')
\t\t			if ( dataLayer.hasLayer(layer) == true ) {
\t\t				map.removeLayer(layer)
\t\t			}
\t\t		}
\t\t\t	})
\t\t\t\t});
\t\tmap.on('zoomend',function(e) {
\t\t	var outerbounds = [[map.getBounds()._southWest.lng,map.getBounds()._northEast.lat],[map.getBounds()._northEast.lng,map.getBounds()._southWest.lat]]
\t\t	var outerbounds = L.bounds(outerbounds[0],outerbounds[1]);
\t\t	dataLayer.eachLayer(function(layer) {
\t\t		if (((outerbounds.contains(layer.feature.properties['bounds']) == true)||(outerbounds.intersects(layer.feature.properties['bounds']) == true))&&((map.getZoom() >= %s)&&(map.getZoom() <= %s))) { 
\t\t			layer.addTo(map) 
\t\t			console.log('added')
\t\t		}
\t\t		else {
\t\t			if ( dataLayer.hasLayer(layer) == true ) {
\t\t				map.removeLayer(layer)
\t\t			}
\t\t		}
\t\t	})
\t\t\t\t});''' % (zoombounds[0],zoombounds[1],zoombounds[0],zoombounds[1])
		else:
			zoomstring = '''
\tmap.on('dragend',function(e) {
\t	dataLayer.eachLayer(function(layer) {
\t		if (((map.getZoom() >= %s)&&(map.getZoom() <= %s))) { 
\t			layer.addTo(map) 
\t			console.log('added')
\t		}
\t		else {
\t			if ( dataLayer.hasLayer(layer) == true ) {
\t				map.removeLayer(layer)
\t			}
\t		}
\t\t	})
\t\t\t});
\tmap.on('zoomend',function(e) {
\t	dataLayer.eachLayer(function(layer) {
\t		if (((map.getZoom() >= %s)&&(map.getZoom() <= %s))) { 
\t			layer.addTo(map) 
\t			console.log('added')
\t		}
\t		else {
\t			if ( dataLayer.hasLayer(layer) == true ) {
\t				map.removeLayer(layer)
\t			}
\t		}
\t\t	})
\t\t\t});''' % (zoombounds[0],zoombounds[1],zoombounds[0],zoombounds[1])
	
	return zoomstring

# make bindings after color options were added
def make_bindings(headers,filename,count,dictrow,element):
	varblock = make_rows(headers)
	block = make_block(filename,count,element,dictrow,varblock)	
	return block


# given a list of file names and kwargs carried throughout returns a string of the function bindings for each element
# this function is where most of the hardcore logic happens to parse js correctly
def make_html(filenames):
	# instantiating string the main string block for the javascript block of html code
	total = make_starting_block()

	# iterating through each geojson filename
	count = 0
	for row in filenames:
		filename = row

		# reading in geojson file into memory
		with open(filename) as data_file:    
   			data = json.load(data_file)


		
		# getting the featuretype which will later dictate what javascript splices are needed
		if not row[-5:] == '.json':
			data = data['features']
			data = data[0]
		else:
			filename = str.split(filename,'.')[0] + '.geojson'

		featuretype = data['geometry']
		featuretype = featuretype['type']
		data = data['properties']
		dictrow = data.get('options',False)
   		# iterating through each header 
		headers = []
		for row in data:
			headers.append(str(row))

		# overwriting false dictrow
		if dictrow == False:
			dictrow = {}

		# creating block to be added to the total or constituent string block
		if featuretype == 'Point':
			binding = make_bindings(headers,filename,count,dictrow,featuretype)+'\n'
			total += binding
		else:
			binding = make_bindings(headers,filename,count,dictrow,featuretype)+'\n'
			total += binding	

		count += 1	

	return total + '\n</script>'

# collecting geojson files in a list 
def collect_geojsons():
	jsons=[]
	for dirpath, subdirs, files in os.walk(os.getcwd()):
	    for x in files:
	        if x.endswith(".geojson"):
	        	jsons.append(x)
	return jsons

# collecting geojson files in a list 
def collect_jsons():
	jsons=[]
	for dirpath, subdirs, files in os.walk(os.getcwd()):
	    for x in files:
	        if x.endswith(".json"):
	        	jsons.append(x)
	return jsons

# getting all filenames or mask filenames
def collect():
	geojsons = collect_geojsons()
	jsons = collect_jsons()
	newgeojsons = []
	for row in geojsons:
		ind = 0
		oldrow = row
		testval = str.split(row,'.')[0]
		for row in jsons:
			jsonval = str.split(row,'.')[0]
			if testval == jsonval:
				newval = row
				ind = 1
		if ind == 0:
			newgeojsons.append(oldrow)
		else:
			newgeojsons.append(newval)

	return newgeojsons

# writes the html file to a document then opens it up in safari (beware it will call a terminal command)
def open_instance(filename,chrome):
	if chrome == True:
		os.system("open -a 'Google Chrome' "+'http://localhost:8000/'+filename)
	else:
		os.system("open -a Safari "+filename)

# if you wish to use this in Jupyter Notebook simply 
# use this function with the returned url to display output
def show(url):
    return IFrame(url, width=400, height=400)

# this is the public api for style rows
# colorkey is a field that persists in all geojsons 
# that contains a hex string
# style rows is a list of dictionaries with at specific inputs
# that can relate to either a field in every feature or a hard value set
# for the entire geojson
def load(filenames,**kwargs):
	colorkey = False
	styledicts = False
	load_instances = False
	chrome = False
	iframe = False


	for key,value in kwargs.items():
		if key == 'colorkey':
			colorkey = value
		if key == 'styledicts':
			styledicts = value
		if key == 'load_instances':
			load_instances = value
		if key == 'chrome':
			chrome = value
		if key == 'iframe':
			iframe = value
		if key == 'width':
			width = value
		if key == 'height':
			height = value

	
	# getting the html block string 
	html = make_html(filenames)

	# writing html block to file

	p = Process(target=localhost_thing)
	p.start()

	port = str(8000)


	with open('index.html','w') as f:
		f.write(html.replace('8000',port))
	

	# logic for if the a() API is called
	# which will open the webpage written in Safari (or chrome)
	if iframe == True:
		return IFrame('http://localhost:%s/index.html' % 8000, width=width, height=height)
	elif load_instances == True:
		open_instance('index.html',chrome)
		

#cleans the current of geojson files (deletes them)
def cln():
	jsons = collect()	
	for row in jsons:
		try:
			os.remove(row)
			os.remove(str.split(row,'.')[0] + '.geojson')
		except:
			pass

# this is an API for development like enviroment
# it WILL open output in browseer and make hasty assumpitons
# that you want all geojsons to in the active directory to be written out
# that being said it can be called with no required arguments
def b(**kwargs):
	colorkey = False
	styledicts = False
	load_instances = True
	width = 800
	height = 400
	iframe = False
	for key,value in kwargs.items():
		if key == 'colorkey':
			colorkey = value
		if key == 'styledicts':
			styledicts = value
		if key == 'load_instances':
			load_instances = value
		if key == 'chrome':
			chrome = value
		if key == 'iframe':
			iframe = value
		if key == 'width':
			width = value
		if key == 'height':
			height = value


	filenames = collect()

	return load(filenames,colorkey=colorkey,styledicts=styledicts,load_instances=load_instances,iframe=iframe,width=width,height=height)


