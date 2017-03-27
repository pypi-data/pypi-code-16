#!/usr/bin/env python

'''display one or more EPICS PVs in a PyQt4 GUI window as a table'''

import os
import sys
import pvview

sys.path.insert(0, os.path.abspath('..'))

sys.argv.append( 'xxx:iso8601' )
#sys.argv.append( 'S:SRcurrentAI' )
#sys.argv.append( 'pj:message' )
pvview.main()
