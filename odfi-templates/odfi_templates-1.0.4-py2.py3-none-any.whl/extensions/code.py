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

class Code(nodes.Inline, nodes.Element):
	"""SVG Node"""



def visit_code_node(self, node):
	self.body.append('<pre>')
	self.body.append('<code>')
	self.body.append("\n".join(node.content))

def depart_code_node(self, node):
	self.body.append('</code>')
	self.body.append('</pre>')



class OdfiCodeDirective(Directive):
	has_content = True

	def run(self):

		codeNode = Code()
		codeNode.content = self.content
		print(self.content)

		return [codeNode]

def setup(app):

	"""html=(visit_OdfiSVG_node, depart_OdfiSVG_node)"""
	app.add_node(Code, html=(visit_code_node, depart_code_node))
	app.add_directive('odfi.code',OdfiCodeDirective)
	return {'version': '1.0.0'}