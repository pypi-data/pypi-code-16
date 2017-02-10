import os
import json
from multiprocessing import Process
import future
import sys
from IPython.display import IFrame
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

# makes the starting block
def start_block(optionsdict):
	try:
		long,lat = optionsdict['firstbound']
	except:
		lat,long = [41.9,-86.90]

	block = '''
<!doctype html>
<html>
<head>
    <title>Many polygons with geojson-vt on Leaflet</title>
    <meta charset="utf-8">

    <style>
        html, body {
            height: 100%;
            padding: 0;
            margin: 0;
            background: rgb(14, 21, 30);
            height: 100%;
            font-family: Tahoma, Geneva, Verdana, sans-serif;
            font-size:12px;
            color:#808080;
        }

        #map {
            position: absolute;
            height: 100%;
            width: 100%;
            background-color: #333;
        }
    </style>
   

</head>
<body>
    <div id="map"></div>
	<script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>

    <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.css" />
    <script src="http://cdn.leafletjs.com/leaflet-0.7.2/leaflet.js"></script>
    <script src="http://www.sumbera.com/gist/js/vt/geojson-vt-dev.js"></script>
    <script src="http://www.sumbera.com/gist/js/leaflet/canvas/L.CanvasTiles.js"></script>

    <script src="http://www.sumbera.com/gist/data/CZDistricts.js"></script> 


    <script>
'''  

	block2 = '''
        var leafletMap = L.map('map').setView([%s,%s], 12);
       	mapLink = '<a href="http://openstreetmap.org">OpenStreetMap</a>';
        L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			attribution: '&copy; ' + mapLink + ' Contributors',maxZoom: 15,}).addTo(leafletMap);


        var tileOptions = {
            maxZoom: 20,  // max zoom to preserve detail on
            tolerance: 5, // simplification tolerance (higher means simpler)
            extent: 4096, // tile extent (both width and height)
            buffer: 64,   // tile buffer on each side
            debug: 0,      // logging level (0 to disable, 1 or 2)

            indexMaxZoom: 0,        // max zoom in the initial tile index
            indexMaxPoints: 1000000, // max number of points per tile in the index
        };
        //-------------------------------------------------
''' % (lat,long)
	block = block + block2
	return block

def create_style_block(optionsdict):
	zoomblock,bothbool = create_zoomblock(optionsdict)
	try:
		color = optionsdict['color']
	except:
		color = 'COLORKEY'
	styleblock = '''\n
				%s
				if ( feature.tags.hasOwnProperty('%s') == false ) {
					ctx.strokeStyle = feature.tags['color'];
					ctx.fillStyle = feature.tags['color'];
				}
				else { 
					ctx.fillStyle = feature.tags['%s'];
					ctx.strokeStyle = feature.tags['%s'];
				} 
	''' % (zoomblock,color,color,color)
	return styleblock,bothbool

def get_options(optionsdict,properties):
	try:
		color = optionsdict['color']
		for row in properties.keys():
			if str(properties[row]) == str(color):
				color = row
	except:
		color = 'color'
	try:
		zooms = optionsdict['zooms']
		for row in properties.keys():
			if str(properties[row]) == str(zooms):
				zooms = row
	except:
		zooms = 'zooms'
	return color,zooms


def create_zoomblock(optionsdict):
	try:
		optionsdict['zooms']
		zoombool = True
	except:
		zoombool = False
	try:
		boundsfield = optionsdict['bounds']
		boundsbool = True
	except:
		boundsbool = False
	bothbool = False
	if boundsbool == False and zoombool == True:
		zoomblock = '''
						var zoomlevel = leafletMap.getZoom();
						var zoom1 = feature.tags['%s'];
						var zoom2 = feature.tags['%s'];
						var displaybool = false;
						if ((zoom1 <= zoomlevel)&&(zoom2 >= zoomlevel)) {
							var displaybool = true;
						};
					''' % (optionsdict['zooms'][0],optionsdict['zooms'][1])
	elif boundsbool == True and zoombool == True:

		zoomblock = '''
						var zoomlevel = leafletMap.getZoom();
						var zoom1 = feature.tags['%s'];
						var zoom2 = feature.tags['%s'];
						var displaybool = false;
						var outerbounds = [[leafletMap.getBounds()._southWest.lng,leafletMap.getBounds()._northEast.lat],[leafletMap.getBounds()._northEast.lng,leafletMap.getBounds()._southWest.lat]]		
						var outerbounds = L.bounds(outerbounds[0],outerbounds[1]);
						if (((outerbounds.contains(feature.tags['%s']) == true)||(outerbounds.intersects(feature.tags['bounds']) == true))&&((zoomlevel >= zoom1)&&(zoomlevel <= zoom2))) { 
							var displaybool = true;
						};
					''' % (optionsdict['zooms'][0],optionsdict['zooms'][1],boundsfield)
		bothbool = True
		
	else:
		bothbool = False
		zoomblock = '''
								var displaybool = true;\n
'''
	return zoomblock,bothbool

