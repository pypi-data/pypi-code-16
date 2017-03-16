#!/usr/bin/env python

import sys
import logging
import bisect
import math

import numpy as np
import scipy

"""
Contains statistical methods.
"""

# Initialize a logging object specific to this module
logger = logging.getLogger(__name__)


def full_fields_to_ptiles(full_fields, climo, ref_ptiles, k, debug=False):
    """ Converts an array of full field values to percentiles based on a set of climatology data
    containing an array of full field values associated with a reference array of percentiles, using linear interpolation.

    A typical example of using this function would be for array full_fields (1-D, size of locations) to use a climatology array (2-D, # ptiles, size of locations) containing full field values where the first dimension (axis=0) represents a set of reference percentiles. The reference percentiles are passed as a 1-D array and must represent the order of percentiles in the climo array appropriately.

    Parameters
    ----------
    full_fields : array_like   
        1-dimensional (e.g. # locations) Numpy array of full field values to convert.
    climo : array_like
        2-dimensional (e.g. # reference percentiles x # locations) Numpy array of climatology
        full field values associated with the set of reference percentiles.
    ref_ptiles : array_like
        1-dimensional (# reference percentiles) Numpy array of reference
        percentiles that is associated with the percentiles used in the
        climatology data. *Values must be between 0 and 1*
    k : Linear interpolation constant representing the ratio of the standard deviation of the
        percentile at the 100th percentile to the last available reference
        percentile. (std(100th ptile)/std(last ptile))

    Returns
    -------
    array_like
        A 1-dimensional (e.g. # locations) Numpy array of percentiles associated
        with the passed full field values.

    Raises
    ------
    Exception
        If input argument data arrays are not the required shape or dimensions
        or if the percentile calculation returns an exception.
    ValueError
        An error occurred if the reference percentiles used were not in order
        from least to greatest or arrays requiring values to be between 0 and 1.

    Examples
    --------

    >>> import numpy as np
    >>> from stats_utils.stats import full_fields_to_ptiles
    >>> ref_ptiles = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
    >>> num_ptiles = ref_ptiles.shape[0]
    >>> k = 1.343
    >>> full_fields = np.array([14.9, 21.1, 30.2, 28.4, 12.12])
    >>> climo_data = np.array([[15.2, 15.2,   15.2, 15.2, 15.2],
    ...                        [16.4, 16.4,   16.4, 16.4, 16.4],
    ...                        [17.8, 17.8,   17.8, 17.8, 17.8],
    ...                        [18.8, 18.8,   18.8, 18.8, 18.8],
    ...                        [20.5, np.nan, 20.5, 20.5, 20.5],
    ...                        [22.3, 22.3,   22.3, 22.3, 22.3],
    ...                        [23.7, 23.7,   23.7, 23.7, 23.7],
    ...                        [24.6, 24.6,   24.6, 24.6, 24.6],
    ...                        [27.6, 27.6,   27.6, 27.6, 27.6]])
    >>> A = full_fields_to_ptiles(full_fields, climo_data, ref_ptiles, k)
    >>> print(A)
    [ 0.08349744         nan  1.          0.93285016  0.        ]
    """
    # Set logging level
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)
    # Initialize returned full_fields var
    ptiles = None

    # Check to see if number of dims are correct
    # Ref ptiles should be 1, Obs should be 1, Climo 2
    if ref_ptiles.ndim != 1:
        raise Exception("Reference percentile array has a dimension of {}. "
                        "Must have an array dimension of 1.".format(
            ref_ptiles.ndim))
    if full_fields.ndim != 1:
        raise Exception("Full fields array has a dimension of {}. Must have "
                        "an array dimension of 1.".format(full_fields.ndim))
    if climo.ndim != 2:
        raise Exception("Climatology array has a dimension of {}. Must have an"
                        " array dimension of 2.".format(climo.ndim))

    # Check to see if obs, climo, and ref_ptiles correct dimensions
    # Size of obs should match the size of climo 2nd dim
    if full_fields.shape[0] != climo.shape[1]:
        raise Exception("Size of obs array does not match size of 2nd dim of "
                        "climo array.")
    if climo.shape[0] != ref_ptiles.shape[0]:
        raise Exception("Size of climo array (1st dim) does not match size "
                        "reference percentiles array.")
    # Check to see if reference percentiles and ptiles are between 0 and 1
    if not (all(ref_ptiles[i] >= 0 and ref_ptiles[i] <= 1.0 for i in range(len(ref_ptiles)))):
            raise ValueError("One or more invalid reference percentiles (ref_ptiles). Values must be between 0 and 1.0.") 
    # Set indices of the last, 50th, and 100th percentile associated with
    # array ref_ptiles
    ptile_last = np.size(ref_ptiles)-1
    ptile_50th = bisect.bisect(ref_ptiles,0.50)-1

    # Check to see if reference ptiles passed are ordered least to greatest
    if not (all(ref_ptiles[i] <= ref_ptiles[i+1] for i in range(ref_ptiles.shape[0]-1))):
        raise ValueError("Reference percentiles are not in order (least to "
                        "greatest). Check passed array to make sure it is "
                        "correct and ordered.")

    try:
        # Calculate the associated or corresponding climatological percentile
        #  with the full fields array
        ptiles = np.array([
            # If full_field is nan, set to a nan value
            np.nan
                if np.isnan(full_field)

            # If full_field == a climo value, set ptile to the reference climo ptile
            # NOTE: Python gives a longer ref_ptiles precision value than
            # specified, ie. 0.10000000000000001 instead of 0.1arg
            else ref_ptiles[np.argwhere(climo[:,loc] == full_field)[0][0]]
                if full_field in climo[:,loc]

            # If full_field >= estimated T100th ptile, set ptile to 1.0
            else 1.00
                if full_field >= k*(climo[ptile_last,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]

            # If full_field > climo[last ptile] AND full_field < est T100th, calculate ptile using linear interpolation
            else ref_ptiles[ptile_last] + ((full_field - climo[ptile_last,loc])/(k*(climo[ptile_last,loc] - \
                climo[ptile_50th,loc]) + climo[ptile_50th,loc] - climo[ptile_last,loc]))*(1-ref_ptiles[ptile_last])
                if full_field > climo[ptile_last,loc] and full_field < k*(climo[ptile_last,loc] - climo[ptile_50th,loc]) \
                + climo[ptile_50th,loc]

            # If full_field <= estimated T0th ptile, set ptile to 0.0
            else 0.00
                if full_field <= k*(climo[0,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]

            # If full_field < climo 1st AND full_field > est T0th, calculate ptile using linear interpolation
            else ref_ptiles[0] + ((full_field - climo[0,loc])/(k*(climo[0,loc] - \
                climo[ptile_50th,loc]) + climo[ptile_50th,loc] - climo[0,loc])) * (0.00 - ref_ptiles[0])
                if full_field < climo[0,loc] and full_field > k*(climo[0,loc] - climo[ptile_50th,loc]) + climo[ptile_50th,loc]

            # If climo[0,loc] < full_field < climo[last,loc], calculate ptile using linear interpolation
            # bisect.bisect(climo[:,loc],full_field) will give the index of the closest upper adjacent climo value relative to the full_field value
            else ref_ptiles[bisect.bisect(climo[:,loc],full_field)-1] + \
            (ref_ptiles[bisect.bisect(climo[:,loc],full_field)] - ref_ptiles[bisect.bisect(climo[:,loc],full_field)-1]) \
            * ((full_field - climo[bisect.bisect(climo[:,loc],full_field)-1,loc])/ \
            (climo[bisect.bisect(climo[:,loc],full_field),loc]-climo[bisect.bisect(climo[:,loc],full_field)-1,loc]))
                if full_field > climo[0,loc] and full_field < climo[ptile_last,loc]

            # Else set to NaN (a climo value may have potentially been a NaN that is necessary)
            else np.nan
            for loc, full_field in enumerate(full_fields)
        ])
    except:
        raise Exception("Full field to percentiles calculation failed.")
    
    logger.debug("Completed converting full field values.")
    return ptiles

def ptiles_to_full_fields(ptiles, climo, ref_ptiles, k, debug=False):
    """ Converts a 2-D array of percentile values to full fields based on a set of climatology data containing an array of full field values associated with a reference array of percentiles, using linear interpolation. Axis 0 of ptiles would be any number of times to iterate this calculation for, and axis 1 would be for example the number of locations, which would correspond to the axis 1 values of climo passed in. The conversion of percentiles to full fields would loop for each ptiles axis=0 (e.g. # sets of locations) for each value in axis=1 (e.g. # locations).

    A typical example of using this function would be for array ptiles (2-D, where axis=0 could be sets of values to process, and axis=1 is the number of locations) to use a climatology array (2-D, # ptiles, size of locations) containing full field values where the first dimension (axis=0) represents a set of reference percentiles. The reference percentiles are passed as a 1-D array and must represent the order of percentiles in the climo array appropriately.  

    Parameters
    ----------
    ptiles : array_like   
        2-dimensional (e.g. # sets of locations x # locations) Numpy array of percentile values to convert. *Values must be between 0 and 1*
    climo : array_like
        2-dimensional (e.g. # reference percentiles x # locations) Numpy array of climatology
        full field values associated with the set of reference percentiles
    ref_ptiles : array_like
        1-dimensional (# reference percentiles) Numpy array of reference
        percentiles that is associated with the percentiles used in the
        climatology data. *Values must be between 0 and 1*
    k : Linear interpolation constant representing the ratio of the standard deviation of the
        percentile at the 100th percentile to the last available reference
        percentile. (std(100th ptile)/std(last ptile))

    Returns
    -------
    array_like
        A 2-dimensional (e.g. # sets of locations x # locations) Numpy array of full field values associated with the passed percentiles.

    Raises
    ------
    Exception
        If input argument data arrays are not the required shape or dimensions
        or if the percentile calculation returns an exception.
    ValueError
        An error occurred if the reference percentiles used were not in order
        from least to greatest or arrays requiring values to be between 0 and 1.

    Examples
    --------

    >>> import numpy as np
    >>> from stats_utils.stats import ptiles_to_full_fields
    >>> ref_ptiles = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
    >>> k = 2.4
    >>> ptiles = np.array([[ 0.96453162,  0.9788125,   0.91784823,  0.95907287,  0.9154159 ],
 [ 0.22127757,  0.71937965,  0.44560025,  0.76208565,  0.55930441]])
    >>> climo_data = np.array( [[  5.55313984,  25.41960951,   0.50288792,   0.6394681,    7.65101108],
 [ 16.36322023,  29.97232946,   1.7436097,   12.03231585,  12.86985957],
 [ 26.51493109,  51.78254632,  27.36005889,  16.73075656,  21.66491018],
 [ 40.69695371,  52.22306231,  29.84435173,  24.67690332,  21.7419636 ],
 [ 66.03066685,  60.1204237,  39.15587001,  27.07399175 , 32.02452737],
 [ 73.88730124,  65.10386727,  51.18023631,  76.12963083,  33.87827395],
 [ 79.44129297,  69.63914678,  60.63850887,  78.06065864,  66.1134694 ],
 [ 85.42577978,  72.04574367,  75.55936204,  79.24654427,  70.92313987],
 [ 94.83219311,  79.5638582 ,  79.12805759,  87.42370628,  70.95441156],
 [ 97.54798656,  89.47133895,  96.21986897,  92.31485394,  73.54732073]])
    >>> A = ptiles_to_full_fields(ptiles, climo_data, ref_ptiles, k)
    >>> print(A)
[[ 110.37192254  113.15018983   85.2292292   108.88866606   71.75385213]
 [  18.52325761   70.10553683   34.09042734   78.79692344   33.12388084]]
    """
    # Set logging level
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)
    logger.debug("Converting to full field values.")
    # Initialize returned array var
    full_fields = None

    # Check to see if number of dims are correct
    # Ref ptiles should be 1, ptile should be 1, Climo 2
    if ref_ptiles.ndim != 1:
        raise Exception("Reference percentile array has a dimension of {}. "
                        "Must have an array dimension of 1.".format(ref_ptiles.ndim))
    if ptiles.ndim != 2:
        raise Exception("Percentiles array has a dimension of {}. Must have "
                        "an array dimension of 2.".format(ptiles.ndim))
    if climo.ndim != 2:
        raise Exception("Climatology array has a dimension of {}. Must have an"
                        " array dimension of 2.".format(climo.ndim))

    # Check to see if climo and ref_ptiles correct dimensions
    # Size of ptiles should match the size of climo 2nd dim
    if climo.shape[0] != ref_ptiles.shape[0]:
        raise Exception("Size of climo array (1st dim) does not match size "
                        "reference percentiles array.")
    # Check to see if reference percentiles and ptiles are between 0 and 1
    if not ((ref_ptiles >= 0.0).all() & (ref_ptiles <= 1.0).all()):
        logger.warn("Invalid reference percentiles : " + str(np.where(ref_ptiles > 1.0)))
        raise ValueError("One or more invalid reference percentiles (ref_ptiles). Values must be between 0 and 1.0.")
    # ToDo: Add exclusion of nans. Commenting out for now because map becomes blank even when a few nans
    # Check to see if ptiles are between 0 and 1
    #if not ((ptiles >= 0.0).all() & (ptiles <= 1.0).all()):
    #    logger.warn("Invalid passed percentiles less than 0 : " + str(np.where(ptiles < 0.0)))
    #    logger.warn("Invalid passed percentiles greater than 1 : " + str(np.where(ptiles > 1.0)))
    #    raise ValueError("One or more invalid passed percentiles (ptiles). Values must be between 0 and 1.0.")

    # Set indices of the last, 50th, and 100th percentile associated with
    # array ref_ptiles
    ptile_last = np.size(ref_ptiles)-1
    ptile_50th = bisect.bisect(ref_ptiles,0.50)-1

    # Check to see if reference ptiles passed are ordered least to greatest
    if not (all(ref_ptiles[i] <= ref_ptiles[i+1] for i in range(ref_ptiles.shape[0]-1))):
        raise ValueError("Reference percentiles are not in order (least to greatest). Check passed array to make sure it is correct and ordered.")

    try:
        # Calculate the associated or corresponding climatological percentile
        #  with the perecntile array
        full_fields = np.array([
            # If ptile is nan OR if greater than 1.0 OR less than 0.0, set to a nan value
            np.nan
                if np.isnan(ptile) or ptile > 1.0 or ptile < 0.0

            # If ptile == a reference percentile, set full field to the associated climo value
            # NOTE: Python gives a longer ref_ptiles precision value than
            # specified, ie. 0.10000000000000001 instead of 0.1arg
            else climo[np.argwhere(ref_ptiles == ptile)[0],loc]
                if ptile in ref_ptiles

            # If ptile > ref_ptiles[last ptile]
            else climo[ptile_last,loc] + ((ptile - ref_ptiles[ptile_last])/(1.0 - ref_ptiles[ptile_last]))*((k*(climo[ptile_last,loc]-climo[ptile_50th,loc])+climo[ptile_50th,loc])-climo[ptile_last,loc])
                if ptile > ref_ptiles[ptile_last]

            # If ptile < ref_ptiles[0]
            else climo[0,loc] + ((ptile - ref_ptiles[0])/(0.0 - ref_ptiles[0])) * ((k*(climo[0,loc]-climo[ptile_50th,loc])+climo[ptile_50th,loc]) - climo[0,loc])
                if ptile < ref_ptiles[0]

            # If ref_ptiles[0] < ptile < ref_ptiles[last], calculate the full field using linear interpolation
            else climo[bisect.bisect(ref_ptiles,ptile)-1,loc] + \
            (climo[bisect.bisect(ref_ptiles,ptile),loc] - climo[bisect.bisect(ref_ptiles,ptile)-1,loc]) \
            * ((ptile - ref_ptiles[bisect.bisect(ref_ptiles,ptile)-1])/ \
            (ref_ptiles[bisect.bisect(ref_ptiles,ptile)]-ref_ptiles[bisect.bisect(ref_ptiles,ptile)-1]))
                if ptile > ref_ptiles[0] and ptile < ref_ptiles[ptile_last]

            # Else set to NaN (a climo value may have potentially been a NaN that is necessary)
            else np.nan
            # Perform for each value in the ptiles array
            # Do for each array along axis=0
            for i in range(0,ptiles[:,0].size)
            # Do for each location
                for loc, ptile in enumerate(ptiles[i,:])
        ])
    except:
        raise Exception("Percentile to full fields values calculation failed.")

    # Reshape to 2-D [# locs x # probs]
    full_fields = np.reshape(full_fields, (ptiles[:,0].size,ptiles[0,:].size))

    logger.debug("Completed converting full field values.")
    return full_fields


def probs_to_ptiles_using_poe(probs, poes, ref_ptiles, k, debug=False):
    """ Returns a 2-D array of percentiles for all probabilities listed in array probs, using the input array of POEs. The returned array dimension is [# probs x size of poes along axis=1 (e.g. # locations)], where the size of probability of exceedences or POEs, along axis=1, would typically be the # of locations. The passed input POEs would typically contain probability of exceedence values for a set of reference percentiles represented along axis=0, for all locations along axis=1. The POE values must be in order of going from greatest to least value across axis=0, which represents the values for each of the reference percentiles. The reference percentiles must be ordered from lowest to highest. Values in passed input arguments (probs, poes, ref_ptiles) must range from 0.0 to 1.0.

    An example of using this function would be to obtain the climatological percentile associated with the forecasts having a 15%, 50%, and 85% probability at every location, where an array of forecast probabilities (in decmial POE format) is used as a reference (variable poes). In this example, probs would be a 1-D array of desired forecast probabilities [0.15, 0.5, 0.85]. poes variable would be the forecast probabilities for exceeding each of the reference percentiles [# percentiles x # locations] from greatest to lowest probabilities across axis=0, and ref_ptiles is the reference percentiles associated  with the forecast POE array (axis=0), ordered from lowest to highest value. A 2-D array is returned of percentiles for all the locations for all 3 requested probabilities, so dimension would be [3 x # locations] in this example.

    Parameters
    ----------
    probs : array_like
        1-dimensional (# probabilities to obtain) Numpy array of probability values to obtain percentile values for using the passed POEs array. Values must be between 0 1nd 1.
    poes : array_like
        2-dimensional (e.g. # reference percentiles x # locations) Numpy array of probability values associated with the reference percentiles, where the values along axis=0 must reflect the values associated with the order of ref_ptiles. These values must be ordered from greatest to least value along axis=0 (decreasing probabilities for increasing associated reference percentiles). This would typically be forecast probability of exceedence (POE) values. Values must be between 0 1nd 1.
    ref_ptiles : array_like
        1-dimensional (# reference percentiles) Numpy array of reference
        percentiles that is associated with the percentiles used in the
        POEs reference probability data. Values must be between 0 and 1
    k : Linear interpolation constant representing the ratio of the standard deviation of the
        percentile at the 100th percentile to the last available reference
        percentile. (std(100th ptile)/std(last ptile))

    Returns
    -------
    array_like
        A 2-dimensional (e.g. # probs  x size of poes along axis=1 (e.g. # locations)) Numpy array of percentiles associated
        with the passed probability values.

    Raises
    ------
    Exception
        If input argument data arrays are not the required shape or dimensions
        or if the percentile calculation returns an exception.
    ValueError
        An error occurred if one or more arrays passed were not in order
        from least to greatest or did not have values between 0 and 1.

    Examples
    --------

    Below is an example where there are 10 reference percentile values, for 5 locations, and each location has the same forecast POE values. The percentile is desired at the 50% forecast probability for each location.

    >>> import numpy as np
    >>> from stats_utils.stats import probs_to_ptiles_using_poe
    >>> ref_ptiles = np.array([0.1,.2,.3,.4,.5,.6,.7,.8,0.9,0.95])
    >>> k = 2.4
    >>> poes =np.transpose( np.reshape(np.array([0.73511322, 0.73474724, 0.72316011,  0.71183449,  0.42931605,  0.35428214, 0.32558677, 0.22493875, 0.21412566, 0.20267395]*5),(5,10)))
    >>> probs =  np.array([0.15, 0.85])
    >>> probs_to_ptiles_using_poe(probs, poes, ref_ptiles, k)
    array([[ 0.96299475,  0.96299475,  0.96299475,  0.96299475,  0.96299475],
       [ 0.05662797,  0.05662797,  0.05662797,  0.05662797,  0.05662797]])

    """
    # Set logging level
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)

    # Initialize returned full_fields var
    ptiles = None
    logger.debug("poes : " + str(poes))
    # Check to see if number of dims are correct
    # Ref ptiles should be 1, probs should be 1,poes 2
    if ref_ptiles.ndim != 1:
        raise Exception("Reference percentile array has a dimension of {}. "
                        "Must have an array dimension of 1.".format(
            ref_ptiles.ndim))
    if probs.ndim != 1:
        raise Exception("Probabilities array has a dimension of {}. Must have "
                        "an array dimension of 1.".format(full_fields.ndim))
    if poes.ndim != 2:
        raise Exception("Reference probabilities array has a dimension of {}. Must have an"
                        " array dimension of 2.".format(poes.ndim))

    # Check to see if arrays have correct dimensions
    if poes.shape[0] != ref_ptiles.shape[0]:
        raise Exception("Size of reference probabilities array (1st dim) does not match size "
                        "POEs array.")
    # Check to see if reference percentiles are between 0 and 1
    if not ((ref_ptiles >= 0.0).all() and (ref_ptiles <= 1.0).all()):
            raise ValueError("One or more invalid reference percentiles (ref_ptiles). Values must be between 0 and 1.0.")
    # Check to see if probabilities to convert are between 0 and 1
    if not ((probs >= 0.0).all() and (probs <= 1.0).all()):
            raise ValueError("One or more invalid probabiltiies. Values must be between 0 and 1.0.")
    # Check to see if POEs are between 0 and 1
    if ((poes < 0.0).any() | (poes > 1.0).any()):
            condition = (poes < 0.0) | (poes > 1.0)
            logger.warning("Invalid values encountered (must be between 0 and 1) : \n" + str(np.extract(condition,poes)))
            logger.warning("Invalid values :  \n" + str(np.argwhere((poes < 0.0) | (poes > 1.0))))
            raise ValueError("One or more invalid probability of exceedence (POE) values. Values must be between 0 and 1.0.") 

    # Sort the reference probabilities and reference percentiles to be ordered lowest to highest
    # This is required for the Python bisect command to work properly.
    rev_poes = poes[::-1]
    rev_ref_ptiles = ref_ptiles[::-1]

    # Set indices of the last, 50th, and 100th percentile associated with
    # array ref_ptiles
    ptile_last = np.size(ref_ptiles)-1
    ptile_50th = bisect.bisect(ref_ptiles,0.50)-1

    # Get number of locations
    num_locations = poes[0,:].size
    # Get number of probs to process
    num_probs = probs.size

    logger.debug("# Locations to process (based on POEs array) : " + str(num_locations) + " # probs to process : " + str(num_probs))
    # Check to see if reference ptiles passed are ordered least to greatest
    if not (all(ref_ptiles[i] <= ref_ptiles[i+1] for i in range(ref_ptiles.shape[0]-1))):
        raise ValueError("Reference percentiles are not in order (least to "
                        "greatest). Check passed array to make sure it is "
                        "correct and ordered.")
    try:
        # Calculate the associated or corresponding climatological percentile
        #  with the full fields array
        ptiles = np.array([
            # If prob is nan OR if greater than 1.0 OR less than 0.0, set to a nan value
            np.nan
                if np.isnan(prob) or prob > 1.0 or prob < 0.0
                
                # If prob == a poe value, set ptile to the associated reference ptile
                # NOTE: Python gives a longer ref_ptiles precision value than
                # specified, ie. 0.10000000000000001 instead of 0.1arg
            else ref_ptiles[np.argwhere(poes[:,loc] == prob)[0][0]]
                if prob in poes[:,loc]

                # If prob > poes[ptile_first,loc], extrapolate associated ptile value less than first reference percentile
                # Using the estimated 
            else ref_ptiles[0] + (prob - poes[0,loc])*((0.0-ref_ptiles[0])/(1.0-poes[0,loc]))
                if prob > poes[0,loc]

                # If prob < poes[ptile_last,loc], extrapolate associate ptile value greater than the last reference percentile
            else ref_ptiles[ptile_last] + (prob-poes[ptile_last,loc])*((1.0-ref_ptiles[ptile_last])/(0.0-poes[ptile_last,loc]))
                if prob < poes[ptile_last,loc]
                
            # If lowest POE value < prob < highest POE value, calculate ptile using linear interpolation
            # bisect.bisect(climo[:,loc],prob) will give the index of the closest upper adjacent climo value relative to the prob value
            else rev_ref_ptiles[bisect.bisect(rev_poes[:,loc],prob)-1] + \
                (rev_ref_ptiles[bisect.bisect(rev_poes[:,loc],prob)] - rev_ref_ptiles[bisect.bisect(rev_poes[:,loc],prob)-1]) \
                * ((prob - rev_poes[bisect.bisect(rev_poes[:,loc],prob)-1,loc])/ \
                (rev_poes[bisect.bisect(rev_poes[:,loc],prob),loc]-rev_poes[bisect.bisect(rev_poes[:,loc],prob)-1,loc]))
                if prob > rev_poes[0,loc] and prob < rev_poes[ptile_last,loc]

            # Else set to NaN
            else np.nan

                # Do for each desired probability
                for prob in probs
                    # Do for each location (in POEs)  
                    for loc in range(0,num_locations)
                    #for loc, prob in enumerate(probs)
        ])
    except:
        raise Exception("Probabilities to percentiles calculation failed.")

    # Reshape to 2-D [# locs x # probs]
    ptiles = np.reshape(ptiles, (num_probs,num_locations))
    
    logger.debug("Completed converting probabilities to percentile values.")
    return ptiles


