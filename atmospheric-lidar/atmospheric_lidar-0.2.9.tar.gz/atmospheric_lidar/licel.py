import datetime
import logging

import numpy as np

import musa_2009_netcdf_parameters
import musa_netcdf_parameters
from generic import BaseLidarMeasurement, LidarChannel

licel_file_header_format = ['Filename',
                            'StartDate StartTime EndDate EndTime Altitude Longtitude Latitude ZenithAngle',
                            # Appart from Site that is read manually
                            'LS1 Rate1 LS2 Rate2 DataSets', ]
licel_file_channel_format = 'Active AnalogPhoton LaserUsed DataPoints 1 HV BinW Wavelength d1 d2 d3 d4 ADCbits NShots Discriminator ID'


class LicelFile:
    def __init__(self, filename, use_id_as_name=False):
        self.filename = filename
        self.use_id_as_name = use_id_as_name
        self.start_time = None
        self.stop_time = None
        self.import_file(filename)
        self.calculate_physical()

    def calculate_physical(self):
        for channel in self.channels.itervalues():
            channel.calculate_physical()

    def import_file(self, filename):
        """Imports a licel file.
        Input: filename
        Output: object """

        channels = {}

        with open(filename, 'rb') as f:

            self.read_header(f)

            # Check the complete header is read
            a = f.readline()

            # Import the data
            for current_channel_info in self.channel_info:
                raw_data = np.fromfile(f, 'i4', int(current_channel_info['DataPoints']))
                a = np.fromfile(f, 'b', 1)
                b = np.fromfile(f, 'b', 1)

                if (a[0] != 13) | (b[0] != 10):
                    logging.warning("No end of line found after record. File could be corrupt: %s" % filename)
                channel = LicelFileChannel(current_channel_info, raw_data, self.duration(),
                                           use_id_as_name=self.use_id_as_name)

                channel_name = channel.channel_name

                if channel_name in channels.keys():
                    # If the analog/photon naming scheme is not enough, find a new one!
                    raise IOError('Trying to import two channels with the same name')

                channels[channel_name] = channel

        self.channels = channels

    def read_header(self, f):
        """ Read the header of a open file f. 
        
        Returns raw_info and channel_info. Updates some object properties. """

        # Read the first 3 lines of the header
        raw_info = {}
        channel_info = []

        # Read first line
        raw_info['Filename'] = f.readline().strip()

        # Read second line
        second_line = f.readline()

        # Many licel files don't follow the licel standard. Specifically, the
        # measurement site is not always 8 characters, and can include white
        # spaces. For this, the site name is detect everything before the first 
        # date. For efficiency, the first date is found by the first '/'.
        # e.g. assuming a string like 'Site name 01/01/2010 ...' 

        site_name = second_line.split('/')[0][:-2]
        clean_site_name = site_name.strip()
        raw_info['Site'] = clean_site_name
        raw_info.update(match_lines(second_line[len(clean_site_name) + 1:], licel_file_header_format[1]))

        # Read third line
        third_line = f.readline()
        raw_info.update(match_lines(third_line, licel_file_header_format[2]))

        # Update the object properties based on the raw info
        start_string = '%s %s' % (raw_info['StartDate'], raw_info['StartTime'])
        stop_string = '%s %s' % (raw_info['EndDate'], raw_info['EndTime'])
        date_format = '%d/%m/%Y %H:%M:%S'

        self.start_time = datetime.datetime.strptime(start_string, date_format)
        self.stop_time = datetime.datetime.strptime(stop_string, date_format)
        self.latitude = float(raw_info['Latitude'])
        self.longitude = float(raw_info['Longtitude'])

        # Read the rest of the header.
        for c1 in range(int(raw_info['DataSets'])):
            channel_info.append(match_lines(f.readline(), licel_file_channel_format))

        self.raw_info = raw_info
        self.channel_info = channel_info

    def duration(self):
        """ Return the duration of the file. """
        dt = self.stop_time - self.start_time
        return dt.seconds


