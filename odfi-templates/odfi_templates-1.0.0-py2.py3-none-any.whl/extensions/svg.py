
import sys
import os
from os.path import basename
from os.path import dirname

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.util.compat import make_admonition
from sphinx.locale import _


from sphinx.util import logging
import logging


from xml.etree import ElementTree


class svg(nodes.Inline, nodes.Element):
	"""SVG Node"""



def visit_svg_node(self, node):

	if hasattr(node,'groupId'):

		## Find Group content in source
		ns = {'svg': 'http://www.w3.org/2000/svg'}
		svgDom = ElementTree.parse(node.source)
		svgRoot = svgDom.getroot()
		foundGroup = svgRoot.find(".//svg:g[@id='%s']" %(node.groupId),ns)
		foundGroup.set("x","0")
		foundGroup.set("y","0")
		foundGroup.set("transform","")

		## Find defs in source
		foundDefs = svgRoot.find(".//svg:defs",ns)

		## Find top most Y (lowest y) to set transformation to get the group back on top
		allwithy = foundGroup.findall(".//*[@y]")
		allwithx = allwithy

		## First calculate translation in X and Y to substract from all X/Y coordinates
		## Sort X list by most Right first
		## Sort Y list by most down first
		## Take last element as most left and most down
		mostRightFirst = sorted(allwithx,key=lambda n: float(n.get("x")),reverse=True)
		mostDownFirst  = sorted(allwithy,key=lambda n: float(n.get("y")),reverse=True)
		minX = float(mostRightFirst[-1].get("x"))
		minY = float(mostDownFirst[-1].get("y"))

		translateX = 0 if minX < 0 else minX
		translateY = 0 if minY < 0 else minY

		## From here translate all X/Y coordnates because we place back the group to 0/0
		## This way sizes are correct
		## Calculate all x+width and sort descending
		allXAndWidth = filter(lambda elt: elt.get("x")!=None and elt.get("width")!=None,allwithx)
		allMostRightCoordinates = sorted(map(lambda elt: float(elt.get("x")) - translateX + float(elt.get("width")), allXAndWidth),reverse=True)

		allYAndHeight = filter(lambda elt: elt.get("y")!=None and elt.get("height")!=None,allwithy)
		allMostDownCoordinates = sorted(map(lambda elt: float(elt.get("y"))  - translateY + float(elt.get("height")), allYAndHeight),reverse=True)

		
		maxX = allMostRightCoordinates[0]
		maxY = allMostDownCoordinates[0]
		#print("Most Right is ",allMostRightCoordinates[0])
		#print("Most Down is ",allMostRightCoordinates[0])

		## Max X is the most right + width
		## Max Y is the most down + height
		#maxX = float(mostRightFirst[0].get("x")) +  float(mostRightFirst[0].get("width")) 
		#maxY = float(mostDownFirst[0].get("y")) +  float(mostDownFirst[0].get("height"))

		
		## Modify Properties of SVG now
		################################

		## Create new SVG 
		newSvg = ElementTree.fromstring('<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg version="1.1"  xmlns="http://www.w3.org/2000/svg"></svg>')
		

		## View Box is 0 0 maxX maxY
		viewBox = "0 0 %s %s" % (maxX,maxY) 
		newSvg.set("viewBox",viewBox)

		#ally = map(lambda n: float(n.get("y")),allwidthy)
		#allx = map(lambda n: float(n.get("x")),allwidthx)
		#allwidth = map(lambda n: float(n.get("width")),allwidthx)
		#allheight = map(lambda n: float(n.get("height")),allwidthx)
		#miny = min(map(lambda n: float(n.get("y")),allwidthy))
		#minx = min(map(lambda n: float(n.get("x")),allwidthx))

		print("Found Min y 2: ",minY)
		print("Found Min x 2: ",minX)
		print("Found Max y 2: ",maxY)
		print("Found Max x 2: ",maxX)

		## Translate Group
		foundGroup.set("transform","translate(%s,%s)" % (-translateX,-translateY))
	

		##  add group to it
		newSvg.insert(0,foundGroup)

		## Add Defs
		newSvg.insert(0,foundDefs)

		
		ElementTree.register_namespace("","http://www.w3.org/2000/svg")
		ElementTree.register_namespace("xlink","http://www.w3.org/1999/xlink")
		
		str = ElementTree.tostring(newSvg, encoding='utf8', method='xml').decode("utf-8") 
		#print("Found svg: ",str)

		## DIV Container and Style
		####################
		targetStyle= node.style if hasattr(node,'style') else ""

		if hasattr(node,'style_center'):
			targetStyle = targetStyle + ";margin-left:auto;margin-right:auto"

		## Set Container Div width provided style if defined
		self.body.append('<div style="%s">' % (targetStyle))
		self.body.append(str)
		self.body.append('</div>')

	else:
		with open(node.source) as f: s = f.read()
		self.body.append(s)

def depart_svg_node(self, node):
	pass

class OdfiSVGDirective(Directive):

  
	has_content = True
	required_arguments = 2 
	optional_arguments = 64
           

	def run(self):

		print('Running ODFI SVG Directive')
		print( self.arguments)
		print( self.options)
		
		env = self.state.document.settings.env
		source = self.state_machine.input_lines.source(self.lineno - self.state_machine.input_offset - 1)

		
		#logger = logging.getLogger(__name__)
		#logger.info('Running ODFI SVG Directive')

		## Get File
		if not "file" in self.arguments: 
			return [nodes.error(None, nodes.paragraph(text = "Unable to Load SVG at %s:%d: file argument not defined" % (basename(source), self.lineno))) ]
		
		## Get File name relative to local source
		fileName = self.arguments[(self.arguments.index('file') +1)]
		sourceDirectory = dirname(source)
		sourceSVG  = os.path.normpath(sourceDirectory+"/"+fileName)

		if os.path.exists(sourceSVG):
			print("SVG File is at",sourceSVG)
		else:
			return [nodes.error(None, nodes.paragraph(text = "Unable to Load SVG at %s:%d: file %s does not exist" % (basename(source), self.lineno,sourceSVG))) ]

		
		## Create SVG Node
		targetid = "svg-%d" % env.new_serialno('svg')
		svgNode = svg()
		svgNode.source = sourceSVG
	
		## Set Target Group Id if necessary
		if "gid" in self.arguments: 
			print('Found Elementid')
			svgNode.groupId = self.arguments[(self.arguments.index('gid') +1)]

		

		## Style Arguments
		######################
		## Set Style if necessary
		if "style" in self.arguments: 
			svgNode.style = self.arguments[(self.arguments.index('style') +1)].replace('"',"").replace("'","")

		if "align" in self.arguments and self.arguments[(self.arguments.index('align') +1)] == "center":
			svgNode.style_center = True

		## Animation Arguments
		######################

		return [svgNode]


def setup(app):

	"""html=(visit_OdfiSVG_node, depart_OdfiSVG_node)"""
	app.add_node(svg, html=(visit_svg_node, depart_svg_node))
	app.add_directive('odfisvg',OdfiSVGDirective)
	return {'version': '0.1'}



