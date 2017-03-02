# General imports
import datetime
from operator import itemgetter
import logging

import matplotlib as mpl
import netCDF4 as netcdf
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import ScalarFormatter

netcdf_format = 'NETCDF3_CLASSIC'  # choose one of 'NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'NETCDF4_CLASSIC' and 'NETCDF4'


class BaseLidarMeasurement(object):
    """ This is the general measurement object.
    It is meant to become a general measurement object 
    independent of the input files.
    
    Each subclass should implement the following:
    * the import_file method.
    * set the "extra_netcdf_parameters" variable to a dictionary that includes the appropriate parameters.
    
    You can override the get_PT method to define a custom procedure to get ground temperature and pressure.
    The one implemented by default is by using the MILOS meteorological station data. 
    
    """

    def __init__(self, filelist=None):
        self.info = {}
        self.dimensions = {}
        self.variables = {}
        self.channels = {}
        self.attributes = {}
        self.files = []
        self.dark_measurement = None

        if filelist:
            self.import_files(filelist)

    def import_files(self, filelist):
        for f in filelist:
            self.import_file(f)
        self.update()

    def import_file(self, filename):
        raise NotImplementedError('Importing files should be defined in the instrument-specific subclass.')

    def update(self):
        '''
        Update the the info, variables and dimensions of the lidar measurement based 
        on the information found in the channels.
        
        Reading of the scan_angles parameter is not implemented.
        '''

        # Initialize
        start_time = []
        stop_time = []
        points = []
        all_time_scales = []
        channel_name_list = []

        # Get the information from all the channels
        for channel_name, channel in self.channels.items():
            channel.update()
            start_time.append(channel.start_time)
            stop_time.append(channel.stop_time)
            points.append(channel.points)
            all_time_scales.append(channel.time)
            channel_name_list.append(channel_name)

        # Find the unique time scales used in the channels
        time_scales = set(all_time_scales)

        # Update the info dictionary
        self.info['start_time'] = min(start_time)
        self.info['stop_time'] = max(stop_time)
        self.info['duration'] = self.info['stop_time'] - self.info['start_time']

        # Update the dimensions dictionary
        self.dimensions['points'] = max(points)
        self.dimensions['channels'] = len(self.channels)
        # self.dimensions['scan angles'] = 1
        self.dimensions['nb_of_time_scales'] = len(time_scales)

        # Update the variables dictionary
        # Write time scales in seconds
        raw_Data_Start_Time = []
        raw_Data_Stop_Time = []

        for current_time_scale in list(time_scales):
            raw_start_time = np.array(current_time_scale) - min(start_time)  # Time since start_time
            raw_start_in_seconds = np.array([t.seconds for t in raw_start_time])  # Convert in seconds
            raw_Data_Start_Time.append(raw_start_in_seconds)  # And add to the list
            # Check if this time scale has measurements every 30 or 60 seconds.

            duration = self._get_duration(raw_start_in_seconds)

            raw_stop_in_seconds = raw_start_in_seconds + duration
            raw_Data_Stop_Time.append(raw_stop_in_seconds)

        self.variables['Raw_Data_Start_Time'] = raw_Data_Start_Time
        self.variables['Raw_Data_Stop_Time'] = raw_Data_Stop_Time

        # Make a dictionary to match time scales and channels
        channel_timescales = []
        for (channel_name, current_time_scale) in zip(channel_name_list, all_time_scales):
            # The following lines are PEARL specific. The reason they are here is not clear.
            # if channel_name =='1064BLR':
            #     channel_name = '1064'
            for (ts, n) in zip(time_scales, range(len(time_scales))):
                if current_time_scale == ts:
                    channel_timescales.append([channel_name, n])
        self.variables['id_timescale'] = dict(channel_timescales)

    def _get_duration(self, raw_start_in_seconds):
        ''' Return the duration for a given time scale. In some files (e.g. Licel) this
        can be specified from the files themselves. In others this must be guessed.
         
        '''
        # The old method, kept here for reference
        # dt = np.mean(np.diff(raw_start_in_seconds))
        # for d in duration_list:
        #    if abs(dt - d) <15: #If the difference of measurements is 10s near the(30 or 60) seconds
        #        duration = d

        duration = np.diff(raw_start_in_seconds)[0]

        return duration

    def subset_by_channels(self, channel_subset):
        ''' Get a measurement object containing only the channels with names
        contained in the channel_sublet list '''

        m = self.__class__()  # Create an object of the same type as this one.
        m.channels = dict([(channel, self.channels[channel]) for channel
                           in channel_subset])
        m.update()
        return m

    def subset_by_scc_channels(self):
        """
        Subset the measurement based on the channels provided in the extra_netecdf_parameter file.
        """
        scc_channels = self.extra_netcdf_parameters.channel_parameters.keys()
        common_channels = list(set(scc_channels).intersection(self.channels.keys()))

        if not common_channels:
            logging.debug("Config channels: %s." % ','.join(scc_channels))
            logging.debug("Licel channels: %s." % ','.join(self.channels.keys()))
            raise ValueError('No common channels between licel and configuration files.')

        return self.subset_by_channels(common_channels)

    def subset_by_time(self, start_time, stop_time):

        if start_time > stop_time:
            raise ValueError('Stop time should be after start time')

        if (start_time < self.info['start_time']) or (stop_time > self.info['stop_time']):
            raise ValueError('The time interval specified is not part of the measurement')

        m = self.__class__()  # Create an object of the same type as this one.
        for (channel_name, channel) in self.channels.items():
            m.channels[channel_name] = channel.subset_by_time(start_time, stop_time)
        m.update()
        return m

    def subset_by_bins(self, b_min=0, b_max=None):
        """Remove some height bins from the file. This could be needed to 
        remove aquisition artifacts at the start or the end of the files.
        """

        m = self.__class__()  # Create an object of the same type as this one.

        for (channel_name, channel) in self.channels.items():
            m.channels[channel_name] = channel.subset_by_bins(b_min, b_max)

        m.update()

        return m

    def rename_channel(self, prefix="", suffix=""):
        """ Add a prefix and a suffix in a channel name.

        :param prefix: A string for the prefix
        :param suffix: A string for the suffix
        :return: Nothing
        """
        channel_names = self.channels.keys()

        for channel_name in channel_names:
            new_name = prefix + channel_name + suffix
            self.channels[new_name] = self.channels.pop(channel_name)

    def get_PT(self):
        ''' Sets the pressure and temperature at station level .
        The results are stored in the info dictionary.        
        '''

        self.info['Temperature'] = 10.0
        self.info['Pressure'] = 930.0

    def subtract_dark(self):

        if not self.dark_measurement:
            raise IOError('No dark measurements have been imported yet.')

        for (channel_name, dark_channel) in self.dark_measurement.channels.iteritems():
            dark_profile = dark_channel.average_profile()
            channel = self.channels[channel_name]

            for measurement_time, data in channel.data.iteritems():
                channel.data[measurement_time] = data - dark_profile

            channel.update()

    def set_measurement_id(self, measurement_id=None, measurement_number="00"):
        """
        Sets the measurement id for the SCC file.

        Parameters
        ----------
        measurement_id: str
           A measurement id with the format YYYYMMDDccNN, where YYYYMMDD the date,
           cc the earlinet call sign and NN a number between 00 and 99.
        measurement_number: str
           If measurement id is not provided the method will try to create one
           based on the input dete. The measurement number can specify the value
           of NN in the created ID.
        """
        if measurement_id is None:
            date_str = self.info['start_time'].strftime('%Y%m%d')
            try:
                earlinet_station_id = self.extra_netcdf_parameters.general_parameters['Call sign']
            except:
                raise ValueError("No valid SCC netcdf parameters found. Did you define the proper subclass?")
            measurement_id = "{0}{1}{2}".format(date_str, earlinet_station_id, measurement_number)

        self.info['Measurement_ID'] = measurement_id

    def save_as_netcdf(self, filename=None):
        """Saves the measurement in the netcdf format as required by the SCC.
        Input: filename. If no filename is provided <measurement_id>.nc will
               be used. 
        """
        params = self.extra_netcdf_parameters

        # Guess measurement ID if none is provided
        if 'Measurement_ID' not in self.info:
            self.set_measurement_id()

        # Check if temperature and pressure are defined
        for parameter in ['Temperature', 'Pressure']:
            stored_value = self.info.get(parameter, None)
            if stored_value is None:
                try:
                    self.get_PT()
                except:
                    raise ValueError('A value needs to be specified for %s' % parameter)

        if not filename:
            filename = "%s.nc" % self.info['Measurement_ID']

        self.scc_filename = filename

        dimensions = {'points': 1,
                      'channels': 1,
                      'time': None,
                      'nb_of_time_scales': 1,
                      'scan_angles': 1, }  # Mandatory dimensions. Time bck not implemented

        global_att = {'Measurement_ID': None,
                      'RawData_Start_Date': None,
                      'RawData_Start_Time_UT': None,
                      'RawData_Stop_Time_UT': None,
                      'RawBck_Start_Date': None,
                      'RawBck_Start_Time_UT': None,
                      'RawBck_Stop_Time_UT': None,
                      'Sounding_File_Name': None,
                      'LR_File_Name': None,
                      'Overlap_File_Name': None,
                      'Location': None,
                      'System': None,
                      'Latitude_degrees_north': None,
                      'Longitude_degrees_east': None,
                      'Altitude_meter_asl': None}

        channel_variables = self._get_scc_mandatory_channel_variables()

        channels = self.channels.keys()

        input_values = dict(self.dimensions, **self.variables)

        # Add some mandatory global attributes
        input_values['Measurement_ID'] = self.info['Measurement_ID']
        input_values['RawData_Start_Date'] = self.info['start_time'].strftime('%Y%m%d')
        input_values['RawData_Start_Time_UT'] = self.info['start_time'].strftime('%H%M%S')
        input_values['RawData_Stop_Time_UT'] = self.info['stop_time'].strftime('%H%M%S')

        # Add some optional global attributes
        input_values['System'] = params.general_parameters['System']
        input_values['Latitude_degrees_north'] = params.general_parameters['Latitude_degrees_north']
        input_values['Longitude_degrees_east'] = params.general_parameters['Longitude_degrees_east']
        input_values['Altitude_meter_asl'] = params.general_parameters['Altitude_meter_asl']

        # Open a netCDF4 file
        f = netcdf.Dataset(filename, 'w', format=netcdf_format)  # the format is specified in the begining of the file

        # Create the dimensions in the file
        for (d, v) in dimensions.iteritems():
            v = input_values.pop(d, v)
            f.createDimension(d, v)

        # Create global attributes
        for (attrib, value) in global_att.iteritems():
            val = input_values.pop(attrib, value)
            if val:
                setattr(f, attrib, val)

        """ Variables """
        # Write either channel_id or string_channel_id in the file
        first_channel_keys = params.channel_parameters.items()[0][1].keys()
        if "channel_ID" in first_channel_keys:
            channel_var = 'channel_ID'
            variable_type = 'i'
        elif "channel string ID" in first_channel_keys:
            channel_var = 'channel string ID'
            variable_type = str
        else:
            raise ValueError('Channel parameters should define either "chanel_id" or "channel_string_ID".')

        temp_v = f.createVariable(channel_var, variable_type, ('channels',))
        for n, channel in enumerate(channels):
            temp_v[n] = params.channel_parameters[channel][channel_var]

        # Write the values of fixed channel parameters
        for (var, t) in channel_variables.iteritems():
            temp_v = f.createVariable(var, t[1], t[0])
            for (channel, n) in zip(channels, range(len(channels))):
                temp_v[n] = params.channel_parameters[channel][var]

        # Write the id_timescale values
        temp_id_timescale = f.createVariable('id_timescale', 'i', ('channels',))
        for (channel, n) in zip(channels, range(len(channels))):
            temp_id_timescale[n] = self.variables['id_timescale'][channel]

        # Laser pointing angle
        temp_v = f.createVariable('Laser_Pointing_Angle', 'd', ('scan_angles',))
        temp_v[:] = params.general_parameters['Laser_Pointing_Angle']

        # Molecular calculation
        temp_v = f.createVariable('Molecular_Calc', 'i')
        temp_v[:] = params.general_parameters['Molecular_Calc']

        # Laser pointing angles of profiles
        temp_v = f.createVariable('Laser_Pointing_Angle_of_Profiles', 'i', ('time', 'nb_of_time_scales'))
        for (time_scale, n) in zip(self.variables['Raw_Data_Start_Time'],
                                   range(len(self.variables['Raw_Data_Start_Time']))):
            temp_v[:len(time_scale), n] = 0  # The lidar has only one laser pointing angle

        # Raw data start/stop time
        temp_raw_start = f.createVariable('Raw_Data_Start_Time', 'i', ('time', 'nb_of_time_scales'))
        temp_raw_stop = f.createVariable('Raw_Data_Stop_Time', 'i', ('time', 'nb_of_time_scales'))
        for (start_time, stop_time, n) in zip(self.variables['Raw_Data_Start_Time'],
                                              self.variables['Raw_Data_Stop_Time'],
                                              range(len(self.variables['Raw_Data_Start_Time']))):
            temp_raw_start[:len(start_time), n] = start_time
            temp_raw_stop[:len(stop_time), n] = stop_time

        # Laser shots
        temp_v = f.createVariable('Laser_Shots', 'i', ('time', 'channels'))
        for (channel, n) in zip(channels, range(len(channels))):
            time_length = len(self.variables['Raw_Data_Start_Time'][self.variables['id_timescale'][channel]])
            # Array slicing stoped working as usual ex. temp_v[:10] = 100 does not work. ??? np.ones was added.
            temp_v[:time_length, n] = np.ones(time_length) * params.channel_parameters[channel]['Laser_Shots']

        # Raw lidar data
        temp_v = f.createVariable('Raw_Lidar_Data', 'd', ('time', 'channels', 'points'))
        for (channel, n) in zip(channels, range(len(channels))):
            c = self.channels[channel]
            temp_v[:len(c.time), n, :c.points] = c.matrix

        self.add_dark_measurements_to_netcdf(f, channels)

        # Pressure at lidar station
        temp_v = f.createVariable('Pressure_at_Lidar_Station', 'd')
        temp_v[:] = self.info['Pressure']

        # Temperature at lidar station
        temp_v = f.createVariable('Temperature_at_Lidar_Station', 'd')
        temp_v[:] = self.info['Temperature']

        self.save_netcdf_extra(f)
        f.close()

    def _get_scc_mandatory_channel_variables(self):
        channel_variables = \
            {'Background_Low': (('channels',), 'd'),
             'Background_High': (('channels',), 'd'),
             'LR_Input': (('channels',), 'i'),
             'DAQ_Range': (('channels',), 'd'),
             }
        return channel_variables

    def add_dark_measurements_to_netcdf(self, f, channels):

        # Get dark measurements. If it is not given in self.dark_measurement
        # try to get it using the get_dark_measurements method. If none is found
        # return without adding something.
        if self.dark_measurement is None:
            self.dark_measurement = self.get_dark_measurements()

        if self.dark_measurement is None:
            return

        dark_measurement = self.dark_measurement

        # Calculate the length of the time_bck dimensions
        number_of_profiles = [len(c.time) for c in dark_measurement.channels.values()]
        max_number_of_profiles = np.max(number_of_profiles)

        # Create the dimension
        f.createDimension('time_bck', max_number_of_profiles)

        # Save the dark measurement data
        temp_v = f.createVariable('Background_Profile', 'd', ('time_bck', 'channels', 'points'))
        for (channel, n) in zip(channels, range(len(channels))):
            c = dark_measurement.channels[channel]
            temp_v[:len(c.time), n, :c.points] = c.matrix

        # Dark profile start/stop time
        temp_raw_start = f.createVariable('Raw_Bck_Start_Time', 'i', ('time_bck', 'nb_of_time_scales'))
        temp_raw_stop = f.createVariable('Raw_Bck_Stop_Time', 'i', ('time_bck', 'nb_of_time_scales'))
        for (start_time, stop_time, n) in zip(dark_measurement.variables['Raw_Data_Start_Time'],
                                              dark_measurement.variables['Raw_Data_Stop_Time'],
                                              range(len(dark_measurement.variables['Raw_Data_Start_Time']))):
            temp_raw_start[:len(start_time), n] = start_time
            temp_raw_stop[:len(stop_time), n] = stop_time

        # Dark measurement start/stop time
        f.RawBck_Start_Date = dark_measurement.info['start_time'].strftime('%Y%m%d')
        f.RawBck_Start_Time_UT = dark_measurement.info['start_time'].strftime('%H%M%S')
        f.RawBck_Stop_Time_UT = dark_measurement.info['stop_time'].strftime('%H%M%S')

    def save_netcdf_extra(self, f):
        pass

    def _gettime(self, date_str, time_str):
        t = datetime.datetime.strptime(date_str + time_str, '%d/%m/%Y%H.%M.%S')
        return t

    def plot(self):
        for channel in self.channels:
            self.channels[channel].plot(show_plot=False)
        plt.show()

    def get_dark_measurements(self):
        return None

    @property
    def mean_time(self):
        start_time = self.info['start_time']
        stop_time = self.info['stop_time']
        dt = stop_time - start_time
        t_mean = start_time + dt / 2
        return t_mean


