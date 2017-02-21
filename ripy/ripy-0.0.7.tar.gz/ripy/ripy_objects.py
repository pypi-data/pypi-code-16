import numpy as np
import scipy.interpolate


class Material:
    """Class that contain optical properties of a material"""

    def __init__(self, ri, ec, name=None, meta=None):
        self.name = '' if None else name
        self.meta = {} if None else meta
        # For convenience, allow user to pass a number as ri/ec.
        self._ri = ri
        self._ec = ec

    def get_ri(self, wl, allow_nan=False):
        return self._ri.get_index(wl, allow_nan)

    def get_ec(self, wl, allow_nan=False):
        return self._ec.get_index(wl, allow_nan)

    def set_ri(self, ri):
        self._ri = ri

    def set_ec(self, ec):
        self._ec = ec

    def get_complex_ri(self, wl, allow_nan=False):
        return self.get_ri(wl, allow_nan) - 1j * self.get_ec(wl, allow_nan)

    def clone(self):
        clone = Material(self._ri.clone(), self._ec.clone())
        clone.meta = self.meta
        return clone

    def is_valid(self):
        if self._ec is None or self._ri is None:
            return False
        return self._ec.is_valid() and self._ri.is_valid()


class FormulaIndexData:
    """Formula RefractiveIndex class"""

    def __init__(self, formula, rangeMin, rangeMax, coefficients):
        """

        :param formula:
        :param rangeMin:
        :param rangeMax:
        :param coefficients:
        """
        self.formula = formula
        self.rangeMin = rangeMin
        self.rangeMax = rangeMax
        self.coefficients = coefficients
        self.min_warning = False
        self.max_warning = False

    def get_index(self, wavelength, allow_nan=False):
        """
        :param allow_nan:
        :param wavelength:
        :return: :raise Exception:
        """
        wavelength /= 1000.0 # HACK: Argument assumed to be in nm, table in micro meters
        if allow_nan and (self.rangeMin > wavelength or wavelength > self.rangeMax):
            return np.nan
        elif self.rangeMin > wavelength:
            if not self.min_warning:
                print('WARNING: Wavelength {} less than minimum table value,'
                      ' {} (displayed only once)'.format(wavelength, self.rangeMin))
                self.min_warning = True
            wavelength = self.rangeMin
        elif self.rangeMax < wavelength:
            if not self.max_warning:
                print('WARNING: Wavelength {} greater than maximum table value,'
                      ' {} (displayed only once)'.format(wavelength, self.rangeMax))
                self.max_warning = True
            wavelength = self.rangeMax
        if self.rangeMin <= wavelength <= self.rangeMax:
            formula_type = self.formula
            coeffs = self.coefficients
            n = 0
            if formula_type == 1:  # Sellmeier
                nsq = 1 + coeffs[0]
                g = lambda c1, c2, w: c1 * (w ** 2) / (w ** 2 - c2 ** 2)
                for i in range(1, len(coeffs), 2):
                    nsq += g(coeffs[i], coeffs[i + 1], wavelength)
                n = np.sqrt(nsq)
            elif formula_type == 2:  # Sellmeier-2
                nsq = 1 + coeffs[0]
                g = lambda c1, c2, w: c1 * (w ** 2) / (w ** 2 - c2)
                for i in range(1, len(coeffs), 2):
                    nsq += g(coeffs[i], coeffs[i + 1], wavelength)
                n = np.sqrt(nsq)
            elif formula_type == 3:  # Polynomal
                g = lambda c1, c2, w: c1 * w ** c2
                nsq = coeffs[0]
                for i in range(1, len(coeffs), 2):
                    nsq += g(coeffs[i], coeffs[i + 1], wavelength)
                n = np.sqrt(nsq)
            elif formula_type == 4:  # RefractiveIndex.INFO
                nsq = coeffs[0]
                g = lambda c1, c2, c3, c4, w: c1 * pow(w, c2) / (w ** 2 - pow(c3, c4))
                nsq += g(coeffs[1], coeffs[2], coeffs[3], coeffs[4], wavelength)
                # nsq += g(coeffs[5], coeffs[6], coeffs[7], coeffs[8], wavelength)
                # g = lambda c1, c2, w: c1*pow(w,c2)
                # nsq += g(coeffs[9], coeffs[10]) + g(coeffs[11], coeffs[12])
                # nsq += g(coeffs[13], coeffs[14]) + g(coeffs[15], coeffs[16])
                n = np.sqrt(nsq)
            elif formula_type == 5:  # Cauchy
                g = lambda c1, c2, w: c1 * w ** c2
                n = coeffs[0]
                for i in range(1, len(coeffs), 2):
                    n += g(coeffs[i], coeffs[i + 1], wavelength)
            elif formula_type == 6:  # Gasses
                n = 1 + coeffs[0]
                g = lambda c1, c2, w: c1 / (c2 - w ** (-2))
                for i in range(1, len(coeffs), 2):
                    n += g(coeffs[i], coeffs[i + 1], wavelength)
            elif formula_type == 7:  # Herzberger
                raise FormulaNotImplemented('Herzberger formula not yet implemented')
            elif formula_type == 8:  # Retro
                raise FormulaNotImplemented('Retro formula not yet implemented')
            elif formula_type == 9:  # Exotic
                w2 = wavelength ** 2
                n2 = coeffs[0] + coeffs[1] * w2 / (w2 - coeffs[2]) + coeffs[3] * w2
                n = np.sqrt(n2)
            else:
                raise Exception('Bad formula type')

            return n
        else:
            raise Exception(
                'Wavelength {} is out of bounds. Correct range(um): ({}, {})'.format(wavelength, self.rangeMin,
                                                                                     self.rangeMax))

    def is_valid(self):
        return not 6 < self.formula < 9


class FixedIndexData:
    def __init__(self, value):
        self.value = value

    def get_index(self, wavelength, allow_nan=False):
        return self.value

    def is_valid(self):
        return True


class TabulatedIndexData:
    """Tabulated RefractiveIndex class"""

    def __init__(self, wavelengths, values):
        self.wavelengths = wavelengths
        self.indexes = values
        self.wl_min = np.min(wavelengths)
        self.wl_max = np.max(wavelengths)
        self.min_warning = False
        self.max_warning = False
        self.interpolation = scipy.interpolate.InterpolatedUnivariateSpline(wavelengths, values, k=1)

    def get_index(self, wl, allow_nan=False):
        wl /= 1000.0  # HACK: Argument assumed to be in nm, table in micro meters
        wl_min = np.min(wl)
        wl_max = np.max(wl)
        if allow_nan and (wl_min < self.wl_min or wl_max > self.wl_max):
            return np.nan
        elif wl_min < self.wl_min:
            if not self.min_warning:
                print('WARNING: Wavelength {} less than minimum table value,'
                      ' {} (displayed only once)'.format(wl_min, self.wl_min))
                self.min_warning = True
            return self.indexes[0]
        elif wl_max > self.wl_max:
            if not self.max_warning:
                print('WARNING: Wavelength {} greater than maximum table value,'
                      ' {} (displayed only once)'.format(wl_max, self.wl_max))
                self.max_warning = True
            return self.indexes[-1]
        return self.interpolation(wl)

    def is_valid(self):
        return len(self.indexes) == len(self.wavelengths)


class FormulaNotImplemented(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
