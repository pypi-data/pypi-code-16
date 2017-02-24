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
# logreg.py - This file is part of the PySptools package.
#


from sklearn import linear_model
from .base import HyperBaseClassifier


class HyperLogisticRegression(linear_model.LogisticRegression, HyperBaseClassifier):
    """
    Apply scikit-learn LogisticRegression on a hypercube.
    
    For the __init__ class contructor parameters: `see the sklearn.linear_model.LogisticRegression class parameters`

    The class is intrumented to be use with the scikit-learn cross validation.
    It use the plot and display methods from the class Output.
    """

    def __init__(self, penalty='l2', dual=False, tol=1e-4, C=1.0,
                 fit_intercept=True, intercept_scaling=1, class_weight=None,
                 random_state=None, solver='liblinear', max_iter=100,
                 multi_class='ovr', verbose=0, warm_start=False, n_jobs=1):
        super(HyperLogisticRegression, self).__init__(penalty=penalty,
                dual=dual,
                tol=tol,
                C=C,
                fit_intercept=fit_intercept,
                intercept_scaling=intercept_scaling,
                class_weight=class_weight,
                random_state=random_state,
                solver=solver,
                max_iter=max_iter,
                multi_class=multi_class,
                verbose=verbose,
                warm_start=warm_start,
                n_jobs=n_jobs)
        HyperBaseClassifier.__init__(self, 'HyperLogisticRegression')

    def fit_rois(self, M, ROIs):
        """
        Fit the HS cube M with the use of ROIs.

        Parameters:
            M: `numpy array`
              A HSI cube (m x n x p).

            ROIs: `ROIs type`
                Regions of interest instance.
        """
        X, y = self._fit_rois(M, ROIs)
        super(HyperLogisticRegression, self).fit(X, y)

    def classify(self, M):
        """
        Classify a hyperspectral cube using the clusters defined by the ROIs.

        Parameters:
            M: `numpy array`
              A HSI cube (m x n x p).

        Returns: `numpy array`
              A class map (m x n x 1).
        """
        img = self._convert2D(M)
        cls = super(HyperLogisticRegression, self).predict(img)
        self.cmap = self._convert3d(cls, M.shape[0], M.shape[1])
        return self.cmap