def linear_interp_constant(first_ptile, debug=False):
    """ Returns the value of the linear interpolation constant (k) that is
    used for calculating a linear interpolated value beyond the bounds of
    available data, where the data is considered Gaussian. This can be used
    for any linear interpolation, regardless of the units.

    For example, given values of temperature associated with a range of
    climatological percentiles, where the percentiles represented begin at
    the 1st percentile and end with the 99th percentile, this constant can be
    used to linearly interpolate temperature values at percentiles less than
    the 1st percentile and greater than the 99th:
    Temp(@0th ptile) = k * (Temp(@1st ptile) - Temp(@50th ptile)) + Temp(
    @50th ptile)
    
    Parameters
    ----------
    first_ptile : float
        Percentile representing the first (lowest) percentile typically
        associated with a dataset that you are trying to use this constant
        for. Value must be in decimal format. If you do not have this, then
        can use a value such as 0.01.

    Returns
    -------
    Float  
        Value of a linear interpolation constant that can be used to
        interpolate values beyond the lowest and greatest percentile values
        available.

    Examples
    --------

    >>> from stats_utils.stats import linear_interp_constant
    >>> linear_interp_constant(0.01)
    1.3434782608695652
    """
    # Set logging level
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)
    logging.debug("Calculating linear interpolation constant k")
    k = None
    # Set reference percentile considered to represent the 0th percentile
    ref_ptile_0 = 0.001
    # 2-D tuple array of estimated standard deviations and associated
    # reference percentiles
    # This MUST be ordered from lowest to highest value for bisect function
    # to work
    std_array = np.array([
    [0.0001, 0.00023, 0.001, 0.00135, 0.002, 0.00621, 0.01, 0.02, 0.02275,
     0.06681, 0.10, 0.1587],
    [3.71, 3.5, 3.09, 3.0, 2.88, 2.5, 2.3, 2.05, 2.0, 1.5, 1.28, 1.0]
    ])
    if not (all(std_array[0, i] <= std_array[0, i+1] for i in range(std_array.shape[1]-1))):
        raise Exception("Reference standard deviation list set in the "
                        "function is not in order (least to greatest). Check "
                        "array std_array in the function to make sure it is "
                        "correct and ordered.")

    # Use bisect to determine the index of the closest associated reference
    # percentile to the reference percentile estimated to represent the 0th
    # an the passed first ptile
    # Calculate ratio of std[reference 0th ptile] / std[first available ptile]
    k = std_array[1, bisect.bisect(std_array[0, :], ref_ptile_0)-1] / \
        std_array[1, bisect.bisect(std_array[0, :], first_ptile)-1]

    return k


