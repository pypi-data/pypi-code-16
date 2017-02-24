#
#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Christian Therien
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
#
# crossval.py - This file is part of the PySptools package.
#

from __future__ import print_function


import numpy as np
import sklearn.cross_validation as cv
from sklearn import grid_search


def vsplit(M, mask, frac):
    """
    Split vertically a hypercube and a mask by percent frac.
    Keep the hypercube and mask left part.
    
    It's use for the tests and demo only. A part of the cube is use for learning,
    the other part is use for fit.
    Nothing generic here!
    """
    y = M.shape[1]
    v = int(y * frac)
    X3d = M[:,0:v,:]
    Y3d = mask[:,0:v]
    X = _convert2D(X3d)
    Y = np.reshape(Y3d, Y3d.shape[0]*Y3d.shape[1])
    return X, Y


def _convert2D(M):
    h, w, numBands = M.shape
    return np.reshape(M, (w*h, numBands))


class HyperEstimatorCrossVal(object):
    """ Do a cross validation on a hypercube or a concatenation of hypercubes.
        Use scikit-learn KFold and GridSearchCV. """

    def __init__(self, estimator, label, param_grid):
        """
        Create a new HyperEstimatorCrossVal.

        Parameters:
            estimator: `class name`
                One of HyperSVC, HyperRandomForestClassifier, HyperKNeighborsClassifier
                HyperLogisticRegression.

            label: `string`
                The feature name, use with the print method.

            param_grid: `dic`
                A dic of parameters to be cross validated.
                Ex. {'C': [10,20,30,50], 'gamma': [0.1,0.5,1.0,10.0]} for
                HyperSVC.
        """
        self.estimator = estimator
        self.feature_name = label
        self.param_grid = param_grid

    def fit_cube(self, M, mask):
        """
        Do the cross validation on a hypercube section
        determined by a binary mask. 
            
        Parameters:
            M: `numpy array`
                A HSI cube (m x n x p).

            mask: `numpy array`
                A binary mask, when *True* the corresponding spectrum is part of the
                cross validation.        
        """
        X = _convert2D(M)
        Y = np.reshape(mask, mask.shape[0]*mask.shape[1])
        self._cross_val(X, Y, self.param_grid)

    def fit_multicube(self, M_list, mask_list):
        """
        Do the cross validation on a hypercube list where the sections
        are determined by a list of binary mask. 

        Parameters:
            M_list: `numpy array list`
                A list of HSI cube (m x n x p).

            mask_list: `numpy array list`
                A list of binary mask, when *True* the corresponding spectrum is part of the
                cross validation.        
        """
        i = 0
        for m,msk in zip(M_list, mask_list):
            x = _convert2D(m)
            y = np.reshape(msk, msk.shape[0]*msk.shape[1])
            if i == 0:
                X = x
                Y = y
                i = 1
            else:
                X = np.concatenate((X, x))
                Y = np.concatenate((Y, y))
        self._cross_val(X, Y, self.param_grid)

    def fit(self, X, Y):
        """
        Do the cross validation on each spectrum of X defined by Y.

        Parameters:
            X: `numpy array`
                A vector where each element is a spectrum.

            Y: `numpy array`
                A vector where each element is a binary value, one or zero. A value of one
                means that the corresponding spectrum in X belong to the feature
                and will be cross validated.
        """
        self._cross_val(X, Y, self.param_grid)

    def _cross_val(self, X, Y, grid):
        kf = cv.KFold(X.shape[0], n_folds=2, shuffle=True)
        self.gcv = grid_search.GridSearchCV(self.estimator(), grid, cv=kf, refit=False)
        self.gcv.fit(X, Y)

    def _convert2D(self, M):
        h, w, numBands = M.shape
        return np.reshape(M, (w*h, numBands))
        
    def get_best_params(self):
        """
        Returns: `dic`
            Dic of best match.
        """
        return self.gcv.best_params_
        
    def print(self):
        """ Print a summary for the cross validation results """
        print('================================================================')
        print('Cross validation results for: {}'.format(self.feature_name))
        print('Param grid:', self.param_grid)
        print('n folds: 2')
        print('Shuffle: True')
        print('================================================================')
        print('Best score:', self.gcv.best_score_)
        print('Best params:', self.gcv.best_params_)
        print('================================================================')
        print('All scores')
        for s in self.gcv.grid_scores_:
            print(s)
        print('================================================================')
        print()
