#
# Copyright 2017 Russell Smiley
#
# This file is part of timetools.
#
# timetools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# timetools is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with timetools.  If not, see <http://www.gnu.org/licenses/>.
#

import matplotlib.pyplot as mpp
import unittest

import timetools.synchronization.compliance.ituTG8261.eecOption1.networkWander as tscg8261eec1nw
import timetools.synchronization.compliance.ituTG8261.eecOption2.networkWander as tscg8261eec2nw
import timetools.synchronization.compliance.ituTG8261.deploymentCase2.wanderBudget as tscg8261dc2awb
import timetools.synchronization.compliance.ituTG8261.deploymentCase1.wanderBudget as tscg8261dc1wb


class TestItuTG8261 (unittest.TestCase):

    def testEecOption1MtieMask (self):
        thisMask = tscg8261eec1nw.mtieNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEecOption1MtieMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 100000) )
        mpp.ylim( (100, 10000) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
    

    def testEecOption1TdevMask (self):
        thisMask = tscg8261eec1nw.tdevNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEecOption1TdevMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.1, 100000) )
        mpp.ylim( (10, 1000) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
    

    def testEecOption2TdevMask (self):
        thisMask = tscg8261eec2nw.tdevNs
          
        figureHandle = mpp.figure()
        mpp.title(self.testEecOption2TdevMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 1000) )
        mpp.ylim( (1, 1000) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
    

    def testDc2AMrtieMask (self):
        thisMask = tscg8261dc2awb.case2A2048MrtieMicroseconds
          
        figureHandle = mpp.figure()
        mpp.title(self.testDc2AMrtieMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 1000) )
        mpp.ylim( (1, 100) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
    

    def testDc11544MrtieMask (self):
        thisMask = tscg8261dc1wb.case11544MrtieMicroseconds
          
        figureHandle = mpp.figure()
        mpp.title(self.testDc11544MrtieMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 100000) )
        mpp.ylim( (0.01, 10) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
    

    def testDc12048MrtieMask (self):
        thisMask = tscg8261dc1wb.case12048MrtieMicroseconds
          
        figureHandle = mpp.figure()
        mpp.title(self.testDc12048MrtieMask.__name__)
        # Set the plot limits before the mask plot so that it will figure out 
        # appropriate ranges in the absence of signal data
        mpp.xlim( (0.01, 1000) )
        mpp.ylim( (0.01, 10) )
        thisMask.addToPlot(figureHandle.number)
          
        mpp.yscale('log')
        mpp.xscale('log')
        mpp.grid(which='minor')
        

    def tearDown (self):
        if __name__ == "__main__":
            mpp.show()


if __name__ == "__main__":
    unittest.main()
    