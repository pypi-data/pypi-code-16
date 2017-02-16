from __future__ import absolute_import

from credulous import credulous

import argparse
import os

if __name__=='__main__':
	parser = argparse.ArgumentParser(
		description="""
	Tool for generating API credentials. Google API is supported.
	<scopes> is a json with a list of scope URL. The list should be under 
	scopes.google""")
	parser.add_argument('--secret',
		required=True,
	  help='Path to your client secret json file')
	parser.add_argument('scopes')
	args = parser.parse_args()

	credulous = credulous.Credulous(args.secret, args.scopes)
	credulous.authenticate()