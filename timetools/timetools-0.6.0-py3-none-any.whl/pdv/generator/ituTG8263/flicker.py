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

import math
import numpy
import numpy.random as nr


class Parameters:
    
    def __init__ (self, R = 2.5, M = 8, loadCycleDurationSeconds = 240, randomSeed = None):
        self.r = R
        self.m = M
        self.loadCycleDurationSeconds = loadCycleDurationSeconds
        
        self.randomGenerator = None
        if randomSeed is not None:
            # Assume randomSeed is a 32 bit integer
            self.randomGenerator = nr.RandomState(randomSeed)
        else:
            self.randomGenerator = nr.RandomState()
            
    
class Generator:
    
    def __init__ (self, parameters):
        self._r = parameters.r
        self._m = parameters.m
        self._loadCycleDurationSeconds = parameters.loadCycleDurationSeconds
        self._randomGenerator = parameters.randomGenerator
        
        self._phi, self._theta = computeFlickerCoefficients(self._r, self._m)
    
    
    def generate (self, timebaseSeconds):
        # Assume the timebase is uniformly sampled.
        # Assume that the r, m selection is constant for the duration of instantiation.
        
        # timebase must be monotonic
        assert(numpy.all(numpy.diff(timebaseSeconds) > 0))
        
        numberLoadNoiseSamples = self._computeNoiseSequenceLength(min(timebaseSeconds), max(timebaseSeconds))
        
        # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp5-10
        pn = self._randomGenerator.normal(size = numberLoadNoiseSamples)
        loadFlickerNoisePercent = computeLoadFlickerNoisePercent(pn, self._phi, self._theta)
        self._alpha, self._beta, self._rho = computeGammaCoefficients(loadFlickerNoisePercent)
        
        startTimesSeconds, stopTimesSeconds = self._calculateSegmentBounds(timebaseSeconds)
        
        assert(len(startTimesSeconds) == len(stopTimesSeconds))
        assert(len(startTimesSeconds) == len(self._alpha))
        
        pdvSeconds = numpy.zeros(timebaseSeconds.shape)
        for startTimeSeconds, stopTimeSeconds, alpha, beta, rho in zip(startTimesSeconds, stopTimesSeconds, self._alpha, self._beta, self._rho):
            
            thisCycleLogicalIndices = numpy.logical_and(timebaseSeconds >= startTimeSeconds, timebaseSeconds <= stopTimeSeconds)
            
            thisCycleTimebaseSeconds = timebaseSeconds[thisCycleLogicalIndices]
            numberCyclePdvSamples = len(thisCycleTimebaseSeconds)
            
            # numpy uses the k/theta and G.8263 uses alpha/beta notation for gamma distribution, so
            #   theta = 1 / beta
            #   k = alpha
            # but there is an error in G.8263 such that theta = beta
            #
            # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp10
            # Add back the static offset    
            pdvNoiseSeconds = self._randomGenerator.gamma(alpha, beta, size = numberCyclePdvSamples) + rho + 57.32e-6
            pdvSeconds[thisCycleLogicalIndices] = pdvNoiseSeconds
        
        return pdvSeconds
    
    
    def _calculateSegmentBounds (self, timebaseSeconds):
        numberSegments = self._computeNoiseSequenceLength(numpy.min(timebaseSeconds), numpy.max(timebaseSeconds))
        
        startTimesSeconds = numpy.zeros(numberSegments)
        stopTimesSeconds = numpy.zeros(numberSegments)
        # Assume the timebase is uniformly sampled
        startTimesSeconds[0] = timebaseSeconds[0]
        
        k = 0
        while k < len(startTimesSeconds):
            stopTimesSeconds[k] = startTimesSeconds[k] + self._loadCycleDurationSeconds
            
            if (stopTimesSeconds[k] < numpy.max(timebaseSeconds)) and ((k + 1) < len(startTimesSeconds)):
                startTimesSeconds[k + 1] = numpy.min(timebaseSeconds[timebaseSeconds > stopTimesSeconds[k]])
            
            k += 1
            
        return startTimesSeconds, stopTimesSeconds
    
    
    def _computeNoiseSequenceLength(self, minTime, maxTime):
        # Assume the timebase is uniformly sampled
        noiseCycleDuration = self._loadCycleDurationSeconds
        
        numberCycleSamples = math.floor((maxTime - minTime) / noiseCycleDuration) + 1
        
        return numberCycleSamples
            
            
