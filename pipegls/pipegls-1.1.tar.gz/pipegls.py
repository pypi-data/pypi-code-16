from pipeleaflet import collect,cln
import pandas as pd
import os
import geohash
from nlgeojson import get_first_bounds,make_lines,make_points,make_polygons,make_blocks
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

def here():
 p = Process(target=localhost_thing)
 p.start()
 return []

# returns a bool that checks if a colorkey
# field exists
def test_colorkey(headers):
 for row in headers:
  if row == 'COLORKEY':
   return True
 return False

 
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
   newrow = """      var popupText = "<table><tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
  else:
   newrow = """      var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+"</td></tr>"; """ % (row1,row2)
  varblock.append(newrow)
  if row == headers[-1]:
   newrow = """      var popupText = popupText+ "<tr><th>%s: </th><td>" + feature.properties['%s']+</td></tr></table>"; """ % (row1,row2)
 total = ''
 for row in varblock:
  total += row 

 return total


# generates a popup for features
def generate_popup(popupstring,count,type):
 if type == 'points':
  typestring = ''
 else:
  typestring = '[0]'

 block = '''
 // Create a popup, but don't add it to the map yet.
 var popup = new mapboxgl.Popup({
  closeButton: false,
  closeOnClick: false
 });

 map.on('click', function(e) {
  var features = map.queryRenderedFeatures(e.point, { layers: ['%s'] });
  // Change the cursor style as a UI indicator.
  map.getCanvas().style.cursor = (features.length) ? 'pointer' : '';

  if (!features.length) {
   popup.remove();
   return;
  }

  var feature = features[0];

  // Populate the popup and set its coordinates
  // based on the feature found.
  %s
  popup.setLngLat(feature.geometry.coordinates%s)
   .setHTML(popupText)
   .addTo(map);
  });''' % (count,popupstring,typestring)
 return block

# given the filename type of data 
# the colorkey and the count of files youve arleady
# written returns the function block 
# corresponding to this specific dataset
def make_block(filename,type,colorkey,count,popupstring,latlng):
 linewidth = 2

 # generating popupstring 
 totalpopupstring = generate_popup(popupstring,'src' + str(count),type)

 if type == 'lines':
  block = '''
function wrap%s(map) {
 map.on('load',function () {
   $.getJSON('http://localhost:8000/%s',function(data1) { addDataToMap0(data1); });
    function addDataToMap0(data1) {

     // Mapbox GL JS Api - import segment
     var segment_src = map.addSource('src%s',{
       type:'geojson',
       data:data1
     });
     map.addLayer({
       'id': 'src%s',
       'type': 'line',
       'source': 'src%s',

       'paint': {
         'line-color': '%s',
         'line-width':%s
       }
       }
       );
       
       };
   });
 %s
};
 ''' % (count,filename,count,count,count,colorkey,linewidth,totalpopupstring)
 elif type == 'points':
  block = '''
function wrap%s(map) {
  map.on('load', function () {
    $.getJSON('http://localhost:8000/%s',function(data1) { addDataToMap0(data1); });
     function addDataToMap0(data1) {

      // Mapbox GL JS Api - import segment
      var segment_src = map.addSource('src%s',{
        type:'geojson',
        data:data1,
        maxzoom:14
      });
      map.addLayer({
        'id': 'src%s',
        'type': 'circle',
        'source': 'src%s',
        'source-layer': 'sf2010%s',
        'paint': {
          // make circles larger as the user zooms from z12 to z22
          'circle-radius': {
            'base': 4,
            'stops': [[12, 2], [22, 180]]
          },
          // color circles by ethnicity, using data-driven styles
          'circle-color': '%s'
          }
        }
      );
     }});
 %s
}
 ''' % (count,filename,count,count,count,count,colorkey,totalpopupstring)
 elif type == 'blocks':
  block = '''
function wrap%s(map) {
 map.on('load', function () {
   $.getJSON('http://localhost:8000/%s',function(data1) { addDataToMap0(data1); });
    function addDataToMap0(data1) {

     // Mapbox GL JS Api - import segment
     var segment_src = map.addSource('src%s',{
       type:'geojson',
       data:data1
     });
     map.addLayer({
       'id': 'src%s',
       'type': 'fill',
       'source': 'src%s',
       'source-layer': 'sf2010%s',
       'paint': {
         // color circles by ethnicity, using data-driven styles
         'fill-color': '%s',
         'fill-opacity': 0.7,

         },
       
      }
     );
    }});
  %s 
}
''' % (count,filename,count,count,count,count,colorkey,totalpopupstring)


 elif type == 'polygons': block = '''
function wrap%s(map) {
 map.on('load', function () {
   $.getJSON('http://localhost:8000/%s',function(data1) { addDataToMap0(data1); });
    function addDataToMap0(data1) {

     // Mapbox GL JS Api - import segment
     var segment_src = map.addSource('src%s',{
       type:'geojson',
       data:data1
     });
     map.addLayer({
       'id': 'src%s',
       'type': 'fill',
       'source': 'src%s',
       'source-layer': 'sf2010%s',
       'paint': {
         // color circles by ethnicity, using data-driven styles
         'fill-color': '%s',
         'fill-opacity': 0.5,
         'fill-outline-color':'black'

         },
       
      }
     );
    }});
  %s 
}
''' % (count,filename,count,count,count,count,colorkey,totalpopupstring)
 return block