class LidarChannel:
    def __init__(self, channel_parameters):
        c = 299792458  # Speed of light
        self.wavelength = channel_parameters['name']
        self.name = str(self.wavelength)
        self.binwidth = float(channel_parameters['binwidth'])  # in microseconds
        self.data = {}
        self.resolution = self.binwidth * c / 2
        self.z = np.arange(
            len(channel_parameters['data'])) * self.resolution + self.resolution / 2.0  # Change: add half bin in the z
        self.points = len(channel_parameters['data'])
        self.rc = []
        self.duration = 60

    def calculate_rc(self, idx_min=4000, idx_max=5000):
        background = np.mean(self.matrix[:, idx_min:idx_max], axis=1)  # Calculate the background from 30000m and above
        self.rc = (self.matrix.transpose() - background).transpose() * (self.z ** 2)

    def update(self):
        self.start_time = min(self.data.keys())
        self.stop_time = max(self.data.keys()) + datetime.timedelta(seconds=self.duration)
        self.time = tuple(sorted(self.data.keys()))
        sorted_data = sorted(self.data.iteritems(), key=itemgetter(0))
        self.matrix = np.array(map(itemgetter(1), sorted_data))

    def _nearest_dt(self, dtime):
        margin = datetime.timedelta(seconds=300)
        if ((dtime + margin) < self.start_time) | ((dtime - margin) > self.stop_time):
            logging.error("Requested date not covered in this file")
            raise ValueError("Requested date not covered in this file")
        dt = abs(self.time - np.array(dtime))
        dtmin = min(dt)

        if dtmin > datetime.timedelta(seconds=60):
            logging.warning("Nearest profile more than 60 seconds away. dt = %s." % dtmin)
        ind_t = np.where(dt == dtmin)
        ind_a = ind_t[0]
        if len(ind_a) > 1:
            ind_a = ind_a[0]
        chosen_time = self.time[ind_a]
        return chosen_time, ind_a

    def subset_by_time(self, start_time, stop_time):

        time_array = np.array(self.time)
        condition = (time_array >= start_time) & (time_array <= stop_time)

        subset_time = time_array[condition]
        subset_data = dict([(c_time, self.data[c_time]) for c_time in subset_time])

        # Create a list with the values needed by channel's __init__()
        parameter_values = {'name': self.wavelength,
                            'binwidth': self.binwidth,
                            'data': subset_data[subset_time[0]], }

        # We should use __class__ instead of class name, so that this works properly
        # with subclasses
        # Ex: c = self.__class__(parameters_values)  
        # This does not currently work with Licel files though
        c = LidarChannel(parameter_values)
        c.data = subset_data
        c.update()
        return c

    def subset_by_bins(self, b_min=0, b_max=None):
        """Remove some height bins from the file. This could be needed to 
        remove aquisition artifacts at the start or the end of the files.
        """

        subset_data = {}

        for ctime, cdata in self.data.items():
            subset_data[ctime] = cdata[b_min:b_max]

        # Create a list with the values needed by channel's __init__()
        parameters_values = {'name': self.wavelength,
                             'binwidth': self.binwidth,
                             'data': subset_data[
                                 subset_data.keys()[0]], }  # We just need any array with the correct length

        c = LidarChannel(parameters_values)
        c.data = subset_data
        c.update()
        return c

    def profile(self, dtime, signal_type='rc'):
        t, idx = self._nearest_dt(dtime)
        if signal_type == 'rc':
            data = self.rc
        else:
            data = self.matrix

        prof = data[idx, :][0]
        return prof, t

    def get_slice(self, starttime, endtime, signal_type='rc'):
        if signal_type == 'rc':
            data = self.rc
        else:
            data = self.matrix
        tim = np.array(self.time)
        starttime = self._nearest_dt(starttime)[0]
        endtime = self._nearest_dt(endtime)[0]
        condition = (tim >= starttime) & (tim <= endtime)
        sl = data[condition, :]
        t = tim[condition]
        return sl, t

    def profile_for_duration(self, tim, duration=datetime.timedelta(seconds=0), signal_type='rc'):
        """ Calculates the profile around a specific time (tim). """
        starttime = tim - duration / 2
        endtime = tim + duration / 2
        d, t = self.get_slice(starttime, endtime, signal_type=signal_type)
        prof = np.mean(d, axis=0)
        tmin = min(t)
        tmax = max(t)
        tav = tmin + (tmax - tmin) / 2
        return prof, (tav, tmin, tmax)

    def average_profile(self):
        """ Return the average profile (NOT range corrected) for all the duration of the measurement. """
        prof = np.mean(self.matrix, axis=0)
        return prof

    def plot(self, signal_type='rc', filename=None, zoom=[0, 12000, 0, -1], show_plot=True, cmap=plt.cm.jet, z0=None,
             title=None, vmin=0, vmax=1.3 * 10 ** 7):
        # if filename is not None:
        #    matplotlib.use('Agg')

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        self.draw_plot(ax1, cmap=cmap, signal_type=signal_type, zoom=zoom, z0=z0, vmin=vmin, vmax=vmax)

        if title:
            ax1.set_title(title)
        else:
            ax1.set_title("%s signal - %s" % (signal_type.upper(), self.name))

        if filename is not None:
            pass
            # plt.savefig(filename)
        else:
            if show_plot:
                plt.show()
                # plt.close() ???

    def draw_plot(self, ax1, cmap=plt.cm.jet, signal_type='rc',
                  zoom=[0, 12000, 0, -1], z0=None,
                  add_colorbar=True, cmap_label='a.u.', cb_format=None,
                  vmin=0, vmax=1.3 * 10 ** 7):

        if signal_type == 'rc':
            if len(self.rc) == 0:
                self.calculate_rc()
            data = self.rc
        else:
            data = self.matrix

        hmax_idx = self.index_at_height(zoom[1])

        # If z0 is given, then the plot is a.s.l.
        if z0:
            ax1.set_ylabel('Altitude a.s.l. [km]')
        else:
            ax1.set_ylabel('Altitude a.g.l. [km]')
            z0 = 0

        ax1.set_xlabel('Time UTC [hh:mm]')
        # y axis in km, xaxis /2 to make 30s measurements in minutes. Only for 1064
        # dateFormatter = mpl.dates.DateFormatter('%H.%M')
        # hourlocator = mpl.dates.HourLocator()

        # dayFormatter = mpl.dates.DateFormatter('\n\n%d/%m')
        # daylocator = mpl.dates.DayLocator()
        hourFormatter = mpl.dates.DateFormatter('%H:%M')
        hourlocator = mpl.dates.AutoDateLocator(minticks=3, maxticks=8, interval_multiples=True)

        # ax1.axes.xaxis.set_major_formatter(dayFormatter)
        # ax1.axes.xaxis.set_major_locator(daylocator)
        ax1.axes.xaxis.set_major_formatter(hourFormatter)
        ax1.axes.xaxis.set_major_locator(hourlocator)

        ts1 = mpl.dates.date2num(self.start_time)
        ts2 = mpl.dates.date2num(self.stop_time)

        im1 = ax1.imshow(data.transpose()[zoom[0]:hmax_idx, zoom[2]:zoom[3]],
                         aspect='auto',
                         origin='lower',
                         cmap=cmap,
                         vmin=vmin,
                         # vmin = data[:,10:400].max() * 0.1,
                         vmax=vmax,
                         # vmax = data[:,10:400].max() * 0.9,
                         extent=[ts1, ts2, self.z[zoom[0]] / 1000.0 + z0 / 1000.,
                                 self.z[hmax_idx] / 1000.0 + z0 / 1000.],
                         )

        if add_colorbar:
            if cb_format:
                cb1 = plt.colorbar(im1, format=cb_format)
            else:
                cb1 = plt.colorbar(im1)
            cb1.ax.set_ylabel(cmap_label)

            # Make the ticks of the colorbar smaller, two points smaller than the default font size
            cb_font_size = mpl.rcParams['font.size'] - 2
            for ticklabels in cb1.ax.get_yticklabels():
                ticklabels.set_fontsize(cb_font_size)
            cb1.ax.yaxis.get_offset_text().set_fontsize(cb_font_size)

    def draw_plot_new(self, ax1, cmap=plt.cm.jet, signal_type='rc',
                      zoom=[0, 12000, 0, None], z0=None,
                      add_colorbar=True, cmap_label='a.u.',
                      cb_format=None, power_limits=(-2, 2),
                      date_labels=False,
                      vmin=0, vmax=1.3 * 10 ** 7):

        if signal_type == 'rc':
            if len(self.rc) == 0:
                self.calculate_rc()
            data = self.rc
        else:
            data = self.matrix

        hmax_idx = self.index_at_height(zoom[1])
        hmin_idx = self.index_at_height(zoom[0])

        # If z0 is given, then the plot is a.s.l.
        if z0:
            ax1.set_ylabel('Altitude a.s.l. [km]')
        else:
            ax1.set_ylabel('Altitude a.g.l. [km]')
            z0 = 0

        ax1.set_xlabel('Time UTC [hh:mm]')
        # y axis in km, xaxis /2 to make 30s measurements in minutes. Only for 1064
        # dateFormatter = mpl.dates.DateFormatter('%H.%M')
        # hourlocator = mpl.dates.HourLocator()


        if date_labels:
            dayFormatter = mpl.dates.DateFormatter('%H:%M\n%d/%m/%Y')
            daylocator = mpl.dates.AutoDateLocator(minticks=3, maxticks=8, interval_multiples=True)
            ax1.axes.xaxis.set_major_formatter(dayFormatter)
            ax1.axes.xaxis.set_major_locator(daylocator)
        else:
            hourFormatter = mpl.dates.DateFormatter('%H:%M')
            hourlocator = mpl.dates.AutoDateLocator(minticks=3, maxticks=8, interval_multiples=True)
            ax1.axes.xaxis.set_major_formatter(hourFormatter)
            ax1.axes.xaxis.set_major_locator(hourlocator)

        # Get the values of the time axis
        dt = datetime.timedelta(seconds=self.duration)

        time_cut = self.time[zoom[2]:zoom[3]]
        time_last = time_cut[-1] + dt  # The last element needed for pcolormesh

        time_all = time_cut + (time_last,)

        t_axis = mpl.dates.date2num(time_all)

        # Get the values of the z axis
        z_cut = self.z[hmin_idx:hmax_idx] - self.resolution / 2.
        z_last = z_cut[-1] + self.resolution

        z_axis = np.append(z_cut, z_last) / 1000. + z0 / 1000.  # Convert to km

        # Plot
        im1 = ax1.pcolormesh(t_axis, z_axis, data.T[hmin_idx:hmax_idx, zoom[2]:zoom[3]],
                             cmap=cmap,
                             vmin=vmin,
                             vmax=vmax,
                             )

        if add_colorbar:
            if cb_format:
                cb1 = plt.colorbar(im1, format=cb_format)
            else:
                cb_formatter = ScalarFormatter()
                cb_formatter.set_powerlimits(power_limits)
                cb1 = plt.colorbar(im1, format=cb_formatter)
            cb1.ax.set_ylabel(cmap_label)

            # Make the ticks of the colorbar smaller, two points smaller than the default font size
            cb_font_size = mpl.rcParams['font.size'] - 2
            for ticklabels in cb1.ax.get_yticklabels():
                ticklabels.set_fontsize(cb_font_size)
            cb1.ax.yaxis.get_offset_text().set_fontsize(cb_font_size)

    def index_at_height(self, height):
        idx = np.array(np.abs(self.z - height).argmin())
        if idx.size > 1:
            idx = idx[0]
        return idx


def netcdf_from_files(LidarClass, filename, files, channels, measurement_ID):
    # Read the lidar files and select channels
    temp_m = LidarClass(files)
    m = temp_m.subset_by_channels(channels)
    m.get_PT()
    m.info['Measurement_ID'] = measurement_ID
    m.save_as_netcdf(filename)
