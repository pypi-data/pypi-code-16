import datetime
import glob
import logging
import os

import netCDF4 as netcdf
import numpy as np
from matplotlib import pyplot as plt

# Text file header
header_template = """# System: {0.system}
# Location: {0.location}
# Latitude: {0.latitude}, Longitude: {0.longitude}
# Emission: {0.emission_wavelength}nm, Detection: {0.detection_wavelength}nm
# Evaluation method: {0.evaluation_method}
# Start: {0.start_time:%Y-%m-%d %H:%M:%S}, Stop: {0.stop_time:%Y-%m-%d %H:%M:%S}\n
"""


class OpticalFile:
    ''' An OpticalProfile object represents the content of an earlinet optical file.
    A simple use::
    
    # Read the file name
    my_profile = OpticalProfile(filename)
    
    # Plot the file
    my_profile.plot()
    
    You can change the range resolution of the file by setting resample = True, and by specifying additional parameters::
    
    # All extra parameters are optional. Defaults are 30-15000 m, 60m resolution, linear resample
    my_profile = OpticalProfile(filename, resample = True, min_altitude = 100, max_altitude = 10000, dz = 10, resample_kind = 'linear')
    
    Resampling can be 'linear' ,'nearest', 'zero', 'slinear', 'quadratic, 'cubic' or as an integer specifying 
    the order of the spline interpolator to use. Default is 'linear'.
    
    See http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html for details.
    
    Several profiles can be imported and an average will be calculated. The files have to be in the same vertical resolution
    or they must be resampled. To combine files you have do for example::
    
    # Read the files one by one
    my_profile_1 = OpticalProfile(filename1)
    my_profile_2 = OpticalProfile(filename2)
    
    # Create an empty profile
    combined_profile = OpticalProfile()
    
    # Combine the files
    combined_profile.combine_files([my_profile_1, my_profile_2], variables = ['a', 'b'])
    '''

    spec_global_attributes = ['Location', 'System', 'Latitude_degrees_north', 'Longitude_degrees_east',
                              'Altitude_meter_asl', 'EmissionWavelength_nm', 'DetectionWavelength_nm', 'DetectionMode',
                              'ZenithAngle_degrees', 'ShotsAveraged', 'ResolutionRaw_meter',
                              'ResolutionEvaluated', 'StartDate', 'StartTime_UT', 'StopTime_UT', 'EvaluationMethod',
                              'InputParameters', 'Comments']

    spec_data_variables = ['Backscatter', 'Extinction', 'VolumeDepol', 'ParticleDepol', ]

    plot_axis_labels = {'Backscatter': r'Backscatter coefficient [$\mathrm{m^{-1}sr^{-1}}$]',
                        'Extinction': r'Extinction coefficient [$\mathrm{m^{-1}}$]',
                        'VolumeDepol': r'Linear volume depolarization ratio',
                        'ParticleDepol': r'Linear particle depolarization ratio'}


    def __init__(self, input_file=None, resample=False, min_altitude=30, max_altitude=15000, dz=60,
                 resample_kind='linear'):

        self.file_path = "<File not saved>"
        self.resample = resample

        if resample:
            self.min_altitude = min_altitude
            self.max_altitude = max_altitude
            self.dz = dz
            self.resample_kind = resample_kind

        self.variables = None

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
        self._read_extra_parameters()
        self._read_dates()
        _ = self._read_variable("Altitude")

        self._create_convenience_properties()

        if self.resample:
            self.read_resample_data(kind=self.resample_kind)
        else:
            self._read_data_variables()

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

    def _read_extra_parameters(self):
        """ Read parameters from the file. """
        try:
            self.analysis_software_version = self.file.__dict__['__AnalysisSoftwareVersion']
            self.measurement_id = self.file.__dict__['__MeasurementNumber']
        except:
            logging.debug("Could not read extra parameters AnalysisSoftwareVersion of Measurement Number.")

    def _read_data_variables(self):
        """ Read the available data variables in the files.

        Assumes that self.file is the open NetCDF dataset.
        """
        available_variables = []
        for variable_name in self.spec_data_variables:
            netcdf_variable = self._read_variable(variable_name)
            if netcdf_variable is not None:
                available_variables.append(variable_name)
                error_variable_name = "Error" + variable_name
                _ = self._read_variable(error_variable_name)

        self.data_variables = available_variables

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
        start_string = "%i %06i" % (self.file.StartDate, self.file.StartTime_UT)
        stop_string = "%i %06i" % (self.file.StartDate, self.file.StopTime_UT)
        date_pattern = "%Y%m%d %H%M%S"

        start_datetime = datetime.datetime.strptime(start_string, date_pattern)
        stop_datetime = datetime.datetime.strptime(stop_string, date_pattern)

        if start_datetime > stop_datetime:
            stop_datetime = stop_datetime + datetime.timedelta(hours=24)

        self.start_datetime = start_datetime
        self.stop_datetime = stop_datetime

        self.duration = stop_datetime - start_datetime
        self.middle_time = start_datetime + self.duration / 2

    def _create_convenience_properties(self):
        """ Create additional properties and aliases, to improve the object's interface."""
        self.z0 = self.Altitude_meter_asl
        self.z = self.Altitude

        self.no_points = len(self.file.dimensions['Length'])

    def combine_files(self, filelist, check_proximity=True, variables=['a', 'b']):
        consecutive = True
        filelist.sort()

        # If asked, check if the files contain consecutive measurements.
        if check_proximity:
            consecutive = self.check_consecutive(filelist)
            if not consecutive:
                raise IOError('The input files are not consecutive')

        # Check that all files contain the needed variables
        for current_file in filelist:
            for variable in variables:
                if not hasattr(current_file, variable):
                    raise IOError('File %s does not contain the \"%s\" variable.' % (self.file_path, variable))

        # Check if all files have the same z values
        first_z = filelist[0].z
        for current_file in filelist:
            if not np.array_equal(first_z, current_file.z):
                raise ValueError('Not all files have the same z values')
        self.z = first_z

        # Calculate the weight
        for variable in variables:
            error_name = variable + '_error'
            weights = self.calculate_weights(filelist, variable)

            values = np.ma.array([getattr(fl, variable) for fl in filelist])
            # weights = np.ones(len(values))
            value_errors = np.ma.array([getattr(fl, error_name) for fl in filelist])
            variable_value = np.ma.average(values, weights=weights, axis=0)
            variable_errors_square = np.ma.average(value_errors ** 2, weights=weights ** 2, axis=0)
            # Divide the Sum(wi^2*s^2) with N before taking the root
            # Find how many errors where masked
            errors_masked = [ve.mask for ve in value_errors if getattr(ve, 'mask', None) != None]
            n_without_errors = np.ma.sum(errors_masked, axis=0)
            # The rest of the errors where not masked
            n_with_errors = len(value_errors) - n_without_errors
            variable_errors_square = variable_errors_square / n_with_errors
            setattr(self, variable, variable_value)
            setattr(self, error_name, variable_errors_square ** 0.5)

        # Check if z0 is equal to all the files. If yes add it to the new file
        z0_list = [fl.z0 for fl in filelist]
        if len(set(z0_list)) == 1:
            self.z0 = z0_list[0]

        # If the measurements are consecutive then define the combined start and stop time
        if check_proximity:
            self.start_datetime = filelist[0].start_datetime
            self.stop_datetime = filelist[-1].stop_datetime
            self.duration = self.stop_datetime - self.start_datetime
        else:
            self.duration = np.sum([fl.duration for fl in filelist])

        self.variables = variables

        evaluation_method_list = [fl.evaluation_method for fl in filelist]
        evaluation_methods = list(set(evaluation_method_list))
        if len(evaluation_methods) == 1:
            self.evaluation_method = evaluation_methods[0]
        else:
            self.evaluation_method = ', '.join(evaluation_methods)

    def check_consecutive(self, filelist, threshold=2):
        ''' Checks if files in filelist are consecutive.
        Threshold is in minutes '''

        filelist.sort()
        time_limit = datetime.timedelta(minutes=threshold)
        for (n, current_file) in enumerate(filelist[:-1]):
            if (current_file.stop_time > filelist[n + 1].start_time) or \
                    (current_file.stop_time < filelist[n + 1].start_time - time_limit):
                return False

        # If no error detected
        return True

    def calculate_weights(self, filelist, variable):
        durations = np.array([fl.duration.seconds for fl in filelist])
        total_duration = float(np.sum(durations))
        weights = durations / total_duration
        return weights

    def read_resample_data(self, kind):

        zold = self.file.variables['Altitude'][:]
        self.variables = []
        # Create the new z array
        self.z = np.arange(self.min_altitude, self.max_altitude, self.dz)

        if 'Extinction' in self.file.variables.keys():

            a = self.file.variables['Extinction'][:]
            a_err = self.file.variables['ErrorExtinction'][:]
            a_mask = getattr(a, 'mask', None)

            if a_mask is not None:
                if a.count():
                    a_new = self.change_z(zold, self.z, a, kind=kind)
                    a_new_err = self.change_z(zold, self.z, a_err, kind=kind)
                    masked_ones = np.ones(len(a))
                    masked_ones[a_mask] = np.Inf
                    new_masked_ones = self.change_z(zold, self.z, masked_ones)
                    a_new = np.ma.masked_array(a_new, mask=new_masked_ones.mask)
                    a_new_err = np.ma.masked_array(a_new_err, mask=new_masked_ones.mask)
                else:
                    a_new = np.ma.masked_equal(np.ones(len(self.z)), 1)
                    a_new_err = np.ma.masked_equal(np.ones(len(self.z)), 1)
            else:
                a_new = self.change_z(zold, self.z, a, kind=kind)
                a_new_err = self.change_z(zold, self.z, a_err, kind=kind)

            self.a = a_new
            self.a_error = a_new_err
            self.alpha_points = np.ma.count(self.a)
            self.variables.append('a')

        if 'Backscatter' in self.file.variables.keys():
            b = self.file.variables['Backscatter'][:]
            b_err = self.file.variables['ErrorBackscatter'][:]
            b_mask = getattr(b, 'mask', None)

            if b_mask is not None:
                if b.count():
                    b_new = self.change_z(zold, self.z, b, kind=kind)
                    b_new_err = self.change_z(zold, self.z, b_err, kind=kind)
                    masked_ones = np.ones(len(b))
                    masked_ones[b_mask] = np.Inf
                    new_masked_ones = self.change_z(zold, self.z, masked_ones)
                    b_new = np.ma.masked_array(b_new, mask=new_masked_ones.mask)
                    b_new_err = np.ma.masked_array(b_new_err, mask=new_masked_ones.mask)
                else:  # if no unmased element is found in b
                    b_new = np.ma.masked_equal(np.ones(len(self.z)), 1)
                    b_new_err = np.ma.masked_equal(np.ones(len(self.z)), 1)
            else:
                b_new = self.change_z(zold, self.z, b, kind=kind)
                b_new_err = self.change_z(zold, self.z, b_err, kind=kind)

            self.b = b_new
            self.b_error = b_new_err

            self.beta_points = np.ma.count(self.b)
            self.variables.append('b')

        self.z0 = np.float(self.file.Altitude_meter_asl)

    def _index_at_height(self, height):
        idx = np.array(np.abs(self.z - height).argmin())
        if idx.size > 1:
            idx = idx[0]
        return idx

    def _indices_at_height_interval(self, zmin, zmax):
        idxs = np.where((self.z > zmin) & (self.z < zmax))[0]
        return idxs

    def mean_at_height_interval(self, zmin, zmax, variable='b'):
        idxs = self._indices_at_height_interval(zmin, zmax)
        var = getattr(self, variable)
        mean_value = np.mean(var[idxs])
        return mean_value

    def max_at_height_interval(self, zmin, zmax, variable='b'):
        idxs = self._indices_at_height_interval(zmin, zmax)
        var = getattr(self, variable)
        max_value = np.max(var[idxs])
        return max_value

    def height_at_max(self, zmin, zmax, variable=None):
        search_variable = variable or self.variables[0]
        idxs = self._indices_at_height_interval(zmin, zmax)
        var = getattr(self, search_variable)
        range_index = var[idxs].argmax()
        total_index = idxs[0] + range_index
        return self.z[total_index]

    def change_z(self, z_old, z_new, values, kind='linear'):

        mask = getattr(values, 'mask', None)
        if mask is not None:
            non_masked = ~mask
        else:
            non_masked = [True, ] * len(values)

        non_masked = np.array(non_masked)
        x = z_old[non_masked]
        y = values[non_masked]
        f_vals = interp1d(x, y, bounds_error=False, kind=kind)
        new_values = f_vals(z_new)
        new_values = np.ma.masked_invalid(new_values)
        return new_values

    def calculate_aod(self):
        min_alpha_idx = np.ma.flatnotmasked_edges(self.a)[0]

        aod_to_ground = self.a[min_alpha_idx] * (self.z[min_alpha_idx] - self.z0)

        if (self.z[min_alpha_idx] - self.z0) > 1000:
            print "Warning: The min altitude is %s. Interpolation to the ground could be wrong." % self.z[0]

        difs = list(set(np.diff(self.z)))
        difs.sort()
        if len(difs) > 2:
            print "Warning: Irregular altitude range. len(set(diffs)): %s " % len(difs)
            print difs

        if abs(difs[0] - 60) > 5:
            raise ValueError("Strange altitude difference. Check manually. Difs[0] %s " % difs[0])

        # Calculate aod with a fix step of 60 meters. This will avoid interpolation
        # between values at different aerosol layers.

        # aod_layers = np.trapz(self.a, dx = 1) * 60 # avoids strange warning
        aod_layers = np.trapz(self.a, self.z)
        aod = aod_to_ground + aod_layers
        return aod

    def calculate_aod_2(self):
        min_alpha_idx = np.ma.flatnotmasked_edges(self.a)[0]

        aod_to_ground = self.a[min_alpha_idx] * (self.z[min_alpha_idx] - self.z0)

        aod_layers = np.trapz(self.a, self.z)
        aod = aod_to_ground + aod_layers
        return aod

    def save_as_txt(self, file_base=None, file_extension='txt', output_dir='.', fill_value=-9999):
        """ Save the content of the file as txt """

        # If no filename provided, use netcdf fileanme as a basis
        if not file_base:
            file_base = os.path.basename(self.file_path).replace('.', '_')

        for variable in self.variables:
            values = getattr(self, variable)
            try:
                errors = getattr(self, "%s_error" % variable)
            except:
                errors = np.ma.masked_all_like(values)

            output_array = np.ma.vstack([self.z, values, errors]).transpose()
            output_array = output_array.filled(fill_value)

            # If more than one variables in the file, add it in the filename
            if len(self.variables) == 1:
                current_file = "%s.%s" % (file_base, file_extension)
            else:
                current_file = "%s_%s.%s" % (file_base, variable, file_extension)

            output_path = os.path.join(output_dir, current_file)
            f = open(output_path, 'w')

            # Write file header
            f.write(header_template.format(self))
            f.write('# Altitude(a.s.l.)\t           %s         Errors\n' % variable)
            f.write('# ----------------------------------------------\n')

            np.savetxt(f, output_array, fmt=("%16.2f", "%10E", "%10E"), delimiter='\t')

    def plot_data(self, z_min=0, z_max=20, errorevery=3, fig_height=6, ax_width=5, fig_width=None, grid=False, add_suptitle=True):

        no_variables = len(self.data_variables)

        if not fig_width:
            fig_width = no_variables * ax_width

        fig = plt.figure(figsize=(fig_width, fig_height))

        for n, variable_name in enumerate(self.data_variables):
            if n==0:
                reference_axis = plt.subplot(1,  no_variables, 1)
                ax = reference_axis
                legend = True  # Show legend only on first plot
            else:
                ax = plt.subplot(1, no_variables, n + 1, sharey=reference_axis)
                legend = False

            self.draw_data_variable(ax, variable_name, z_min=z_min, z_max=z_max, errorevery=errorevery, grid=grid,
                                    legend=legend, custom_title=variable_name)

        if add_suptitle:
            suptitle = "{0.System} at {0.EmissionWavelength_nm}nm / {0.start_datetime:%Y-%m-%d}\n{0.Location} ({0.Latitude_degrees_north:4.1f}N, {0.Longitude_degrees_east:4.1f}E, {0.Altitude_meter_asl}m a.s.l.)".format(self)
            plt.suptitle(suptitle)

        plt.tight_layout()
        plt.subplots_adjust(wspace=0.2)

        if add_suptitle:
            plt.subplots_adjust(top=1 - (0.9 / fig_height))  # 0.9 inches from top

        plt.show()

    def plot_data_variable(self, variable_name, z_min=0, z_max=20, errorevery=3, figsize=(6, 6), custom_title=None,
                           custom_ylabel=None, legend=True, grid=False, add_suptitle=True):

        fig = plt.figure(figsize=figsize)
        ax = plt.subplot(111)

        self.draw_data_variable(ax, variable_name, z_min=z_min, z_max=z_max, errorevery=errorevery,
                                custom_title=custom_title, custom_ylabel=custom_ylabel, legend=legend, grid=grid)

        if add_suptitle:
            suptitle = "{0.System} at {0.EmissionWavelength_nm}nm / {0.start_datetime:%Y-%m-%d}\n{0.Location} ({0.Latitude_degrees_north:4.1f}N, {0.Longitude_degrees_east:4.1f}E, {0.Altitude_meter_asl}m a.s.l.)".format(
            self)
            plt.suptitle(suptitle)

        plt.tight_layout()

        if add_suptitle:
            plt.subplots_adjust(top=1 - (0.9 / figsize[1]))  # 0.9 inches from top

        plt.show()

        return fig

    def draw_data_variable(self, ax, variable_name, z_min=0, z_max=20, errorevery=3, custom_title=None,
                           custom_ylabel=None, legend=True, grid=False):

        min_idx = self._index_at_height(z_min * 1000.)
        max_idx = self._index_at_height(z_max * 1000.)

        error_variable_name = "Error" + variable_name
        data_variable = getattr(self, variable_name)
        error_variable = getattr(self, error_variable_name)

        plt.errorbar(data_variable[min_idx:max_idx],
                     self.z[min_idx:max_idx] / 1000.,
                     xerr=error_variable[min_idx:max_idx],
                     errorevery=errorevery,
                     label=self.start_datetime.strftime('%H:%M:%S'))

        plt.ylim(z_min, z_max)

        plt.ticklabel_format(style='sci', axis='x', scilimits=(-1, 1))

        if custom_ylabel:
            plt.ylabel(custom_ylabel)
        else:
            plt.ylabel('Heigh a.s.l. [km]')

        plt.xlabel(self.plot_axis_labels[variable_name])

        if custom_title:
            plt.title(custom_title)
        else:
            plt.title('%s' % variable_name)

        if legend:
            ax.legend()

        plt.grid(grid)

    def get_variable_plot_name(self, variable_name):
        image_base = self.file_name.replace('.', '_')
        image_filename = "%s_%s.png" % (image_base, variable_name.lower())
        return image_filename

    def __eq__(self, other):
        if (self.start_datetime == other.start_time) and (self.stop_datetime == other.stop_time):
            return True
        else:
            return False

    def __lt__(self, other):
        if (self.start_datetime < other.start_time):
            return True
        else:
            return False

    def __le__(self, other):
        if (self.start_datetime <= other.start_time):
            return True
        else:
            return False

    def __ne__(self, other):
        if (self.start_datetime != other.start_time) or (self.stop_datetime != other.stop_time):
            return True
        else:
            return False

    def __gt__(self, other):
        if (self.start_datetime > other.start_time):
            return True
        else:
            return False

    def __ge__(self, other):
        if (self.start_datetime >= other.start_time):
            return True
        else:
            return False


def combine_files(search_string, variables=['a', 'b'], check_proximity=True, resample=True):
    files = glob.glob(search_string)
    filelist = [OpticalFile(fl, resample=resample) for fl in files]
    new_profile = OpticalFile()
    new_profile.combine_files(filelist, variables=variables, check_proximity=check_proximity)
    return new_profile
