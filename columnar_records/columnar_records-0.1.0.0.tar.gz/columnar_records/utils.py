'''Utility functions for ColumnarRecords, mostly lifted from
the package "np_utils"'''

from __future__ import print_function, division
from builtins import zip

from itertools import chain, islice

import numpy as np

def assertSameAndCondense(l, message='List values differ!'):
    '''Take a list of values that should all be the same, assert that this is true,
       and then return the common value
       This acts as a safe funnel in exploratory data processing,
       cutting a large same-valued list down to a single value.
       
       Simplified version of np_utils.assertSameAndCondense'''
    l0 = l[0]
    assert all([i == l0 for i in l]), message
    return l0

def split_at_boundaries(l, boundaries):
    '''Split a list at the boundaries (which must be a sorted list)
       Endpoints are optional and will be ignored
       This function uses itertools in case "boundaries" is very large
       (avoids any intermediate list or array creation)
       This function works on and is fast for any iterable, including arrays
       
       Copy of np_utils.list_utils.split_at_boundaries'''
    lenl = len(l)
    boundaries = boundaries[(1 if boundaries[0] == 0 else 0):
                            (-1 if boundaries[-1] == lenl else None)]
    if not len(boundaries):
        return [l]
    
    start_end = chain([[0, boundaries[0]]],
                      zip(islice(boundaries, 0, lenl-1),
                          islice(boundaries, 1, None)),
                      [[boundaries[-1], lenl]])
    count = len(boundaries) + 1
    return [l[start:end] for start, end in start_end]

def index_helper(arr, sort_arr):
    '''Compute some basic things needed for indexing functions below
       Inputs
       arr:      Any flat array
       sort_arr: Sorted version of arr
       
       Returns
       isdiff:       Boolean array with same length as arr
                     True if each element is different from its lefthand
                     False if it is the same
                     (called "flag" in np.unique)
       
       keys:         Unique values of arr (sorted)
       
       split_points: Locations where the isdiff is True
                     (or where the sorted array has change points)
                     This is what makes it possible to determine the
                     size of each group
                     
       Copy of np_utils.recarray_utils._index_helper'''
    isdiff = np.concatenate(([True], sort_arr[1:] != sort_arr[:-1]))
    keys = sort_arr[isdiff]
    split_points = np.flatnonzero(isdiff)
    return isdiff, keys, split_points

def get_index_groups(arr):
    '''For a 1D array, get all unique values (keys)
       and the locations of each value in the original array (index_groups).
       keys and index_groups are aligned so that dict(zip(keys, index_groups))
       creates a dictionary that maps from each unique value in arr
       to a list of all the locations for that value.
       
       "index_groups" can be thought of as a much more efficient variant of:
           [np.where(arr==i) for i in np.unique(arr)]
       Example: a group by "count" can be achieved by:
           keys, index_groups = get_index_groups(arr)
           counts = map(len, index_groups)
       which would be equivalent to this pseudo-sql:
           select count(x) from arr group by x
       
       The algorithm can be summarized as follows:
       * Form a list of unique values (keys)
       
       * Find the locations where the sorted array changes values (split_points)
       
       * Replace every value in arr with an index into the unique keys (inv)
         - keys and inv are calculated in the exact same way as in np.unique
       
       * Argsort "inv" to cluster the indices of arr into groups and
         split these groups at the split points
         These indices will then be indices for the original values as well since
         the positions of elements in "inv" represent values in "arr"

       Note: The reason for using _index_base (above) instead of "np.unique"
             is that we can reuse "flag" (isdiff here) to calculate the
             split_points directly and avoid calling np.bincount and
             then np.cumsum on inv
       
       Internal variable details:
       sort_ind:        Argsort of arr -- indices of the array rearranged such
                                          that arr[sort_ind] == np.sort(arr)
       
       sort_arr:        Sorted version of arr
       
       sorted_key_inds: A list the unique value's indices in keys (so just 0-n)
                        repeated the number of times if occurs in the array
       
       inv:             The inverse mapping from unique to arr, an array
                        of the indices of keys such that keys[inv] == arr
                        (same as the optional return value from np.unique)
                        
                        Note that np.argsort(inv) gives the indices of arr
                        sorted into groups based on keys; a 1d array where
                        indices in the same group are "clustered" contiguously
       
       index_groups:    The indices of arr grouped into list of arrays
                        where each group (array) matches a specific key
                        This property will then be true:
                        np.all(arr[index_groups[i]] == keys[i])
       
       Copy of np_utils.recarray_utils.get_index_groups
    '''
    arr = np.ravel(arr)
    sort_ind = np.argsort(arr) #,kind='mergesort')
    sort_arr = arr[sort_ind]
    isdiff, keys, split_points = index_helper(arr, sort_arr)
    sorted_key_inds = np.cumsum(isdiff) - 1
    inv = np.empty(arr.shape, dtype=np.intp)
    inv[sort_ind] = sorted_key_inds
    index_groups = split_at_boundaries(np.argsort(inv), split_points)
    return keys, index_groups