def computeLoadFlickerNoisePercent (inputNoise, phi, theta):
    assert(len(phi) == len(theta))
    
    # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp6, Eq. I-3
    M = len(phi)
    N = len(inputNoise)
    Y = numpy.zeros( (M, N) )
    for n in range(1, N):
        Y[0, n] = (phi[0] * Y[0, (n - 1)]) + inputNoise[n]
        
        for m in range(1, M):
            firstTerm = phi[m] * Y[m, (n - 1)]
            secondTerm = Y[(m - 1), n]
            thirdTerm = -theta[m] * Y[(m - 1), (n - 1)]
            
            Y[m, n] = firstTerm + secondTerm + thirdTerm
    
    flickerNoise = Y[-1, :]
    
    minNoise = numpy.min(flickerNoise)
    maxNoise = numpy.max(flickerNoise)
    
    # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp7, Eq. I-6
    loadFlickerNoisePercent = 100 * (flickerNoise - minNoise) / (maxNoise - minNoise)
    
    assert(numpy.all(loadFlickerNoisePercent >= 0))
    assert(numpy.all(loadFlickerNoisePercent <= 100))
    
    return loadFlickerNoisePercent

    
def computeFlickerCoefficients (r, m):
    # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp6, Eq. I-5
    phi = numpy.zeros(m)
    phi[0] = 0.13
    
    omega = numpy.zeros(m)
    omega[0] = (1 - phi[0]) / math.sqrt(phi[0])
    omega[1:] = omega[0] / numpy.power(r, numpy.arange(1, m))
    
    mu = omega / r
    
    phi = 1 + mu * (mu - numpy.sqrt(numpy.power(mu, 2) + 4)) / 2
    
    theta = 1 + omega * (omega - numpy.sqrt(numpy.power(omega, 2) + 4)) / 2
    
    return phi, theta


def computeGammaCoefficients (networkLoadPercent):
    assert(numpy.all(networkLoadPercent >= 0))
    assert(numpy.all(networkLoadPercent <= 100))
    # Rec. ITU-T G.8263/Y.1363 (2012)/Amd.2 (05/2014), pp10
    # Table I.2, pp10
    alphaCoefficients = numpy.array([
                                     3.0302171048327E-10, 
                                     -9.7822643361772E-08, 
                                     1.1854660981753E-05, 
                                     -6.6624332958641E-04, 
                                     1.8713517871851E-02, 
                                     -1.4120879264166E-01, 
                                     1.3306420437613E+00
                                     ])
    betaCoefficients = numpy.array([
                                    -3.7527709385196E-16,
                                    1.2590219237780E-13,
                                    -1.6595170368502E-11,
                                    1.0886566230108E-09,
                                    -3.7186572402355E-08,
                                    5.9390899042069E-07,
                                    1.6110589771449E-06
                                    ])
    rhoCoefficients = numpy.array([
                                   1.0843935243576E-15,
                                   -2.8578719666972E-13,
                                   2.9508400604002E-11,
                                   -1.4410536532614E-09,
                                   3.3119857891960E-08,
                                   -2.9200865252098E-07,
                                   8.1781119355525E-07
                                   ])
    
    assert(len(alphaCoefficients) == 7)
    assert(len(betaCoefficients) == len(alphaCoefficients))
    assert(len(rhoCoefficients) == len(alphaCoefficients))

    alpha = numpy.zeros(networkLoadPercent.shape)
    beta = numpy.zeros(networkLoadPercent.shape)
    rho = numpy.zeros(networkLoadPercent.shape)
    
    clipIndices = networkLoadPercent > 99
    
    alpha[clipIndices] =  2.0132036140218E+01
    beta[clipIndices] = 2.96693980102245E-06
    rho[clipIndices] = 5.59439990063761E-05
    
    interpolateIndices = networkLoadPercent <= 99
    interpolatingNetworkLoad = networkLoadPercent[interpolateIndices]
    
    alpha[interpolateIndices] = numpy.polyval(alphaCoefficients, interpolatingNetworkLoad)
    beta[interpolateIndices] = numpy.polyval(betaCoefficients, interpolatingNetworkLoad)
    rho[interpolateIndices] = numpy.polyval(rhoCoefficients, interpolatingNetworkLoad)
    
    return alpha, beta, rho
    