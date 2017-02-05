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

import timetools.synchronization.compliance.analysis as tsca
import timetools.synchronization.compliance.ituTG8263.definitions as tscg8263d


# Holdover transient response, Section 8.1, Rec. ITU-T G.8263/Y.1363 (02/2012), pp7
phaseErrorNs = tsca.Mask([ ([0], tscg8263d.transientResponsePhaseErrorNs.tolist(), 
                            (-tscg8263d.transientResponsePhaseErrorNs).tolist()) ])

ffoPpb = tsca.Mask([ ([0], tscg8263d.transientResponseFfoPpb.tolist(), 
                      (-tscg8263d.transientResponseFfoPpb).tolist()) ])

ffoRatePpbPerSecond = tsca.Mask([ ([0], tscg8263d.transientResponseFfoRatePpbPerSecond.tolist(), 
                                    (-tscg8263d.transientResponseFfoRatePpbPerSecond).tolist()) ])
