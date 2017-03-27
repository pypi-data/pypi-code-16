#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010-2017

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""HRIT format reader for JMA data.

References:
    JMA HRIT - Mission Specific Implementation
    http://www.jma.go.jp/jma/jma-eng/satellite/introduction/4_2HRIT.pdf

"""

import logging
from datetime import datetime, timedelta

import numpy as np

from pyresample import geometry
from satpy.readers.hrit_base import (HRITFileHandler, ancillary_text,
                                     annotation_header, base_hdr_map,
                                     image_data_function, make_time_cds_short,
                                     time_cds_short)


class CalibrationError(Exception):
    pass

logger = logging.getLogger('hrit_jma')


# JMA implementation:
key_header = np.dtype([('key_number', 'u4')])

segment_identification = np.dtype([('image_segm_seq_no', '>u1'),
                                   ('total_no_image_segm', '>u1'),
                                   ('line_no_image_segm', '>u2')])

encryption_key_message = np.dtype([('station_number', '>u2')])

image_compensation_information = np.dtype('|S1')

image_observation_time = np.dtype('|S1')

image_quality_information = np.dtype('|S1')


jma_variable_length_headers = {}

msg_text_headers = {image_data_function: 'image_data_function',
                    annotation_header: 'annotation_header',
                    ancillary_text: 'ancillary_text',
                    image_compensation_information: 'image_compensation_information',
                    image_observation_time: 'image_observation_time',
                    image_quality_information: 'image_quality_information'}

jma_hdr_map = base_hdr_map.copy()
jma_hdr_map.update({7: key_header,
                    128: segment_identification,
                    129: encryption_key_message,
                    130: image_compensation_information,
                    131: image_observation_time,
                    132: image_quality_information
                    })


cuc_time = np.dtype([('coarse', 'u1', (4, )),
                     ('fine', 'u1', (3, ))])

time_cds_expanded = np.dtype([('days', '>u2'),
                              ('milliseconds', '>u4'),
                              ('microseconds', '>u2'),
                              ('nanoseconds', '>u2')])


def make_time_cds_expanded(tcds_array):
    return (datetime(1958, 1, 1) +
            timedelta(days=int(tcds_array['days']),
                      milliseconds=int(tcds_array['milliseconds']),
                      microseconds=float(tcds_array['microseconds'] +
                                         tcds_array['nanoseconds'] / 1000.)))


def recarray2dict(arr):
    res = {}
    for dtuple in arr.dtype.descr:
        key = dtuple[0]
        ntype = dtuple[1]
        data = arr[key]
        if isinstance(ntype, list):
            res[key] = recarray2dict(data)
        else:
            res[key] = data

    return res


class HRITJMAFileHandler(HRITFileHandler):

    """JMA HRIT format reader
    """

    def __init__(self, filename, filename_info, filetype_info):
        """Initialize the reader."""
        super(HRITJMAFileHandler, self).__init__(filename, filename_info,
                                                 filetype_info,
                                                 (jma_hdr_map,
                                                  jma_variable_length_headers,
                                                  jma_text_headers))

        import ipdb
        ipdb.set_trace()

        earth_model = self.prologue['GeometricProcessing']['EarthModel']
        b = (earth_model['NorthPolarRadius'] +
             earth_model['SouthPolarRadius']) / 2.0 * 1000
        self.mda['projection_parameters'][
            'a'] = earth_model['EquatorialRadius'] * 1000
        self.mda['projection_parameters']['b'] = b
        ssp = self.prologue['ImageDescription'][
            'ProjectionDescription']['LongitudeOfSSP']
        self.mda['projection_parameters']['SSP_longitude'] = ssp
        self.platform_id = self.prologue["SatelliteStatus"][
            "SatelliteDefinition"]["SatelliteID"]
        self.platform_name = "Meteosat-" + SATNUM[self.platform_id]
        self.channel_name = CHANNEL_NAMES[self.mda['spectral_channel_id']]

    @property
    def start_time(self):
        pacqtime = self.epilogue['ImageProductionStats'][
            'ActualScanningSummary']

        return pacqtime['ForwardScanStart']

    @property
    def end_time(self):
        pacqtime = self.epilogue['ImageProductionStats'][
            'ActualScanningSummary']

        return pacqtime['ForwardScanEnd']

    def get_area_extent(self, size, offsets, factors, platform_height):
        """Get the area extent of the file."""
        aex = super(HRITMSGFileHandler, self).get_area_extent(size,
                                                              offsets,
                                                              factors,
                                                              platform_height)

        if self.start_time < datetime(2037, 1, 24):
            xadj = 1500
            yadj = 1500
            aex = (aex[0] + xadj, aex[1] + yadj,
                   aex[2] + xadj, aex[3] + yadj)

        return aex

    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        res = super(HRITMSGFileHandler, self).get_dataset(key, info, out,
                                                          xslice, yslice)
        if res is not None:
            out = res

        self.calibrate(out, key.calibration)
        out.info['units'] = info['units']
        out.info['standard_name'] = info['standard_name']
        out.info['platform_name'] = self.platform_name
        out.info['sensor'] = 'seviri'

    def calibrate(self, data, calibration):
        """Calibrate the data."""
        tic = datetime.now()

        if calibration == 'counts':
            return

        if calibration in ['radiance', 'reflectance', 'brightness_temperature']:
            self.convert_to_radiance(data)
        if calibration == 'reflectance':
            self._vis_calibrate(data)
        elif calibration == 'brightness_temperature':
            self._ir_calibrate(data)

        logger.debug("Calibration time " + str(datetime.now() - tic))

    def convert_to_radiance(self, data):
        """Calibrate to radiance."""
        coeffs = self.prologue["RadiometricProcessing"]
        coeffs = coeffs["Level1_5ImageCalibration"]
        gain = coeffs['Cal_Slope'][self.mda['spectral_channel_id'] - 1]
        offset = coeffs['Cal_Offset'][self.mda['spectral_channel_id'] - 1]

        data.data[:] *= gain
        data.data[:] += offset
        data.data[data.data < 0] = 0

    def _vis_calibrate(self, data):
        """Visible channel calibration only."""
        solar_irradiance = CALIB[self.platform_id][self.channel_name]["F"]
        data.data[:] *= 100 / solar_irradiance

    def _tl15(self, data):
        """Compute the L15 temperature."""
        wavenumber = CALIB[self.platform_id][self.channel_name]["VC"]
        data.data[:] **= -1
        data.data[:] *= C1 * wavenumber ** 3
        data.data[:] += 1
        np.log(data.data, out=data.data)
        data.data[:] **= -1
        data.data[:] *= C2 * wavenumber

    def _erads2bt(self, data):
        """computation based on effective radiance."""
        cal_info = CALIB[self.platform_id][self.channel_name]
        alpha = cal_info["ALPHA"]
        beta = cal_info["BETA"]

        self._tl15(data)

        data.data[:] -= beta
        data.data[:] /= alpha

    def _srads2bt(self, data):
        """computation based on spectral radiance."""
        coef_a, coef_b, coef_c = BTFIT[self.channel_name]

        self._tl15(data)

        data.data[:] = (coef_a * data.data[:] ** 2 +
                        coef_b * data.data[:] +
                        coef_c)

    def _ir_calibrate(self, data):
        """IR calibration."""
        cal_type = self.prologue['ImageDescription'][
            'Level1_5ImageProduction']['PlannedChanProcessing'][self.mda['spectral_channel_id']]

        if cal_type == 1:
            # spectral radiances
            self._srads2bt(data)
        elif cal_type == 2:
            # effective radiances
            self._erads2bt(data)
        else:
            raise NotImplemented('Unknown calibration type')


def show(data, negate=False):
    """Show the stretched data.
    """
    from PIL import Image as pil
    data = np.array((data - data.min()) * 255.0 /
                    (data.max() - data.min()), np.uint8)
    if negate:
        data = 255 - data
    img = pil.fromarray(data)
    img.show()


if __name__ == "__main__":

    # TESTFILE = ("/media/My Passport/HIMAWARI-8/HISD/Hsfd/" +
    #            "201502/07/201502070200/00/B13/" +
    #            "HS_H08_20150207_0200_B13_FLDK_R20_S0101.DAT")
    TESTFILE = ("/local_disk/data/himawari8/testdata/" +
                "HS_H08_20130710_0300_B13_FLDK_R20_S1010.DAT")
    #"HS_H08_20130710_0300_B01_FLDK_R10_S1010.DAT")
    SCENE = ahisf([TESTFILE])
    SCENE.read_band(TESTFILE)
    SCENE.calibrate(['13'])
    # SCENE.calibrate(['13'], calibrate=0)

    # print SCENE._data['13']['counts'][0].shape

    show(SCENE.channels['13'], negate=False)

    import matplotlib.pyplot as plt
    plt.imshow(SCENE.channels['13'])
    plt.colorbar()
    plt.show()
