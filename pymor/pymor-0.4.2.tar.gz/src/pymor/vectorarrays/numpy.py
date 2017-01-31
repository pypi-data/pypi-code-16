# -*- coding: utf-8 -*-
# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2016 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function

from numbers import Number

import numpy as np
from scipy.sparse import issparse

from pymor.core import NUMPY_INDEX_QUIRK
from pymor.vectorarrays.interfaces import VectorArrayInterface, VectorSpace


class NumpyVectorArray(VectorArrayInterface):
    """|VectorArray| implementation via |NumPy arrays|.

    This is the default |VectorArray| type used by all |Operators|
    in pyMOR's discretization toolkit. Moreover, all reduced |Operators|
    are based on |NumpyVectorArray|.

    Note that this class is just a thin wrapper around the underlying
    |NumPy array|. Thus, while operations like
    :meth:`~pymor.vectorarrays.interfaces.VectorArrayInterface.axpy` or
    :meth:`~pymor.vectorarrays.interfaces.VectorArrayInterface.dot`
    will be quite efficient, removing or appending vectors will
    be costly.
    """

    def __init__(self, instance, dtype=None, copy=False, order=None, subok=False):
        assert not isinstance(instance, np.matrixlib.defmatrix.matrix)
        if isinstance(instance, np.ndarray):
            if copy:
                self._array = instance.copy()
            else:
                self._array = instance
        elif issparse(instance):
            self._array = instance.toarray()
        elif hasattr(instance, 'data'):
            self._array = instance.data
            if copy:
                self._array = self._array.copy()
        else:
            self._array = np.array(instance, dtype=dtype, copy=copy, order=order, subok=subok, ndmin=2)
        if self._array.ndim != 2:
            assert self._array.ndim == 1
            self._array = np.reshape(self._array, (1, -1))
        self._len = len(self._array)
        self._refcount = [1]

    @classmethod
    def from_file(cls, path, key=None, single_vector=False, transpose=False):
        assert not (single_vector and transpose)
        from pymor.tools.io import load_matrix
        array = load_matrix(path, key=key)
        assert isinstance(array, np.ndarray)
        assert array.ndim <= 2
        if array.ndim == 1:
            array = array.reshape((1, -1))
        if single_vector:
            assert array.shape[0] == 1 or array.shape[1] == 1
            array = array.reshape((1, -1))
        if transpose:
            array = array.T
        return cls(array)

    @classmethod
    def make_array(cls, subtype=None, count=0, reserve=0):
        assert isinstance(subtype, Number)
        assert count >= 0
        assert reserve >= 0
        va = cls(np.empty((0, 0)))
        va._array = np.zeros((max(count, reserve), subtype))
        va._len = count
        return va

    @property
    def data(self):
        if self._refcount[0] > 1:
            self._deep_copy()
        return self._array[:self._len]

    @property
    def real(self):
        return NumpyVectorArray(self._array[:self._len].real, copy=True)

    @property
    def imag(self):
        return NumpyVectorArray(self._array[:self._len].imag, copy=True)

    def __len__(self):
        return self._len

    @property
    def subtype(self):
        return self._array.shape[1]

    @property
    def dim(self):
        return self._array.shape[1]

    def copy(self, ind=None, deep=False):
        assert self.check_ind(ind)

        if not deep and ind is None:
            c = NumpyVectorArray(self._array, copy=False)
            c._len = self._len
            c._refcount = self._refcount
            self._refcount[0] += 1
            return c

        if NUMPY_INDEX_QUIRK and self._len == 0:
            return NumpyVectorArray(self._array[:0], copy=True)

        if ind is None:
            return NumpyVectorArray(self._array[:self._len], copy=True)
        else:
            C = NumpyVectorArray(self._array[ind], copy=False)
            if not C._array.flags['OWNDATA']:
                C._array = np.array(C._array)
            return C

    def append(self, other, o_ind=None, remove_from_other=False):
        assert other.check_ind(o_ind)
        assert self.dim == other.dim
        assert other is not self or not remove_from_other

        if self._refcount[0] > 1:
            self._deep_copy()
        if remove_from_other and other._refcount[0] > 1:
            other._deep_copy()

        if NUMPY_INDEX_QUIRK and other._len == 0:
            o_ind = None

        if o_ind is None:
            len_other = other._len
            if len_other <= self._array.shape[0] - self._len:
                if self._array.dtype != other._array.dtype:
                    self._array = self._array.astype(np.promote_types(self._array.dtype, other._array.dtype))
                self._array[self._len:self._len + len_other] = other._array[:len_other]
            else:
                self._array = np.vstack((self._array[:self._len], other._array[:len_other]))
            self._len += len_other
        else:
            if not hasattr(o_ind, '__len__'):
                len_other = 1
                o_ind = [o_ind]
            else:
                len_other = len(o_ind)
            if len_other <= self._array.shape[0] - self._len:
                if self._array.dtype != other._array.dtype:
                    self._array = self._array.astype(np.promote_types(self._array.dtype, other._array.dtype))
                other._array.take(o_ind, axis=0, out=self._array[self._len:self._len + len_other])
            else:
                self._array = np.append(self._array[:self._len], other._array[o_ind], axis=0)
            self._len += len_other
        if remove_from_other:
            other.remove(o_ind)

    def remove(self, ind=None):
        assert self.check_ind(ind)

        if self._refcount[0] > 1:
            self._deep_copy()

        if ind is None:
            self._array = np.zeros((0, self.dim))
            self._len = 0
        else:
            if hasattr(ind, '__len__'):
                if len(ind) == 0:
                    return
                remaining = sorted(set(xrange(len(self))) - set(ind))
                self._array = self._array[remaining]
            else:
                assert -self._len < ind < self._len
                self._array = self._array[range(ind) + range(ind + 1, self._len)]
            self._len = self._array.shape[0]
        if not self._array.flags['OWNDATA']:
            self._array = self._array.copy()

    def replace(self, other, ind=None, o_ind=None, remove_from_other=False):
        assert self.check_ind_unique(ind)
        assert other.check_ind(o_ind)
        assert self.dim == other.dim
        assert other is not self or not remove_from_other

        if self._refcount[0] > 1:
            self._deep_copy()
        if remove_from_other and other._refcount[0] > 1:
            other._deep_copy()

        if NUMPY_INDEX_QUIRK:
            if self._len == 0 and hasattr(ind, '__len__'):
                ind = None
            if other._len == 0 and hasattr(o_ind, '__len__'):
                o_ind = None

        if ind is None:
            if o_ind is None:
                if other is self:
                    return
                assert other._len == self._len
                self._array = other._array[:other._len].copy()
            else:
                if not hasattr(o_ind, '__len__'):
                    o_ind = [o_ind]
                assert self._len == len(o_ind)
                self._array = other._array[o_ind]
            self._len = self._array.shape[0]
        else:
            len_ind = self.len_ind(ind)
            other_array = np.array(self._array) if other is self else other._array
            if self._array.dtype != other._array.dtype:
                self._array = self._array.astype(np.promote_types(self._array.dtype, other._array.dtype))
            if o_ind is None:
                assert len_ind == other._len
                self._array[ind] = other_array[:other._len]
            else:
                len_oind = other.len_ind(o_ind)
                assert len_ind == len_oind
                self._array[ind] = other_array[o_ind]
        assert self._array.flags['OWNDATA']

        if remove_from_other:
            other.remove(o_ind)

    def scal(self, alpha, ind=None):
        assert self.check_ind_unique(ind)
        assert isinstance(alpha, Number) \
            or isinstance(alpha, np.ndarray) and alpha.shape == (self.len_ind(ind),)

        if self._refcount[0] > 1:
            self._deep_copy()

        if NUMPY_INDEX_QUIRK and self._len == 0:
            return

        if isinstance(alpha, np.ndarray) and not isinstance(ind, Number):
            alpha = alpha[:, np.newaxis]

        alpha_type = type(alpha)
        alpha_dtype = alpha.dtype if alpha_type is np.ndarray else alpha_type
        if self._array.dtype != alpha_dtype:
            self._array = self._array.astype(np.promote_types(self._array.dtype, alpha_dtype))

        if ind is None:
            self._array[:self._len] *= alpha
        else:
            self._array[ind] *= alpha

    def axpy(self, alpha, x, ind=None, x_ind=None):
        assert self.check_ind_unique(ind)
        assert x.check_ind(x_ind)
        assert self.dim == x.dim
        assert self.len_ind(ind) == x.len_ind(x_ind) or x.len_ind(x_ind) == 1
        assert isinstance(alpha, Number) \
            or isinstance(alpha, np.ndarray) and alpha.shape == (self.len_ind(ind),)

        if self._refcount[0] > 1:
            self._deep_copy()

        if NUMPY_INDEX_QUIRK:
            if self._len == 0 and hasattr(ind, '__len__'):
                ind = None
            if x._len == 0 and hasattr(x_ind, '__len__'):
                x_ind = None

        if np.all(alpha == 0):
            return

        B = x._array[:x._len] if x_ind is None else x._array[x_ind]

        alpha_type = type(alpha)
        alpha_dtype = alpha.dtype if alpha_type is np.ndarray else alpha_type
        if self._array.dtype != alpha_dtype or self._array.dtype != B.dtype:
            dtype = np.promote_types(self._array.dtype, alpha_dtype)
            dtype = np.promote_types(dtype, B.dtype)
            self._array = self._array.astype(dtype)

        if np.all(alpha == 1):
            if ind is None:
                self._array[:self._len] += B
            elif isinstance(ind, Number) and B.ndim == 2:
                self._array[ind] += B.reshape((B.shape[1],))
            else:
                self._array[ind] += B
        elif np.all(alpha == -1):
            if ind is None:
                self._array[:self._len] -= B
            elif isinstance(ind, Number) and B.ndim == 2:
                self._array[ind] -= B.reshape((B.shape[1],))
            else:
                self._array[ind] -= B
        else:
            if isinstance(alpha, np.ndarray):
                alpha = alpha[:, np.newaxis]
            if ind is None:
                self._array[:self._len] += (B * alpha)
            elif isinstance(ind, Number):
                self._array[ind] += (B * alpha).reshape((-1,))
            else:
                self._array[ind] += (B * alpha)

    def dot(self, other, ind=None, o_ind=None):
        assert self.check_ind(ind)
        assert other.check_ind(o_ind)
        assert self.dim == other.dim

        if NUMPY_INDEX_QUIRK:
            if self._len == 0 and hasattr(ind, '__len__'):
                ind = None
            if other._len == 0 and hasattr(o_ind, '__len__'):
                o_ind = None

        A = self._array[:self._len] if ind is None else \
            self._array[ind] if hasattr(ind, '__len__') else self._array[ind:ind + 1]
        B = other._array[:other._len] if o_ind is None else \
            other._array[o_ind] if hasattr(o_ind, '__len__') else other._array[o_ind:o_ind + 1]

        if B.dtype in _complex_dtypes:
            return A.dot(B.conj().T)
        else:
            return A.dot(B.T)

    def pairwise_dot(self, other, ind=None, o_ind=None):
        assert self.check_ind(ind)
        assert other.check_ind(o_ind)
        assert self.dim == other.dim
        assert self.len_ind(ind) == other.len_ind(o_ind)

        if NUMPY_INDEX_QUIRK:
            if self._len == 0 and hasattr(ind, '__len__'):
                ind = None
            if other._len == 0 and hasattr(o_ind, '__len__'):
                o_ind = None

        A = self._array[:self._len] if ind is None else \
            self._array[ind] if hasattr(ind, '__len__') else self._array[ind:ind + 1]
        B = other._array[:other._len] if o_ind is None else \
            other._array[o_ind] if hasattr(o_ind, '__len__') else other._array[o_ind:o_ind + 1]

        if B.dtype in _complex_dtypes:
            return np.sum(A * B.conj(), axis=1)
        else:
            return np.sum(A * B, axis=1)

    def lincomb(self, coefficients, ind=None):
        assert self.check_ind(ind)
        assert 1 <= coefficients.ndim <= 2

        if NUMPY_INDEX_QUIRK and self._len == 0:
            ind = None

        if coefficients.ndim == 1:
            coefficients = coefficients[np.newaxis, ...]

        assert ind is None and coefficients.shape[1] == len(self) \
            or not hasattr(ind, '__len__') and coefficients.shape[1] == 1 \
            or hasattr(ind, '__len__') and coefficients.shape[1] == len(ind)

        if ind is None:
            return NumpyVectorArray(coefficients.dot(self._array[:self._len]), copy=False)
        elif hasattr(ind, '__len__'):
            return NumpyVectorArray(coefficients.dot(self._array[ind]), copy=False)
        else:
            return NumpyVectorArray(coefficients.dot(self._array[ind:ind + 1]), copy=False)

    def l1_norm(self, ind=None):
        assert self.check_ind(ind)

        if NUMPY_INDEX_QUIRK and self._len == 0:
            ind = None

        A = self._array[:self._len] if ind is None else \
            self._array[ind] if hasattr(ind, '__len__') else self._array[ind:ind + 1]

        return np.linalg.norm(A, ord=1, axis=1)

    def l2_norm(self, ind=None):
        assert self.check_ind(ind)

        if NUMPY_INDEX_QUIRK and self._len == 0:
            ind = None

        A = self._array[:self._len] if ind is None else \
            self._array[ind] if hasattr(ind, '__len__') else self._array[ind:ind + 1]

        return np.linalg.norm(A, axis=1)

    def components(self, component_indices, ind=None):
        assert self.check_ind(ind)
        assert isinstance(component_indices, list) and (len(component_indices) == 0 or min(component_indices) >= 0) \
            or (isinstance(component_indices, np.ndarray) and component_indices.ndim == 1
                and (len(component_indices) == 0 or np.min(component_indices) >= 0))
        # NumPy 1.9 is quite permissive when indexing arrays of size 0, so we have to add the
        # following check:
        assert self._len > 0 \
            or (isinstance(component_indices, list)
                and (len(component_indices) == 0 or max(component_indices) < self.dim)) \
            or (isinstance(component_indices, np.ndarray) and component_indices.ndim == 1
                and (len(component_indices) == 0 or np.max(component_indices) < self.dim))

        if NUMPY_INDEX_QUIRK and (self._len == 0 or self.dim == 0):
            assert isinstance(component_indices, list) \
                and (len(component_indices) == 0 or max(component_indices) < self.dim) \
                or isinstance(component_indices, np.ndarray) \
                and component_indices.ndim == 1 \
                and (len(component_indices) == 0 or np.max(component_indices) < self.dim)
            return np.zeros((self.len_ind(ind), len(component_indices)))

        if ind is None:
            return self._array[:self._len, component_indices]
        else:
            if not hasattr(ind, '__len__'):
                ind = [ind]
            return self._array[:, component_indices][ind, :]

    def amax(self, ind=None):
        assert self.dim > 0
        assert self.check_ind(ind)

        if NUMPY_INDEX_QUIRK and self._len == 0:
            ind = None

        if self._array.shape[1] == 0:
            l = self.len_ind(ind)
            return np.ones(l) * -1, np.zeros(l)

        A = self._array[:self._len] if ind is None else \
            self._array[ind] if hasattr(ind, '__len__') else self._array[ind:ind + 1]

        A = np.abs(A)
        max_ind = np.argmax(A, axis=1)
        max_val = A[np.arange(len(A)), max_ind]
        return max_ind, max_val

    def __str__(self):
        return self._array[:self._len].__str__()

    def __repr__(self):
        return 'NumpyVectorArray({})'.format(self._array[:self._len].__str__())

    def __del__(self):
        self._refcount[0] -= 1

    def _deep_copy(self):
        self._array = self._array.copy()  # copy the array data
        self._refcount[0] -= 1            # decrease refcount for original array
        self._refcount = [1]              # create new reference counter


def NumpyVectorSpace(dim):
    """Shorthand for |VectorSpace| `(NumpyVectorArray, dim)`."""
    return VectorSpace(NumpyVectorArray, dim)


_complex_dtypes = (np.complex64, np.complex128)