def find_nearest_index(array, value):
    """ Returns the index of the array containing the value closest to the given
    value.

    Parameters
    ----------
    array : array_like
        1-dimensional Numpy array of numbers
    value : real
        Value to compare array elements to

    Returns
    -------
    int
        The array index containing the value closest to the given value

    Examples
    --------

    >>> import numpy as np
    >>> from stats_utils.stats import find_nearest_index
    >>> arr = np.array([4, 5, 6, 7, 8])
    >>> find_nearest_index(arr, 6.1)
    2
    """
    array = np.array(array)
    # Get min of array minus the value
    idx = (np.abs(array-value)).argmin()
    return idx


def poe_to_moments(values, ptiles, axis=0):
    """ Returns the first 2 moments of the distribution defined by the given
    percentiles and values

    Credit goes to `this Matlab
    answers page <http://www.mathworks.com/matlabcentral/answers/83354-how
    -to-get-mean-and-std-from-a-known-cdf-curve#answer_92921>`_

    Parameters
    ----------
    values : array_like
        1-d NumPy array of values corresponding to the given ptiles
    ptiles : list
        List of percentiles (between 0 and 100)
    axis : int, optional
        Axis along which moments are calculated

    Returns
    -------
    tuple of float
        The array index containing the value closest to the given value

    Examples
    --------

    Compare moments calculated from percentiles to moments calculated from
    raw values

    >>> import numpy as np
    >>> from stats_utils.stats import poe_to_moments
    >>> ptiles = [1,  2,  5, 10, 15,
    ...          20, 25, 33, 40, 50,
    ...          60, 67, 75, 80, 85,
    ...          90, 95, 98, 99]
    >>> A = np.array([10,  6, 10,  6,  4,  5,  1,  2, 10,  6, 13,  4])
    >>> climo_vals = [np.percentile(A, ptile) for ptile in ptiles]
    >>> mean, std = poe_to_moments(climo_vals, ptiles)
    >>> print('Regular moments:')
    Regular moments:
    >>> print('Mean: {:.3f}, std: {:.3f}'.format(np.mean(A), np.std(A)))
    Mean: 6.417, std: 3.475
    >>> print('poe_to_moments():')
    poe_to_moments():
    >>> print('Mean: {:.3f}, std: {:.3f}'.format(mean, std))
    Mean: 6.218, std: 2.960

    Calculate moments along an axis with multi-dimensional data

    >>> import numpy as np
    >>> from stats_utils.stats import poe_to_moments
    >>> ptiles = [1,  2,  5, 10, 15,
    ...          20, 25, 33, 40, 50,
    ...          60, 67, 75, 80, 85,
    ...          90, 95, 98, 99]
    >>> A = np.array([[21,  6, 13,  3, 20,  5, 13, 10,  8, 21,  4,  9,],
    ...               [5,  20, 23,  6, 13,  8,  6, 13, 21,  2,  7, 16],
    ...               [24,  7,  0,  8,  8,  8,  6, 12,  0, 24, 17,  7],
    ...               [14,  8, 13, 21, 11, 10, 22, 10, 10, 19, 22,  4]])
    >>> climo_vals = np.array([np.percentile(A, ptile, axis=1) for ptile in
    ...     ptiles])
    >>> mean, std = poe_to_moments(climo_vals, ptiles)
    >>> print('Regular moments:')
    Regular moments:
    >>> print('- Mean: {}\\n- Std: {}'.format(np.mean(A, axis=1),
    ...     np.std(A, axis=1)))
    - Mean: [ 11.08333333  11.66666667  10.08333333  13.66666667]
    - Std: [ 6.30420935  6.73712764  7.58791071  5.73488351]
    >>> print('trapz() moments:')
    trapz() moments:
    >>> print('- Mean: {}\\n- Std: {}'.format(mean, std))
    - Mean: [ 10.79595  11.34645   9.6775   13.46155]
    - Std: [ 5.78240317  6.03460267  6.68999579  5.12680442]
    """

    # --------------------------------------------------------------------------
    # Check parameters
    #
    # Make sure the ptiles are sorted
    if sorted(ptiles) != ptiles:
        raise ValueError('ptiles should be sorted from lowest to highest')
    # Make sure the ptiles are within the range 0-100
    if min(ptiles) < 0 or max(ptiles) > 100:
        raise ValueError('ptiles should be within the range 0-100')

    # --------------------------------------------------------------------------
    # Calculate the moments using NumPy's trapz() function
    #
    # Created a MaskedArray version of values
    values = np.ma.masked_invalid(values)
    mean = np.trapz(values, np.array(ptiles)/100, axis=axis)
    std = (np.trapz((values - mean)**2, np.array(ptiles)/100,
                       axis=axis))**0.5

    return mean, std