def shift_middle(middleblock):
	middleblock = str.split(middleblock,'\n')
	middleblock = ['\t\t'+row for row in middleblock]
	middleblock = '\n'.join(middleblock)
	return middleblock


# makes each block filename
def make_block(filename,maskdict,count):
	# analyzing mask dict
	if not maskdict == False:

		filetype = maskdict['geometry']['type']
		optionsdict = maskdict['properties']['options']

		styleblock,zoombool = create_style_block(optionsdict)

		shit = '''function colorizeFeatures(data) {
				var counter = 0;
				for (var i = 0; i < data.features.length; i++) {
				if ( data.features[i].properties.hasOwnProperty('color') == false ) {
					data.features[i].properties.color = "hsl(" + 360 * Math.random() + ", 50%, 50%)";
					counter += data.features[i].geometry.coordinates[0].length;
						}
					}
				return counter;
			}'''
		middle =  '''\n
					for (var i = 0; i < features.length; i++) {
						var feature = features[i],
							type = feature.type;
				
				
						
						%s 
          	
						if (displaybool == true) {     	
			
							// ctx.fillStyle = feature.tags.color ? feature.tags.color : 'rgba(255,0,0,0.05)';
							ctx.beginPath();

							for (var j = 0; j < feature.geometry.length; j++) {
								var geom = feature.geometry[j];
								ctx.lineWidth = 3;
								if (type === 1) {
								  var x = geom[0] / extent * 256;
								  var y = geom[1] / extent * 256;
								  ctx.arc(x + pad, y + pad, 2, 0, 2 * Math.PI, false);
								  ctx.closePath()
								  ctx.fill()
								  //continue;
								}

								for (var k = 0; k < geom.length; k++) {
									var p = geom[k];
									var extent = 4096;
					   
									var x = p[0] / extent * 256;
									var y = p[1] / extent * 256;
									if (k) ctx.lineTo(x  + pad, y   + pad);
									else ctx.moveTo(x  + pad, y  + pad);
								}
							}

							if (type === 3 || type === 1) ctx.fill('evenodd');
							ctx.stroke();
						}
					}
				});
''' % (styleblock)
		if zoombool == True:
			middle = shift_middle(str(middle).encode('utf-8'))
			potential = '''\n
					var featurezero = features[0]
					var tileezoomlevel1 = featurezero.tags['ZOOMKEY1'];
					var tileezoomlevel2 = featurezero.tags['ZOOMKEY2'];
					var zoomlevel = leafletMap.getZoom();
					if ((zoomlevel >= tileezoomlevel1)&&(zoomlevel <= tileezoomlevel2)) {
						colorizeFeatures(data);
						leafletMap.on('zoomend',function(e) {						
							%s
						leafletMap.on('dragend',function(e) {						
							%s
					};

''' % (middle,middle)
		else:
			middle = middle.replace('});','')
			middle = '''\n\t\t\t\tcolorizeFeatures(data);\n''' + middle

			potential = middle
		block = '''\n
		$.getJSON('http://localhost:8000/%s',function(data) { addDataToMap(data,map); });
			function addDataToMap(data, map) {
				var tileIndex = geojsonvt(data, tileOptions);

				%s

	  
				var tileLayer = L.canvasTiles()
							  .params({ debug: false, padding: 5 })
							  .drawing(drawingOnCanvas)
				   
	 
				var pad = 0;

				tileLayer.addTo(leafletMap);
  
		
				function drawingOnCanvas(canvasOverlay, params) {

					var bounds = params.bounds;
					params.tilePoint.z = params.zoom;

					var ctx = params.canvas.getContext('2d');
					ctx.globalCompositeOperation = 'source-over';



					var tile = tileIndex.getTile(params.tilePoint.z, params.tilePoint.x, params.tilePoint.y);
					if (!tile) {
						return;
					}
					ctx.clearRect(0, 0, params.canvas.width, params.canvas.height);

					var features = tile.features;
					%s	
				};
				};

				
''' % (filename,shit,potential)
	else:
		shit = '''function colorizeFeatures(data) {
				var counter = 0;
				for (var i = 0; i < data.features.length; i++) {
				if ( data.features[i].properties.hasOwnProperty('color') == false ) {
					data.features[i].properties.color = "hsl(" + 360 * Math.random() + ", 50%, 50%)";
					counter += data.features[i].geometry.coordinates[0].length;
						}
					}
				return counter;
			}'''
		block = '''\n
		$.getJSON('http://localhost:8000/%s',function(data) { addDataToMap0(data,map); });
			function addDataToMap%s(data, map) {
				var tileIndex = geojsonvt(data, tileOptions);

				%s

				colorizeFeatures(data);
	  
				var tileLayer%s = L.canvasTiles()
							  .params({ debug: false, padding: 5 })
							  .drawing(drawingOnCanvas%s)
				   
	 
				var pad = 0;

				tileLayer%s.addTo(leafletMap);
  
		
				function drawingOnCanvas%s(canvasOverlay, params) {

					var bounds = params.bounds;
					params.tilePoint.z = params.zoom;

					var ctx = params.canvas.getContext('2d');
					ctx.globalCompositeOperation = 'source-over';



					var tile = tileIndex.getTile(params.tilePoint.z, params.tilePoint.x, params.tilePoint.y);
					if (!tile) {
						return;
					}
					ctx.clearRect(0, 0, params.canvas.width, params.canvas.height);

					var features = tile.features;
			



					for (var i = 0; i < features.length; i++) {
						var feature = features[i],
							type = feature.type;
				
				
						if ( feature.tags.hasOwnProperty('zooms') == false ) {
							var displaybool = true;
						}
						else { 
							var zoomlevel = leafletMap.getZoom();
							zooms = feature.tags['zooms']
							var zoom1 = zooms[0];
							var zoom2 = zooms[1];
							var displaybool = false;
							if ((zoom1 <= zoomlevel)&&(zoom2 >= zoomlevel)) {
								var displaybool = true;
							}	
						} 
				
						if (displaybool == true) {     	
							if ( feature.tags.hasOwnProperty('color') == false ) {
								ctx.strokeStyle = 'red';
							}
							else { 
								ctx.strokeStyle = feature.tags.color;
								ctx.fillStyle = feature.tags.color;

							}
							ctx.fillStyle = feature.tags.color ? feature.tags.color : 'rgba(255,0,0,0.05)';
							ctx.beginPath();

							for (var j = 0; j < feature.geometry.length; j++) {
								var geom = feature.geometry[j];
								ctx.lineWidth = 3;
								if (type === 1) {
								  var x = geom[0] / extent * 256;
								  var y = geom[1] / extent * 256;
								  ctx.arc(x + pad, y + pad, 2, 0, 2 * Math.PI, false);
								  ctx.closePath()
								  ctx.fill()
								  //continue;
								}

								for (var k = 0; k < geom.length; k++) {
									var p = geom[k];
									var extent = 4096;
					   
									var x = p[0] / extent * 256;
									var y = p[1] / extent * 256;
									if (k) ctx.lineTo(x  + pad, y   + pad);
									else ctx.moveTo(x  + pad, y  + pad);
								}
							}

							if (type === 3 || type === 1) ctx.fill('evenodd');
							ctx.stroke();
						}
					}
				};
				};

				
''' % (filename,count,shit,count,count,count,count)
	return block