class LicelFileChannel:
    def __init__(self, raw_info=None, raw_data=None, duration=None, use_id_as_name=False):
        self.raw_info = raw_info
        self.raw_data = raw_data
        self.duration = duration
        self.use_id_as_name = use_id_as_name

    @property
    def wavelength(self):
        if self.raw_info is not None:
            wave_str = self.raw_info['Wavelength']
            wavelength = wave_str.split('.')[0]
            return int(wavelength)
        else:
            return None

    @property
    def channel_name(self):
        '''
        Construct the channel name adding analog photon info to avoid duplicates

        If use_id_as_name is True, the channel name will be the transient digitizer ID (e.g. BT01).
        This could be useful if the lidar system has multiple telescopes, so the descriptive name is
        not unique.
        '''
        if self.use_id_as_name:
            channel_name = self.raw_info['ID']
        else:
            acquisition_type = self.analog_photon_string(self.raw_info['AnalogPhoton'])
            channel_name = "%s_%s" % (self.raw_info['Wavelength'], acquisition_type)
        return channel_name

    def analog_photon_string(self, analog_photon_number):
        if analog_photon_number == '0':
            string = 'an'
        else:
            string = 'ph'
        return string

    def calculate_physical(self):
        data = self.raw_data

        number_of_shots = float(self.raw_info['NShots'])
        norm = data / number_of_shots
        dz = float(self.raw_info['BinW'])

        if self.raw_info['AnalogPhoton'] == '0':
            # If the channel is in analog mode
            ADCb = int(self.raw_info['ADCbits'])
            ADCrange = float(self.raw_info['Discriminator']) * 1000  # Value in mV
            channel_data = norm * ADCrange / ((2 ** ADCb) - 1)

            # print ADCb, ADCRange,cdata,norm
        else:
            # If the channel is in photoncounting mode
            # Frequency deduced from range resolution! (is this ok?)
            # c = 300 # The result will be in MHZ
            # SR  = c/(2*dz) # To account for pulse folding
            # channel_data = norm*SR
            # CHANGE:
            # For the SCC the data are needed in photons
            channel_data = norm * number_of_shots
            # print res,c,cdata,norm

        # Calculate Z
        number_of_bins = int(self.raw_info['DataPoints'])
        self.z = np.array([dz * bin_number + dz / 2.0 for bin_number in range(number_of_bins)])
        self.dz = dz
        self.number_of_bins = number_of_bins
        self.data = channel_data


class LicelLidarMeasurement(BaseLidarMeasurement):
    '''
    
    '''
    extra_netcdf_parameters = musa_netcdf_parameters
    raw_info = {}  # Keep the raw info from the files
    durations = {}  # Keep the duration of the files

    def __init__(self, filelist=None, use_id_as_name=False):
        self.use_id_as_name = use_id_as_name
        super(LicelLidarMeasurement, self).__init__(filelist)

    def import_file(self, filename):
        if filename in self.files:
            logging.warning("File has been imported already: %s" % filename)
        else:
            current_file = LicelFile(filename, use_id_as_name=self.use_id_as_name)
            self.raw_info[current_file.filename] = current_file.raw_info
            self.durations[current_file.filename] = current_file.duration()

            for channel_name, channel in current_file.channels.items():
                if channel_name not in self.channels:
                    self.channels[channel_name] = LicelChannel(channel)
                self.channels[channel_name].data[current_file.start_time] = channel.data
            self.files.append(current_file.filename)

    def append(self, other):

        self.start_times.extend(other.start_times)
        self.stop_times.extend(other.stop_times)

        for channel_name, channel in self.channels.items():
            channel.append(other.channels[channel_name])

    def _get_duration(self, raw_start_in_seconds):
        ''' Return the duration for a given time scale. If only a single
        file is imported, then this cannot be guessed from the time difference
        and the raw_info of the file are checked.
        '''

        if len(raw_start_in_seconds) == 1:  # If only one file imported
            duration = self.durations.itervalues().next()  # Get the first (and only) raw_info
            duration_sec = duration
        else:
            duration_sec = np.diff(raw_start_in_seconds)[0]

        return duration_sec


class LicelChannel(LidarChannel):
    def __init__(self, channel_file):
        c = 299792458.0  # Speed of light
        self.wavelength = channel_file.wavelength
        self.name = channel_file.channel_name
        self.binwidth = channel_file.dz * 2 / c  # in seconds 
        self.data = {}
        self.resolution = channel_file.dz
        self.z = np.arange(
            channel_file.number_of_bins) * self.resolution + self.resolution / 2.0  # Change: add half bin in the z
        self.points = channel_file.number_of_bins
        self.rc = []
        self.duration = channel_file.duration

    def append(self, other):
        if self.info != other.info:
            raise ValueError('Channel info are different. Data can not be combined.')

        self.data = np.vstack([self.data, other.data])

    def __unicode__(self):
        return "<Licel channel: %s>" % self.name

    def __str__(self):
        return unicode(self).encode('utf-8')


class Licel2009LidarMeasurement(LicelLidarMeasurement):
    extra_netcdf_parameters = musa_2009_netcdf_parameters


def match_lines(f1, f2):
    list1 = f1.split()
    list2 = f2.split()

    if len(list1) != len(list2):
        logging.debug("Channel parameter list has different length from licel specifications.")
        logging.debug("List 1: %s" % list1)
        logging.debug("List 2: %s" % list2)
    combined = zip(list2, list1)
    combined = dict(combined)
    return combined
