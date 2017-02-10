#!/usr/bin/env python

from metabolicmodel import MetabolicModel
import sys
import os

try:
    filename = sys.argv[1]
except IndexError:
    print "Error: No filename given."
    print "Usage is\n    " + os.path.basename(sys.argv[0]), "<reaction file>"
    exit()

model = MetabolicModel()
try:
    model.addReactionsFromFile(filename)
except IOError, strerror:
    print ("An error occurred while trying to read file %s:" %
           os.path.basename(filename))
    print strerror
    exit()
except SyntaxError, strerror:
    print ("Error in reaction file %s:" %
           os.path.basename(filename))
    print strerror
    exit()
print "\n".join(sorted(model.getMetaboliteNames()))