def make_poe(ensemble_array, ptiles, kernel_std=math.sqrt(1 - 0.7 ** 2),
             member_axis=0, num_xvals=150, plot_points=None):
    """ Converts a set of discrete ensemble members into a continuous
    Probability of Exceedance (POE) distribution. The members are each "dressed"
    with a "kernel" (small Gaussian PDF), and then the kernels are all averaged
    to obtain a single PDF that is essentially a continuous representation of
    the distribution described by the discrete members.

    Parameters
    ----------
    ensemble_array : array_like
        N-dimensional Numpy array of discrete member values. The array can optionally be masked.
        If masked then the mask will be respected and the final POE will be masked wherever all
        the ensemble members were masked.
    ptiles : list
        List of percentiles at which to return the POE
    kernel_std : real, optional
        Standard deviation of the kernels. Defaults to a PDF in which the best
        member has a 0.7 correlation with observations.
    member_axis : int, optional
        Axis containing the varying members, over which the POE is calculated.
        Defaults to 0
    num_xvals : int, optional
        Number of discrete X values for generating PDFs - defaults to 150

    Returns
    -------
    array_like
        NumPy array of POE values at the given percentiles

    Examples
    --------


    2
    """

    # --------------------------------------------------------------------------
    # Create kernels for all members
    #
    num_members = ensemble_array.shape[member_axis]
    # Create list of x values in standardized space
    x = np.linspace(-4, 4, num_xvals)
    # Create an array to store all pdfs
    final_pdf = np.empty((x.shape[0], ensemble_array.shape[1]))
    # Make ensemble_array a masked array if it isn't already (so as not to break the mask check
    # below)
    if not np.ma.is_masked(ensemble_array):
        ensemble_array = np.ma.array(ensemble_array, mask=False)
    # Loop over each grid point
    for g in range(ensemble_array.shape[1]):
        # If this value is masked, set the final PDF to all NaNs
        if np.all(ensemble_array[:, g].mask):
            final_pdf[:, g] = np.empty(x.size) * np.nan
        else:
            # Create kernels around ensemble members and sum over all members
            final_pdf[:, g] = np.sum(
                scipy.stats.norm.pdf(
                    x,
                    ensemble_array[~np.isnan(ensemble_array[:, g]), g, np.newaxis],
                    kernel_std
                ) / num_members, axis=0
            )
    # --------------------------------------------------------------------------
    # Convert into a POE (1 - CDF)
    #
    denom = np.max(np.cumsum(final_pdf, axis=0), axis=0)
    denom = np.where(denom == 0, np.nan, denom)
    final_poe = 1 - np.cumsum(final_pdf, axis=0) / denom

    # --------------------------------------------------------------------------
    # Return the POE at the given percentiles
    #
    output = np.empty((len(ptiles), ensemble_array.shape[1]))
    ptile_indexes = []
    for ptile in scipy.stats.norm.ppf(np.array(ptiles)/100):
        ptile_indexes.append(find_nearest_index(x, ptile))
    for g in range(ensemble_array.shape[1]):
        output[:, g] = final_poe[ptile_indexes, g]

    # ---------------------------------------------------------------------------
    # Plot all ensemble members
    #
    # if plot_point:
    #     try:
    #         matplotlib.rcParams['font.size'] = 10
    #         # matplotlib.rcParams['legend.fontsize'] = 'small'
    #         # Create a figure
    #         fig, ax1 = matplotlib.pyplot.subplots(1, 1)
    #         # Loop over all standardized ensemble members and plot their kernel
    #         kernels = np.empty(shape=(num_members, int(num_xvals))) * np.nan
    #         # Loop over all ensemble members and create their kernels
    #         for m in range(num_members):
    #             kernels[m] = scipy.stats.norm.pdf(x, ensemble_array[m, plot_point],
    #                                               kernel_std) / num_members
    #         for member in range(num_members):
    #             if member == 0:
    #                 ax1.plot(x, kernels[member], 'b', label='Ensemble member')
    #             else:
    #                 ax1.plot(x, kernels[member], 'b')
    #         # Plot the average of all kernels (final PDF)
    #         ax1.plot(x, final_pdf[:, plot_point], 'r', label='Ensemble PDF')
    #         # Plot the average of all kernels in POE form
    #         ax2 = ax1.twinx()
    #         ax2.plot(x, final_poe[:, plot_point], 'k', label='Ensemble POE')
    #         # Create legends
    #         leg1 = ax1.legend(loc="upper left")
    #         ax2.add_artist(leg1)
    #         leg2 = ax2.legend(loc="upper right")
    #         # Save the plot
    #         matplotlib.pyplot.savefig('stats.png')
    #     except:
    #         logger.warning('Can\'t plot stats...')

    return output


