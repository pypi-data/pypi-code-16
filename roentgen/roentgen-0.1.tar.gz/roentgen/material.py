"""
"""

from __future__ import absolute_import

import numpy as np
import os
import astropy.units as u
from scipy import interpolate
import roentgen
import warnings

__all__ = ['Material', 'MassAttenuationCoefficient', 'Compound']

_package_directory = roentgen._package_directory
_data_directory = roentgen._data_directory


class Material(object):
    """An object which provides the properties of a material in x-rays

    Parameters
    ----------
    material_str : str
        A string representing a material (e.g. cdte, be, mylar, si)
    thickness : `astropy.units.Quantity`
        The thickness of the material in the optical path.
    density : `astropy.units.Quantity`
        The density of the material. If None use default values.

    Examples
    --------
    >>> from roentgen.material import Material
    >>> import astropy.units as u
    >>> detector = Material('cdte', 500 * u.um)
    >>> thermal_blankets = Material('mylar', 0.5 * u.mm)
    """

    def __init__(self, material_str, thickness, density=None):
        self.name = material_str
        self.thickness = thickness
        self.mass_attenuation_coefficient = MassAttenuationCoefficient(material_str)
        self.long_name = self.mass_attenuation_coefficient.long_name
        if density is None:
            mat = roentgen.material_list[material_str.lower()]
            try:
                self.density = u.Quantity(mat['density']['value'], mat['density']['unit'])
            except:
                warnings.warn("Default density not available. Assuming " + str(u.Quantity(1, 'g/cm^3')))
                self.density = u.Quantity(1, 'g/cm^3')
        else:
            self.density = density

    def __repr__(self):
        """Returns a human-readable representation."""
        txt = '<Material ' + str(self.name) + ' (' + str(self.long_name) + ') '
        txt += str(self.thickness) + ' ' + str(self.density) + '>'
        return txt

    def __add__(self, other):
        if isinstance(other, Material):
            return Compound([self, other])
        elif isinstance(other, Compound):
            return Compound([self] + other.materials)
        else:
            raise ValueError("Can't add <Material> and " + str(other))

    def transmission(self, energy):
        """Provide the transmission fraction (0 to 1).

        Parameters
        ----------
        energy : `astropy.units.Quantity`
            An array of energies in keV
        """
        coefficients = self.mass_attenuation_coefficient.func(energy)
        transmission = np.exp(- coefficients * self.density * self.thickness)
        return transmission

    def absorption(self, energy):
        """Provides the absorption fraction (0 to 1).

        Parameters
        ----------
        energy : `astropy.units.Quantity`
            An array of energies in keV.
        """
        return 1 - self.transmission(energy)


class Compound(object):
    """An object which provides the properties of a compound (i.e.
     many materials) in x-rays.

    Parameters
    ----------
    materials : list
        A list of Material objects

    Examples
    --------
    >>> from roentgen.material import Material
    >>> import astropy.units as u
    >>> detector = Material('cdte', 500 * u.um)
    >>> thermal_blankets = Material('mylar', 0.5 * u.mm)
    """

    def __init__(self, materials):
        self.materials = materials

    def __add__(self, other):
        if isinstance(other, Material):
            return Compound(self.materials + [other])
        elif isinstance(other, Compound):
            return Compound(self.materials + other.materials)
        else:
            raise ValueError("Can't add <Compound> and " + str(other))

    def __repr__(self):
        """Returns a human-readable representation."""
        txt = '<Compound '
        for material in self.materials:
            txt += str(material)
        return txt + '>'

    def transmission(self, energy):
        """Provide the transmission fraction (0 to 1).

        Parameters
        ----------
        energy : `astropy.units.Quantity`
            An array of energies in keV
        """
        transmission = np.ones(len(energy), dtype=np.float)
        for material in self.materials:
            coefficients = material.mass_attenuation_coefficient.func(energy)
            transmission *= np.exp(- coefficients * material.density * material.thickness)
        return transmission

    def absorption(self, energy):
        """Provides the absorption fraction (0 to 1).

        Parameters
        ----------
        energy : `astropy.units.Quantity`
            An array of energies in keV.
        """
        return 1 - self.transmission(energy)


class MassAttenuationCoefficient(object):
    """
    The mass attenuation coefficient

    Parameters
    ----------
    material : str
        A string representing a material (e.g. cdte, be, mylar, si)
    """
    def __init__(self, material):
        # find the material in our list
        mat = roentgen.material_list[material.lower()]
        self.name = mat['symbol']
        self.long_name = mat['name']
        datafile_path = os.path.join(_data_directory, mat['file'])
        data = np.loadtxt(datafile_path, delimiter=',')
        self.energy = u.Quantity(data[:, 0] * 1000, 'keV')
        self.data = u.Quantity(data[:, 1], 'cm^2/g')

        data_energy_kev = np.log10(self.energy.value)
        data_attenuation_coeff = np.log10(self.data.value)
        self._f = interpolate.interp1d(data_energy_kev, data_attenuation_coeff, bounds_error=False, fill_value=0.0)
        self.func = lambda x: u.Quantity(10 ** self._f(np.log10(x.to('keV').value)), 'cm^2/g')


def _get_long_name(material):
    return roentgen.material_list.get(material)['name']