# wraps the make functions based on tehre 
# type given 
def make_type(data,filename,type):
 if type == 'points':
  make_points(data,filename)
 if type == 'blocks':
  make_blocks(data,filename)
 if type == 'lines':
  make_lines(data,filename)
 if type == 'polygons':
  make_polygons(data,filename)

# wraps a make operation to divide into several smaller geojson
# files also accepts kwargs that go into 
# the make wrappers
# current list is the current list of file names
# that will continue to be appeneded to upon sent in
def make_wraps(data,type,basefilename,latlng,**kwargs):
 currentlist = False
 currentcount = 0
 for key,value in kwargs.items():
  if key == 'currentlist':
   currentlist = value
  if key == 'currentcount':
   currentcount = value

 basefilename = str.split(basefilename,'.')[0]
 if currentcount == False:
  count = 0
 else:
  count = currentcount
 # logiic for if a currrent list is given
 if not currentlist == False:
  newlist = currentlist
 else:
  newlist = []
 
 colorkeybool = test_colorkey(data.columns.values.tolist())
 stringrow = make_rows(data.columns.values.tolist())
 # if no colorkey exists this wraper function is
 # assumed that the geojson file is advantageous enough of a 
 # file size to be worth splitting 
 if colorkeybool == True:
  # grouping by colorkey to get splits
  for name,group in data.groupby('COLORKEY'): 
   group = group.reset_index()
   if count == 0:
    latlng = get_first_bounds(group,type,pipegl=True)
   newfilename = basefilename + str(count) + '.geojson'
   make_type(group,newfilename,type)
   block = make_block(newfilename,type,name,count,stringrow,latlng)
   newlist.append(block)
   count += 1
 return newlist,latlng

