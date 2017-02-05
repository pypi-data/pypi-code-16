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
import numpy
import unittest

import timetools.synchronization.compliance.analysis as sca


class TestAnalysis(unittest.TestCase):
    
    def testMask0 (self):
        # There should be no exceptions from this call
        thisMask = sca.Mask([])
        
    
    def testMask1 (self):
        thisMask = sca.Mask([( [0.0], [10.0] )])
        
        # The signal exceeds the mask bound so the evaluation should fail
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0))
        
        self.assertFalse(thisMask.evaluate(signal), 'Mask (1) bound test failed')
        
        
    def testMask2 (self):
        thisMask = sca.Mask([( [0.0], [12.0] )])
        
        # The signal is equal to the mask bounds so the evaluation should pass
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0))
        
        self.assertTrue(thisMask.evaluate(signal), 'Mask (2) bound test failed')


    def testMask3 (self):
        thisMask = sca.Mask([( [0.0, 10.0], [10.0] )])
        
        # The signal is <= the mask bound for the specified interval so the evaluation should pass
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0))
        
        self.assertTrue(thisMask.evaluate(signal), 'Mask (3) bound test failed')


    def testMask4 (self):
        thisMask = sca.Mask([( [0.0, 10.0], [10.0], [-1.0] )])
        
        # The signal >= the mask bound on the lower bound side and <= the mask bound on the 
        # upper bound side over the mask interval so the evaluation should pass
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0))
        
        self.assertTrue(thisMask.evaluate(signal), 'Mask (4) bound test failed')


    def testMask5 (self):
        thisMask = sca.Mask([( [0.0, 10.0], ([10.0], [0.5]) )])
        
        # The signal >= the mask bound on the lower bound side and <= the mask bound on the 
        # upper bound side over the mask interval so the evaluation should pass
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0))
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.plot(signal[0], signal[1], color='r')
        mpp.title('testMask5')
        
        self.assertTrue(thisMask.evaluate(signal), 'Mask (5) bound test failed')


    def testMask6 (self):
        thisMask = sca.Mask([( [0.0, 10.0], ([10.0], [0.5]) )])
        
        # The signal >= the mask bound on the upper bound side so the evaluation should fail
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0) + 10)
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.plot(signal[0], signal[1], color='r')
        mpp.title('testMask6')
        
        self.assertFalse(thisMask.evaluate(signal), 'Mask (6) bound test failed')


    def testMask7 (self):
        thisMask = sca.Mask([( [0.0, 10.0], ([5, 10.0], [0, 0.5]) )])
        
        # The signal >= the mask bound on the upper bound side so the evaluation should fail
        signal = (numpy.arange(0.0, 12.0), numpy.arange(0.0, 12.0) + 10)
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.plot(signal[0], signal[1], color='r')
        mpp.title('testMask7')
        
        self.assertFalse(thisMask.evaluate(signal), 'Mask (7) bound test failed')


    def testPlotMask1 (self):
        thisMask = sca.Mask([( [0.0, 10.0], [10.0] ), ( [10, 20], [0.0, 1.0] ), ( [20.0, 30.0], [20.0] ), ( [30.0, 40.0], [170, -8.0, 0.1] )])
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.title(self.testPlotMask1.__name__)
        
        mpp.ylim( (0, 30) )


    def testPlotMask2 (self):
        thisMask = sca.Mask([( [0.0, 10.0], [10.0] ), ( [10, 20], [0.0, 1.0] ), ( [20.0, 30.0], [20.0] ), ( [30.0, 40.0], [170, -8.0, 0.1])])
        
        figureHandle = mpp.figure()
        # Test adding line properties
        thisMask.addToPlot(figureHandle.number, linewidth=3, linestyle='-', color='r')
        mpp.title(self.testPlotMask2.__name__)
        
        mpp.ylim( (0, 30) )


    def testPlotMask3 (self):
        thisMask = sca.Mask([( [0.0, 10.0], [10.0], [-5.0] ), ( [10, 20], [0.0, 1.0], [5.0, -1.0] )])
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.title(self.testPlotMask3.__name__)
        
        mpp.ylim( (-20, 30) )


    def testPlotMask4 (self):
        thisMask = sca.Mask([( [0.0], [10.0] )])
        
        figureHandle = mpp.figure()
        thisMask.addToPlot(figureHandle.number)
        mpp.title(self.testPlotMask4.__name__)
        
        mpp.ylim( (0, 30) )


    def tearDown (self):
        if __name__ == "__main__":
            mpp.show()
        

if __name__ == "__main__":
    unittest.main()
    