def poe_to_terciles(poe, ptiles):
    """

    Parameters
    ----------
    discrete_members : array_like
        1-dimensional Numpy array of discrete member values
    ptiles : list
        List of percentiles at which to return the POE
    kernel_std : real, optional
        Standard deviation of the kernels. Defaults to a PDF in which the best
        member has a 0.7 correlation with observations.
    make_plot : boolean
        Whether to make a plot of the PDFs and POE. Defaults to False

    Returns
    -------
    array_like
        NumPy array of POE values at the given percentiles

    Examples
    --------


    """
    # --------------------------------------------------------------------------
    # Verify input
    #
    # ptiles must contain 33 and 67
    if 33 not in ptiles or 67 not in ptiles:
        raise ValueError('ptiles must contain 33 and 67')

    below = 1 - poe[find_nearest_index(ptiles, 33), :]
    above = poe[find_nearest_index(ptiles, 67), :]
    near = 1 - (below + above)

    return below, near, above


def put_terciles_in_one_array(below, near, above):
    """
    Combines tercile probabilities into a single array for plotting purposes

    Belows become negative probabilities, and near normal becomes zero
    """
    # Make an empty array to store above, near, and below
    all_probs = np.empty(below.shape)
    all_probs[:] = np.nan
    with np.errstate(invalid='ignore'):
        # Insert belows where they are the winning category and above 33%
        all_probs = np.where((below > 0.333) & (below > above), -1*below,
                             all_probs)
        # Insert aboves where they are the winning category and above 33%
        all_probs = np.where((above > 0.333) & (above > below), above, all_probs)
        # Insert nears where neither above or below are above 33%
        all_probs = np.where((below <= 0.333) & (above <= 0.333), 0, all_probs)
    # Return all_probs
    return all_probs