# make starting block
def make_starting(latlng):
 lat,long = latlng
 starting = '''
<html>
<head>
<meta charset=utf-8 />
<title>PipeLeaflet</title>
<meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
<script src="http://code.jquery.com/jquery-1.11.3.min.js"></script>

 <link rel="stylesheet" href="https://npmcdn.com/leaflet@1.0.0-rc.3/dist/leaflet.css" />
 <script src="https://api.tiles.mapbox.com/mapbox-gl-js/v0.15.0/mapbox-gl.js"></script>


 <div id="map"></div>


<style> #map {
 position: relative;
 width: auto;
 height: 650px;
 overflow:visible;
}
</style>

<style>
 body { margin:0; padding:0; }
</style>
<style> #map {
 position: relative;
 width: auto;
 height: 650px;
 overflow:visible;
}
</style>

<style>
body {
 font-family: Arial, sans-serif;
 background-size: cover;
 height: 100vh;
}

h1 {
 text-align: center;
 font-family: Tahoma, Arial, sans-serif;
 color: #06D85F;
 margin: 10px 0;
}

.box {
 width: 40%;
 margin: 0 auto;
 background: rgba(255,255,255,0.2);
 padding: 35px;
 border: 2px solid #fff;
 border-radius: 10px/10px;
 background-clip: padding-box;
 text-align: center;
}

.button {
 font-size: 1em;
 padding: 10px;
 color: #fff;
 border: 2px solid #06D85F;
 border-radius: 10px/10px;
 text-decoration: none;
 cursor: pointer;
}
.button:hover {
 background: #06D85F;
}

.overlay {
 position: fixed;
 top: 0;
 bottom: 0;
 left: 0;
 right: 0;
 background: rgba(0, 0, 0, 0.7);
 visibility: hidden;
 opacity: 0;
}
.overlay:target {
 visibility: visible;
 opacity: 1;
}

.mapboxgl-popup {
 margin: 20px auto;
 padding: 20px;
 background: #fff;
 border-radius: 5px;
 width: 40%;
 position: relative;
}

.mapboxgl-popup h2 {
 margin-top: 0;
 color: #333;
 font-family: Tahoma, Arial, sans-serif;
}
.mapboxgl-popup .close {
 position: absolute;
 top: 20px;
 right: 30px;
 font-size: 30px;
 font-weight: bold;
 text-decoration: none;
 color: #333;
}
.mapboxgl-popup .close:hover {
 color: #06D85F;
}
.mapboxgl-popup .content {
 max-height: 70%;
 overflow: auto;
}

</style>


<script>
'''
 a = '''\n
mapboxgl.accessToken = 'pk.eyJ1IjoicnNiYXVtYW5uIiwiYSI6IjdiOWEzZGIyMGNkOGY3NWQ4ZTBhN2Y5ZGU2Mzg2NDY2In0.jycgv7qwF8MMIWt4cT0RaQ';
var map = new mapboxgl.Map({
  container: 'map', // container id
  style: 'mapbox://styles/mapbox/dark-v8', //stylesheet location
  center: [%s, %s], // starting position
  zoom: 10 // starting zoom 
});''' % (lat,long)

 starting = starting + a
 return starting


def make_addseg(blocks):
 newlist = []
 for i in range(len(blocks)):
  newlist.append('\twrap%s(map);\n' % i)
 middle = ''.join(newlist)
 return 'function add(map) {\n' + middle + '\n}'

# writes html out 
# and opens up webpage in safari
def d(blocks,latlng,port):
 # getting started
 starting = make_starting(latlng)

 # getting total block
 totalblock = '\n'.join(blocks)

 # making function that executes the total block 
 # hopefully lazily
 wrapfunction = make_addseg(blocks[:get_maxfile()+1])

 # ending part
 ending = '''
\n
add(map);
</script>'''
 
 html = '\n'.join([starting,totalblock,wrapfunction,ending])
 with open('index.html','w') as f: f.write(html.replace('8000',port))

# makes a configuration dictionary
def make_config(data,type,**kwargs):
 current = []
 for key,value in kwargs.items():
  if key == 'current':
   current = value
 configdict = {'data':data,'type':str(type)}
 current.append(configdict)
 return current

def get_maxfile():
 newlist = []
 geojsons = collect()
 for row in geojsons:
  row = str.split(row,'.')[0]
  row = str.split(row,'_')[1]
  newlist.append(int(row))
 return max(newlist)


def make_map(configs,iframe=False,width=800,height=400):
 if not isinstance(configs[0],list):
  configs = [configs]
 a = []
 for data,type in configs:
  a = make_config(data,type,current=a)
 return eval_config(a,iframe=iframe,width=width,height=height)

# given a configuration dict compiles blocks for a specific basefile
# namm and then opens htmlm webpage
def eval_config(configdict,iframe=False,width=False,height=False):
 cln()
 count = 1
 latlng = 0
 for config in configdict:
  filename = 'basefile%s_.geojson' % count
  if count == 1:
   currentlist,latlng = make_wraps(config['data'],config['type'],filename,latlng,currentlist=[])
  else:
   oldcurrentlist = currentlist
   currentlist += make_wraps(config['data'],config['type'],filename,latlng,currentlist=currentlist,currentcount=get_maxfile()+1)[0]
  count += 1
 del configdict
 here()
 time.sleep(.3)

 # writiing and opening html
 d(currentlist,latlng,str(8000))

 if iframe == False:
  os.system("open -a Safari index.html")
  return ''
 else:
  return IFrame('http://localhost:%s/index.html' % port, width=width, height=height)



