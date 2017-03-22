import argparse
from nullelf3 import *

parser = argparse.ArgumentParser(description='Test nullelf3.py')
parser.add_argument('--log',
                    const='warning',
                    default='warning',
                    nargs='?')
args = parser.parse_args()
logging.basicConfig(level=args.log.upper(), format='%(levelname)s:%(module)s:%(funcName)s: %(message)s')
#getattr(logging, args.log.upper())
logging.debug("THIS IS A DEBUG TEST MESSAGE")
e = elf('/bin/true')
print(e.entry)
