from __future__ import division, print_function

import collections
import numbers

import numpy as np
import scipy.interpolate
import scipy.optimize
from scipy import inf


# region Stack classes

class Stack(list):
    """Class that represent a stack of layers"""

    def __init__(self):
        # Per default, the stack is planar and surrounded by (perfect) vacuum.
        super(Stack, self).__init__()
        self.left = Material(1, 0)
        self.right = Material(1, 0)

    def assemble(self):
        # Add surrounding layers.
        stack = [Layer(self.left, inf)]
        stack.extend(self)
        stack.append(Layer(self.right, inf))
        return stack

    def clone(self):
        s = Stack()
        s.left = self.left.clone()
        s.right = self.right.clone()
        for layer in self:
            s.append(layer.clone())
        return s


class Layer:
    """Class that represents a layer"""

    def __init__(self, mat, d):
        self.material = mat
        self.depth = d

    def clone(self):
        return Layer(self.material.clone(), self.depth)


# endregion

# region Material classes

class Material:
    """Class that contain optical properties of a material"""

    def __init__(self, ri, ec, name=None, meta=None):
        self.name = '' if None else name
        self.meta = {} if None else meta
        # For convenience, allow user to pass a number as ri/ec.
        self._ri = FixedIndex(ri) if isinstance(ri, numbers.Number) else ri
        self._ec = FixedIndex(ec) if isinstance(ec, numbers.Number) else ec

    def get_ri(self, lmb):
        return self._ri.get_index(lmb)

    def get_ec(self, lmb):
        return self._ec.get_index(lmb)

    def set_ri(self, ri):
        self._ri = FixedIndex(ri) if isinstance(ri, numbers.Number) else ri

    def set_ec(self, ec):
        self._ec = FixedIndex(ec) if isinstance(ec, numbers.Number) else ec

    def get_complex_ri(self, lmb):
        return self.get_ri(lmb) - 1j * self.get_ec(lmb)

    def clone(self):
        clone = Material(self._ri.clone(), self._ec.clone())
        clone.meta = self.meta
        return clone


class MixMaterial:
    """Class that contain optical properties of an Effective Medium Approximation (EMA) material"""

    def __init__(self, materials, fractions, model=None, name=None, meta=None):
        self.name = name
        self.meta = meta
        self.materials = materials
        self.fractions = fractions
        self._cache = {}
        self.model = model if model is not None else self.average_model

    def get_ri(self, lmb):
        self._validate_cache(lmb)
        return np.real(self._cache[lmb])

    def get_ec(self, lmb):
        self._validate_cache(lmb)
        return np.imag(self._cache[lmb])

    def get_complex_ri(self, lmb):
        self._validate_cache(lmb)
        return self._cache[lmb]

    def _validate_cache(self, lmb):
        if lmb in self._cache:
            return
        self._cache[lmb] = self.model(self.materials, self.fractions, lmb)

    @staticmethod
    def average_model(mats, fracs, lmb):
        return np.average([mat.get_complex_ri(lmb) for mat in mats], weights=fracs)

    @staticmethod
    def bruggemann_model(mats, fracs, lmb):
        idxs = [mat.get_complex_ri(lmb) for mat in mats]
        guess = np.average([mat.get_complex_ri(lmb) for mat in mats], weights=fracs)

        def obj(ne):
            val = np.sum([fracs[i] * (idx ** 2 - ne ** 2) / (idx ** 2 + 2 * ne ** 2) for i, idx in enumerate(idxs)])
            return abs(val) ** 2

        result = scipy.optimize.minimize(obj, guess)
        return result['x'][0]

    def clone(self):
        return MixMaterial(self.materials, self.fractions, self.name, self.meta)


class FixedIndex:
    """ Fixed index class"""

    def __init__(self, index):
        self.index = index

    def get_index(self, lmb):
        return np.ones(len(lmb)) * self.index if isinstance(lmb, collections.Sized) else self.index

    def clone(self):
        return FixedIndex(self.index)


class TabulatedIndex:
    """ Tabulated index class"""

    def __init__(self, lmbs, idxs):
        self.wavelengths = lmbs
        self.indexes = idxs
        self.lmb_min = np.min(lmbs)
        self.lmb_max = np.max(lmbs)
        self.min_warning = False
        self.max_warning = False
        self.interpolation = scipy.interpolate.InterpolatedUnivariateSpline(lmbs, idxs, k=1)

    def get_index(self, lmb):
        lmb_min = np.min(lmb)
        if lmb_min < self.lmb_min:
            if not self.min_warning:
                print(
                    'WARNING: Wavelength less than minimum table value, {} (displayed only once)'.format(self.lmb_min))
                self.min_warning = True
            return self.indexes[0]
            # raise ValueError('Wavelength less than minimum table value, {}'.format(self.lmb_min))
        elif np.max(lmb) > self.lmb_max:
            if not self.max_warning:
                print('Wavelength greater than maximum table value, {} (displayed only once)'.format(self.lmb_max))
                self.max_warning = True
            return self.indexes[-1]
            # raise ValueError('Wavelength greater than maximum table value, {}'.format(self.lmb_max))
        return self.interpolation(lmb)

    def clone(self):
        return TabulatedIndex(self.wavelengths, self.indexes)


class FormulaIndex:
    """ Tabulated index class"""

    def __init__(self, formula):
        self.formula = formula

    def get_index(self, lmb):
        return self.formula(lmb)

    def clone(self):
        return FormulaIndex(self.formula)

# endregion
