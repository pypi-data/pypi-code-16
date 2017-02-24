import datetime
import os
import logging

import netCDF4 as netcdf
import numpy as np
from matplotlib import pyplot as plt

plot_captions = {'mean_elPP': r'Parallel ',
                 'mean_elCP': r'Cross'}


class PreprocessedFile:
    ''' Reads a SCC preprocessed file. Currently assumes only one scan angle.
    '''

    spec_global_attributes = ['Location', 'System', 'Latitude_degrees_north',
                              'Longitude_degrees_east', 'Altitude_meter_asl', 'Measurement_ID',
                              'Measurement_Start_Date', 'Measurement_Date_Format', 'Measurement_Start_Time_UT',
                              'Measurement_Time_Format', 'Comments', 'Overlap_File_Name', 'LR_File_Name',
                              'SCCPreprocessingVersion']

    spec_data_variables = ['elT', 'elTnr', 'elTfr', 'elPR', 'elPRnr', 'elPRfr', 'elPT', 'elPTnr', 'elPTfr',
                           'vrRN2', 'vrRN2nr', 'vrRN2fr']

    spec_technical_variables = ['altitude_resolution', 'range_resolution', 'laser_pointing_angle',
                                'emission_wavelength', 'detection_wavelength', 'laser_pointing_angle_of_profiles',
                                'shots', 'start_time', 'stop_time', 'LR_Input', 'overlap_correction', 'cloud_flag',
                                'Depolarization_Calibration_Type']

    spec_molecular_variables = ['Elastic_Mol_Extinction', 'LR_Mol', 'Emission_Wave_Mol_Trasmissivity',
                                'Detection_Wave_Mol_Trasmissivity', 'Molecular_Linear_Depolarization_Ratio']

    spec_polarization_variables = ['G_T', 'H_T', 'G_R', 'H_R', 'Polarization_Channel_Gain_Factor',
                                   'Polarization_Channel_Gain_Factor_Correction',
                                   'G_T_Near_Range', 'H_T_Near_Range', 'G_R_Near_Range', 'H_R_Near_Range',
                                   'Polarization_Channel_Gain_Factor_Near_Range',
                                   'Polarization_Channel_Gain_Factor_Correction_Near_Range',
                                   'G_T_Far_Range', 'H_T_Far_Range', 'G_R_Far_Range', 'H_R_Far_Range',
                                   'Polarization_Channel_Gain_Factor_Far_Range',
                                   'Polarization_Channel_Gain_Factor_Correction_Far_Range', ]

    def __init__(self, input_file=None):
        self.file_path = "<File not saved>"

        if input_file:
            self.load_file(input_file)

    def load_file(self, input_file):

        try:
            self.file = netcdf.Dataset(input_file)
        except:
            raise IOError('Could not read file %s' % input_file)

        self.file_path = input_file
        self.file_name = os.path.basename(input_file)

        self._read_global_attributes()
        self._read_data_variables()
        self._read_technical_variables()
        self._read_molecular_variables()
        self._read_polarization_variables()
        self._read_dates()
        self._create_convenience_properties()

        self.file.close()

    def _read_global_attributes(self):
        """ Read the global attributes from the files.

        Assumes that self.file is the open NetCDF dataset.
        """

        for attribute_name in self.spec_global_attributes:
            # Check if the specific attribute is actually present in the file.
            attribute_value = getattr(self.file, attribute_name, None)
            if attribute_value is not None:
                setattr(self, attribute_name, attribute_value)

    def _read_data_variables(self):
        """ Read the available data variables in the files.

        Assumes that self.file is the open NetCDF dataset.
        """
        available_variables = []
        for variable_name in self.spec_data_variables:
            netcdf_variable = self._read_variable(variable_name)
            if netcdf_variable is not None:
                available_variables.append(variable_name)
                error_variable_name = variable_name + "_err"
                _ = self._read_variable(error_variable_name)

        self.data_variables = available_variables

    def _read_technical_variables(self):
        """ Read the available technical variables in the files.

        Assumes that self.file is the open NetCDF dataset.
        """
        available_variables = []
        for variable_name in self.spec_technical_variables:
            netcdf_variable = self._read_variable(variable_name)
            if netcdf_variable is not None:
                available_variables.append(variable_name)

        self.technical_variables = available_variables

    def _read_molecular_variables(self):
        """ Read the available technical variables in the files.

        Assumes that self.file is the open NetCDF dataset.
        """
        available_variables = []
        for variable_name in self.spec_molecular_variables:
            netcdf_variable = self._read_variable(variable_name)
            if netcdf_variable is not None:
                available_variables.append(variable_name)

        self.molecular_variables = available_variables

    def _read_polarization_variables(self):
        """ Read the available polarization variables in the files.

        Assumes that self.file is the open NetCDF dataset.
        """
        available_variables = []
        for variable_name in self.spec_polarization_variables:
            netcdf_variable = self._read_variable(variable_name)
            if netcdf_variable is not None:
                available_variables.append(variable_name)
                statistical_error_name = variable_name + "_Statistical_Err"
                _ = self._read_variable(statistical_error_name)
                systematic_error_name = variable_name + "_Systematic_Err"
                _ = self._read_variable(systematic_error_name)

        self.polarization_variables = available_variables

    def _read_variable(self, variable_name):
        """ Read a variable, and assign it as a object property. """
        netcdf_variable = self.file.variables.get(variable_name, None)

        if netcdf_variable is not None:
            data_values = netcdf_variable[:]
            if isinstance(data_values, np.ndarray):
                # If an array variable, force masked array, even if files were created with fill on.
                dtype_str = netcdf_variable.dtype.str[-2:]  # If strings is "<f8", keep only "f8"
                default_fill_value = netcdf.default_fillvals[dtype_str]
                data_values = np.ma.masked_equal(data_values, default_fill_value)

            setattr(self, variable_name, data_values)

        return netcdf_variable

    def _read_dates(self):
        start_string = "%s %s" % (self.Measurement_Start_Date,
                                  self.Measurement_Start_Time_UT)
        date_pattern = "%Y%m%d %H%M%S"

        start_datetime = datetime.datetime.strptime(start_string, date_pattern)

        profile_start = [start_datetime + datetime.timedelta(seconds=float(s))
                         for s in self.start_time]

        profile_stop = [start_datetime + datetime.timedelta(seconds=float(s))
                        for s in self.stop_time]

        self.start_datetime = start_datetime
        self.stop_datetime = profile_stop[-1]

        self.duration = self.stop_datetime - self.start_datetime
        self.profile_start = profile_start
        self.profile_stop = profile_stop
        self.middle_time = self.start_datetime + self.duration / 2

    def _create_convenience_properties(self):
        """ Create additional properties and aliases, to improve the object's interface."""
        self.z0 = self.Altitude_meter_asl
        self.dz = self.altitude_resolution

        self.no_points = len(self.file.dimensions['points'])

        # Range
        self.R = self.range_resolution[0] * np.arange(self.no_points) + self.range_resolution[0] / 2.

        # Altitude
        self.z = self.z0 + self.dz[0] * np.arange(self.no_points) + self.dz[0] / 2.

    def molecular_attenuated_backscatter(self, variable_name):
        backscatter = self.Elastic_Mol_Extinction[0, :] / self.LR_Mol # Assume only one scanning angle.

        if variable_name[0:2] == 'el':
            transmissivity = self.Emission_Wave_Mol_Trasmissivity[0, :] **2  # Assume only one scanning angle.
            logging.debug("Calculating transmissivity for elastic variable.")
        else:
            transmissivity = self.Emission_Wave_Mol_Trasmissivity[0, :] * self.Detection_Wave_Mol_Trasmissivity[0, :]
            logging.debug("Calculating transmissivity for in-elastic variable.")

        attenuated_backscatter = backscatter * transmissivity
        return attenuated_backscatter

    def get_normalized_data_variable(self, variable_name, zmin, zmax):

        idxs = self._indices_at_height_interval(zmin, zmax)

        variable, variable_error = self.get_data_variable(variable_name)

        molecular_backscatter = self.molecular_attenuated_backscatter(variable_name)

        # Get the normalization constant for each profile separately
        normalization_constant = np.mean(molecular_backscatter[None, idxs] / variable[:, idxs], axis=1)

        normalized_variable = variable * normalization_constant[:, None]
        normalized_errors = variable_error * normalization_constant[:, None]

        return normalized_variable, normalized_errors

    def get_data_variable(self, variable_name):
        error_variable_name = variable_name + '_err'
        data_variable = getattr(self, variable_name)
        error_variable = getattr(self, error_variable_name)
        return data_variable, error_variable

    def _index_at_height(self, height):
        idx = np.array(np.abs(self.z - height).argmin())
        if idx.size > 1:
            idx = idx[0]
        return idx

    def _index_at_range(self, range):
        idx = np.array(np.abs(self.R - range).argmin())
        if idx.size > 1:
            idx = idx[0]
        return idx

    def _indices_at_height_interval(self, zmin, zmax):
        idxs = np.where((self.z > zmin) & (self.z < zmax))[0]
        return idxs

    def get_variable_plot_name(self, variable_name):
        image_filename = self.file_name.replace('.nc', '_%s.png' % variable_name)
        return image_filename

    @property
    def has_polarization(self):
        return len(self.polarization_variables) > 0

    def plot_data(self, r_min=0, r_max=20, v_min=None, v_max=None, errorevery=3, fig_width=9, ax_height=4, fig_height=None, grid=False, log=False, normalized=False, norm_min=7, norm_max=8):

        no_variables = len(self.data_variables)
        if not fig_height:
            fig_height = no_variables * ax_height

        fig = plt.figure(figsize=(fig_width, fig_height))

        for n, variable_name in enumerate(self.data_variables):
            if n==0:
                reference_axis = plt.subplot(no_variables, 1, 1)
                ax = reference_axis
                legend = True  # Show legend only on first plot
            else:
                ax = plt.subplot(no_variables, 1, n + 1, sharex=reference_axis)
                legend = False

            self.draw_data_variable(ax, variable_name, r_min=r_min, r_max=r_max, v_min=v_min, v_max=v_max, errorevery=errorevery, grid=grid,
                                    legend=legend, custom_title=variable_name, log=log, normalized=normalized, norm_min=norm_min, norm_max=norm_max)

        suptitle = "{0.Measurement_ID} / {0.System} / {0.start_datetime:%Y-%m-%d}\n{0.Location} ({0.Latitude_degrees_north}N, {0.Longitude_degrees_east}E, {0.Altitude_meter_asl}m a.s.l.)".format(self)
        plt.suptitle(suptitle)
        plt.tight_layout()
        plt.subplots_adjust(top=1 - (0.9 / fig_height))  # 0.9 inches from top

        plt.show()

    def plot_data_variable(self, variable_name, r_min=0, r_max=20, v_min=None, v_max=None, errorevery=3, figsize=(9, 5), custom_title=None,
                           custom_xlabel=None, legend=True, grid=False, add_suptitle=True, log=False, normalized=False, norm_min=7, norm_max=8):

        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(111)
        self.draw_data_variable(ax, variable_name, r_min=r_min, r_max=r_max, v_min=v_min, v_max=v_max, errorevery=errorevery,
                                custom_title=custom_title, custom_xlabel=custom_xlabel, legend=legend, grid=grid, log=log,
                                normalized=normalized, norm_min=norm_min, norm_max=norm_max)

        if add_suptitle:
            suptitle = "{0.Measurement_ID} / {0.System} / {0.start_datetime:%Y-%m-%d}\n{0.Location} ({0.Latitude_degrees_north}N, {0.Longitude_degrees_east}E, {0.Altitude_meter_asl}m a.s.l.)".format(
                self)
            plt.suptitle(suptitle)

        plt.tight_layout()

        if add_suptitle:
            plt.subplots_adjust(top=1 - (0.9 / figsize[1]))  # 0.9 inches from top

        plt.show()

        return fig

    def draw_data_variable(self, ax, variable_name, r_min=0, r_max=20, v_min=None, v_max=None, errorevery=3, custom_title=None,
                           custom_xlabel=None, legend=True, grid=False, log=False, normalized=False, norm_min=7, norm_max=8):

        min_idx = self._index_at_range(r_min * 1000.)
        max_idx = self._index_at_range(r_max * 1000.)

        if normalized:
            data_variable, error_variable = self.get_normalized_data_variable(variable_name, norm_min*1000., norm_max*1000.)
        else:
            data_variable, error_variable = self.get_data_variable(variable_name)

        plt.ticklabel_format(style='sci', axis='y', scilimits=(-1, 1))

        if log:
            data_label = "$log_{10}(%s)$" % variable_name
            plt.yscale('log')
        else:
            data_label = variable_name

        for n, profile_time in enumerate(self.profile_start):
            plt.errorbar(self.R[min_idx:max_idx] / 1000.,
                         data_variable[n, min_idx:max_idx],
                         yerr=error_variable[n, min_idx:max_idx],
                         label=profile_time.strftime('%H:%M:%S'),
                         errorevery=errorevery)

        if normalized:
            molecular_backscatter = self.molecular_attenuated_backscatter(variable_name)
            plt.plot(self.R[min_idx:max_idx] / 1000., molecular_backscatter[min_idx:max_idx], '--', label='Molecular atmosphere', zorder=10)  # Plot on top.

        plt.xlim(r_min, r_max)
        plt.ylim(v_min, v_max)

        if custom_xlabel:
            plt.xlabel(custom_xlabel)
        else:
            plt.xlabel('Range [km]')

        plt.ylabel(data_label)

        if custom_title:
            plt.title(custom_title)
        else:
            plt.title('%s' % variable_name)

        if legend:
            ax.legend()

        plt.grid(grid)



    def __eq__(self, other):
        if (self.start_datetime == other.start_datetime) and (self.stop_datetime == other.stop_datetime):
            return True
        else:
            return False

    def __lt__(self, other):
        if (self.start_datetime < other.start_datetime):
            return True
        else:
            return False

    def __le__(self, other):
        if (self.start_datetime <= other.start_datetime):
            return True
        else:
            return False

    def __ne__(self, other):
        if (self.start_datetime != other.start_datetime) or (self.stop_datetime != other.stop_datetime):
            return True
        else:
            return False

    def __gt__(self, other):
        if (self.start_datetime > other.start_datetime):
            return True
        else:
            return False

    def __ge__(self, other):
        if (self.start_datetime >= other.start_datetime):
            return True
        else:
            return False