# gets the end block of the html
def end_block():
	block = '''\n

    </script>
</body>
</html>
'''

	return block

def read_json(filename):
	with open(filename,'rb') as f:
		return json.load(f)

# getting first options dictionary
def get_first_optionsdict(filenames):
	for row in filenames:
		if row[-5:] == '.json':
			dictfile = read_json(str(row))
			firstoptionsdict = dictfile['properties']['options']
			try:
				firstoptionsdict['firstbound']
				return firstoptionsdict
			except:
				pass
	return {}
# writes the html code associated with parsing and reutrning
# html string
def make_html(filenames):
	firstopt = get_first_optionsdict(filenames)
	total = start_block(firstopt)
	count = 0
	for filename in filenames:
		maskdict = False
		if filename[-5:] == '.json':
			maskdict = read_json(filename)
		filename = filename.replace('.json','.geojson')
		block = make_block(filename,maskdict,count)

		count += 1
		total += block
	total += end_block()
	return total


def read_json(filename):
	with open(filename,'rb') as f:
		return json.load(f)

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

#cleans the current of geojson files (deletes them)
def cln():
	jsons = collect()	
	for row in jsons:
		try:
			os.remove(row)
			os.remove(str.split(row,'.')[0] + '.geojson')
		except:
			pass

# main function api
def a(iframe=False,height=400,width=800):
	# getting filenames
	filenames = collect()
	
	# getting html block
	htmlblock = make_html(filenames)
	p = Process(target=localhost_thing)
	p.start()
	

	# writng to file
	with open('index.html','w') as f:
		f.write(htmlblock)

	if iframe == True:
		 return IFrame('http://localhost:8000/index.html', width=width, height=height)
	else:
		os.system("open -a Safari index.html")

