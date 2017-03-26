class Primitive:
	'''
		https://cprogrammer1994.github.io/ModernGL/Primitive.html
	'''

	def __init__(self):
		'''
		'''

TRIANGLES = Primitive()
TRIANGLE_STRIP = Primitive()
TRIANGLE_FAN = Primitive()
LINES = Primitive()
LINE_STRIP = Primitive()
LINE_LOOP = Primitive()
POINTS = Primitive()
LINE_STRIP_ADJACENCY = Primitive()
LINES_ADJACENCY = Primitive()
TRIANGLE_STRIP_ADJACENCY = Primitive()
TRIANGLES_ADJACENCY = Primitive()

class Buffer:
	'''
		https://cprogrammer1994.github.io/ModernGL/Buffer.html
	'''

	def __init__(self, data, reserve = 0, dynamic = False):
		'''
		'''

class Program:
	'''
		https://cprogrammer1994.github.io/ModernGL/Program.html
	'''

	def __init__(self, shaders, varyings = None):
		'''
		'''

class Shader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

class VertexShader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

	def __init__(self, source):
		'''
		'''

class FragmentShader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

	def __init__(self, source):
		'''
		'''

class GeometryShader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

	def __init__(self, source):
		'''
		'''

class TessEvaluationShader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

	def __init__(self, source):
		'''
		'''

class TessControlShader:
	'''
		https://cprogrammer1994.github.io/ModernGL/Shader.html
	'''

	def __init__(self, source):
		'''
		'''

class VertexArray:
	'''
		https://cprogrammer1994.github.io/ModernGL/VertexArray.html
	'''

	def __init(self, program, content, index_buffer = None, skip_errors = False):
		'''
		'''

	def render(self, mode, vertices, first = 0, instances = 1):
		'''
		'''

class SimpleVertexArray:
	'''
		https://cprogrammer1994.github.io/ModernGL/VertexArray.html
	'''

	def __init__(self, program, buffer, format, attributes, index_buffer = None, skip_errors = False):
		'''
		'''

	def render(self, mode, vertices, first = 0, instances = 1):
		'''
		'''

class Framebuffer:
	'''
		https://cprogrammer1994.github.io/ModernGL/Framebuffer.html
	'''

	def __init__(self, attachments):
		'''
		'''

class Renderbuffer:
	'''
		https://cprogrammer1994.github.io/ModernGL/Renderbuffer.html
	'''

	def __init__(self, size, components, floats = True):
		'''
		'''

class DepthRenderbuffer:
	'''
		https://cprogrammer1994.github.io/ModernGL/DepthRenderbuffer.html
	'''

	def __init__(self, size):
		'''
		'''

class Texture:
	'''
		https://cprogrammer1994.github.io/ModernGL/Texture.html
	'''

	def __init__(self, size, components, data = None, floats = False):
		'''
		'''

class DepthTexture:
	'''
		https://cprogrammer1994.github.io/ModernGL/DepthTexture.html
	'''

	def __init__(self, size, data = None):
		'''
		'''

class MultisampleRenderbuffer:
	'''
		https://cprogrammer1994.github.io/ModernGL/MultisampleRenderbuffer.html
	'''

class MultisampleTexture:
	'''
		https://cprogrammer1994.github.io/ModernGL/MultisampleTexture.html
	'''

class Context:
	'''
		https://cprogrammer1994.github.io/ModernGL/Context.html
	'''

	def __init__(self):
		'''
		'''

		self.Buffer = Buffer
		self.Program = Program
		self.Shader = Shader
		self.VertexShader = VertexShader
		self.FragmentShader = FragmentShader
		self.GeometryShader = GeometryShader
		self.TessEvaluationShader = TessEvaluationShader
		self.TessControlShader = TessControlShader
		self.VertexArray = VertexArray
		self.SimpleVertexArray = SimpleVertexArray
		self.Framebuffer = Framebuffer
		self.Renderbuffer = Renderbuffer
		self.Texture = Texture
		self.DepthRenderbuffer = DepthRenderbuffer
		self.DepthTexture = DepthTexture
		self.MultisampleRenderbuffer = MultisampleRenderbuffer
		self.MultisampleTexture = MultisampleTexture

	def clear(self, r = 0, g = 0, b = 0, a = 0):
		'''
		'''

def create_context():
	'''
		https://cprogrammer1994.github.io/ModernGL/ModernGL.html#ModernGL.create_context
	'''

	return Context()

def create_standalone_context():
	'''
		https://cprogrammer1994.github.io/ModernGL/ModernGL.html#ModernGL.create_standalone_context
	'''

	return Context()
