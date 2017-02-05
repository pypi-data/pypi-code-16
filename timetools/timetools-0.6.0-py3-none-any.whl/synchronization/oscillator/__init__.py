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

import logging
import numpy


log = logging.getLogger( __name__ )


class OscillatorModel :
    def __init__( self, initialFfoPpb = 0,
                  agingModel = None,
                  temperatureSensitivityModel = None,
                  noiseModel = None ) :
        self.initialFfoPpb = initialFfoPpb
        self.agingModel = agingModel
        self.temperatureSensitivityModel = temperatureSensitivityModel
        self.noiseModel = noiseModel


    def generate( self, referenceTimeSeconds,
                  referenceTemperatureKelvin = None ) :

        ffoPpb = numpy.ones( referenceTimeSeconds.shape ) * self.initialFfoPpb

        if self.agingModel is not None :
            ffoPpb += self.agingModel.generate( referenceTimeSeconds )

        if self.noiseModel is not None :
            ffoPpb += self.noiseModel.generate( referenceTimeSeconds )

        if self.temperatureSensitivityModel is not None and referenceTemperatureKelvin is not None :
            assert (numpy.all( referenceTemperatureKelvin.shape == referenceTemperatureKelvin.shape ))
            ffoPpb += self.temperatureSensitivityModel.generate( referenceTemperatureKelvin )

        elif referenceTemperatureKelvin is None and self.temperatureSensitivityModel is not None :
            log.warning(
                'Temperature sensitivity model was specified but reference temperature not specified for FFO calculations.' )

        elif referenceTemperatureKelvin is not None and self.temperatureSensitivityModel is None :
            log.warning(
                'Temperature sensitivity model was not specified but reference temperature was specified for FFO calculations.' )

        return ffoPpb
