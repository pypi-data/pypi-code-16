#!/usr/bin/env python

import sys
from subprocess import Popen, PIPE

usage = """
DESCRIPTION: 
    List all the modules that contains a given word.

USAGE:
    To print this page:

        %s

    The expected syntax is:

        %s word
"""%(sys.argv[0], sys.argv[0])

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHT_PURPLE = '\033[94m'
PURPLE = '\033[95m'
END = '\033[0m'

n = len(sys.argv)

if (n == 1):
   print usage
else:
   w = sys.argv[1]
   print 80*"-"
   print "    List of modules containing the word: ", RED+w+END
   print 80*"-"

   p = Popen("/usr/bin/modulecmd tcsh av", shell=True, stdout=PIPE, stderr=PIPE)
   out, err = p.communicate()

   availModules = err.rstrip()

   i = 0
   for x in availModules.split():
       if w.lower() in x.lower():
          i += 1
          posB = x.lower().find(w.lower())
          posE = posB + len(w)
          print "%4d--> %s%s%s" %(i,x[0:posB],RED+x[posB:posE]+END,x[posE:])
   
   if (i == 0): print "    NONE"

   print 80*"-"
