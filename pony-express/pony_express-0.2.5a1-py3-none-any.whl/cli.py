"""
This module defines the command line interface to pony.
It provide facilities to properly end to end test the whole application. 
"""

import pony
import bag 
from bag import Bag, MongoConnectionInfo

import json
import os, sys
import time
from argparse import ArgumentParser, FileType

#meve the following in a proper module!
    
def charge(args):
    metadata = args.meta.read()
    connection_info = MongoConnectionInfo(args)
    
    try:
        pony.charge(db_connection_info = connection_info, json=metadata)
    except bag.YetInBag as ex:
        jobject = json.loads(metadata)
        try:
            del jobject['package']
        except:
            pass
        
        try:
            del jobject['__UNBOX_INSTRUCTIONS__']
        except:
            pass
            
        try:
            del jobject['__BOX_INSTRUCTIONS__']
        except:
            pass
                
        print ("""
charge operation failed: there is a conflicting package in the bag. 
  Metadata are:

  """ + json.dumps(jobject, indent=4))

def deliver(args):
    connection_info = MongoConnectionInfo(args)
    created_files, gr = pony.deliver_json(args.meta.read(), db_connection_info=connection_info)
    with open('.pony', 'w') as f:
        for fname in created_files:
            f.write(fname+'\n')
    
    return created_files, gr

def clear(args):
    with open('.pony', 'r') as f:
        for fname in f:
            os.remove(fname[:-1])


# setup the parser and its subparsers
parser = ArgumentParser( prog='pony')
subparsers = parser.add_subparsers()

# meta-informations source
parser.add_argument('--meta', type=FileType('r'), default='meta.json')
# mongo host
parser.add_argument('--mongo', default='localhost')
# mongo port
parser.add_argument('--port', type=int, default=27017)
# user
parser.add_argument('--user', default='')
# password
parser.add_argument('--pwd', default='')

charge_command_parser = subparsers.add_parser('charge')
charge_command_parser.set_defaults(func=charge, dest='func')

deliver_command_parser = subparsers.add_parser('deliver')
deliver_command_parser.set_defaults(func=deliver)

deliver_command_parser = subparsers.add_parser('clear')
deliver_command_parser.set_defaults(func=clear)