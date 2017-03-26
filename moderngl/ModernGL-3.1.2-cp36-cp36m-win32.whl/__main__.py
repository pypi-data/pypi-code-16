import argparse

parser = argparse.ArgumentParser(prog = 'ModernGL')
parser.add_argument('-v', '--version', action = 'version', version = '%(prog)s 3.1.1')
args = parser.parse_args()

import ModernGL

ctx = ModernGL.create_standalone_context()

print('Vendor:', ctx.vendor)
print('Renderer:', ctx.renderer)
print('Version:', ctx.version)
