
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

		## Find top most Y (lowest y) to set transformation to get the group back on top
		allwithy = foundGroup.findall(".//*[@y]")
		allwithx = allwithy
		ally = map(lambda n: float(n.get("y")),allwithy)
		allx = map(lambda n: float(n.get("x")),allwithx)
		allwith = map(lambda n: float(n.get("width")),allwithx)
		allheight = map(lambda n: float(n.get("height")),allwithx)

		miny = min(map(lambda n: float(n.get("y")),allwithy))
		minx = min(map(lambda n: float(n.get("x")),allwithx))

		print("Found Min y: ",miny)
		print("Found Min x: ",minx)

		foundGroup.set("transform","translate(-%s,-%s)" % (minx,miny))

		## Create new SVG and add group to it
		newSvg = ElementTree.fromstring('<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg version="1.1"  xmlns="http://www.w3.org/2000/svg"></svg>')
		newSvg.insert(0,foundGroup)
		newSvg.set("viewBox","0 0 50 50")
		ElementTree.register_namespace("","http://www.w3.org/2000/svg")
		str = ElementTree.tostring(newSvg, encoding='utf8', method='xml').decode("utf-8") 
		print("Found svg: ",str)

		## Set Container Div with provided style if defined
		if hasattr(node,'style'):
			self.body.append('<div style="%s">' % (node.style))
		else:
			self.body.append('<div style="width:50%">')

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

		## Set Style if necessary
		if "style" in self.arguments: 
			svgNode.style = self.arguments[(self.arguments.index('style') +1)].replace('"',"").replace("'","")

		return [svgNode]


def setup(app):

	"""html=(visit_OdfiSVG_node, depart_OdfiSVG_node)"""
	app.add_node(svg, html=(visit_svg_node, depart_svg_node))
	app.add_directive('odfisvg',OdfiSVGDirective)
	return {'version': '0.1'}



