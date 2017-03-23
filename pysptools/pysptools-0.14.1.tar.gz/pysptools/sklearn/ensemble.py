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
# ensemble.py - This file is part of the PySptools package.
#


import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from .base import HyperBaseClassifier


def _plot_feature_importances(feature_importances_, path=None, suffix=None):
    import os.path as osp
    import matplotlib.pyplot as plt

    n_features_ = len(feature_importances_)
    nb_bands_pos = np.arange(n_features_)
    bands_id = [str(n+1) for n in range(n_features_)]
    n_graph = 1
    x = 0
    min_ = np.min(feature_importances_)
    max_ = np.max(feature_importances_)
    
    nb_to_plot = 15
    for i in range(n_features_):
        if (i+1) % nb_to_plot == 0 :
            if path != None: plt.ioff()
            fig, ax = plt.subplots()
            nb_bands_pos = np.arange(nb_to_plot)

            ax.barh(nb_bands_pos, feature_importances_[x:i+1],
                    align='center', color='green', height=0.8)
            ax.set_yticks(nb_bands_pos)
            ax.set_yticklabels(bands_id[x:i+1])
            ax.invert_yaxis()  # labels read top-to-bottom
            ax.set_xbound(min_, max_)
            ax.set_xlabel('Importances value')
            ax.set_ylabel('band #')
    
            if path != None:
                ax.set_title('Feature Importances #{}'.format(n_graph))
                if suffix == None:
                    fout = osp.join(path, 'HyperRandomForestClassifier_feat_imp_{}.png'.format(n_graph))
                else:
                    fout = osp.join(path, 'HyperRandomForestClassifier_feat_imp_{0}_{1}.png'.format(suffix,n_graph))
                try:
                    plt.savefig(fout)
                except IOError:
                    raise IOError('in HyperRandomForestClassifier.plot_feature_importances, no such file or directory: {0}'.format(path))
            else:
                if suffix == None:
                    ax.set_title('Feature Importances #{}'.format(n_graph))
                else:
                    ax.set_title('Feature Importances #{0} {1}'.format(n_graph, suffix))
                plt.show()
            n_graph += 1
            x = i+1
            plt.clf()
    if x < n_features_:
        if path != None: plt.ioff()
        end = n_features_
        fig, ax = plt.subplots()
        nb_bands_pos = np.arange(end-x)
        ax.barh(nb_bands_pos, feature_importances_[x:end],
                align='center', color='green', height=0.001)
        ax.set_yticks(nb_bands_pos)
        ax.set_yticklabels(bands_id[x:end])
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xbound(min_, max_)
        ax.set_xlabel('Importances value')
        ax.set_ylabel('band #')

        if path != None:
            ax.set_title('Feature Importances #{}'.format(n_graph))
            if suffix == None:
                fout = osp.join(path, 'HyperRandomForestClassifier_feat_imp_{}.png'.format(n_graph))
            else:
                fout = osp.join(path, 'HyperRandomForestClassifier_feat_imp_{0}_{1}.png'.format(suffix,n_graph))
            try:
                plt.savefig(fout)
            except IOError:
                raise IOError('in HyperRandomForestClassifier.plot_feature_importances, no such file or directory: {0}'.format(path))
        else:
            if suffix == None:
                ax.set_title('Feature Importances #{}'.format(n_graph))
            else:
                ax.set_title('Feature Importances #{0} {1}'.format(n_graph, suffix))
            plt.show()
        plt.clf()          
    plt.close()

    
class HyperGradientBoostingClassifier(GradientBoostingClassifier, HyperBaseClassifier):
    """
    Apply scikit-learn GradientBoostingClassifier on a hypercube.
    
    For the __init__ class contructor parameters: `see the sklearn.ensemble.GradientBoostingClassifier class parameters`

    The class is intrumented to be use with the scikit-learn cross validation.
    It use the plot and display methods from the class Output.
    """

    cmap = None

    def __init__(self, loss='deviance', learning_rate=0.1, n_estimators=100,
                 subsample=1.0, criterion='friedman_mse', min_samples_split=2,
                 min_samples_leaf=1, min_weight_fraction_leaf=0.,
                 max_depth=3, min_impurity_split=1e-7, init=None,
                 random_state=None, max_features=None, verbose=0,
                 max_leaf_nodes=None, warm_start=False,
                 presort='auto'):
        super(HyperGradientBoostingClassifier, self).__init__(
            loss=loss, learning_rate=learning_rate, n_estimators=n_estimators,
            criterion=criterion, min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_depth=max_depth, init=init, subsample=subsample,
            max_features=max_features,
            random_state=random_state, verbose=verbose,
            max_leaf_nodes=max_leaf_nodes,
            min_impurity_split=min_impurity_split,
            warm_start=warm_start,
            presort=presort)
        HyperBaseClassifier.__init__(self, 'HyperGradientBoostingClassifier')

    def fit(self, X, y):
        """
        Same as the sklearn.ensemble.GradientBoostingClassifier fit call.

        Parameters:
            X: `numpy array`
                A vector (n_samples, n_features) where each element *n_features* is a spectrum.

            y: `numpy array`
                Target values (n_samples,). A zero value is the background. A value of one or more is a class value.
        """
        super(HyperGradientBoostingClassifier, self)._set_n_clusters(int(np.max(y)))
        super(HyperGradientBoostingClassifier, self).fit(X, y)

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
        super(HyperGradientBoostingClassifier, self).fit(X, y)

    def classify(self, M):
        """
        Classify a hyperspectral cube.

        Parameters:
            M: `numpy array`
              A HSI cube (m x n x p).

        Returns: `numpy array`
              A class map (m x n x 1).
        """
        img = self._convert2D(M)
        cls = super(HyperGradientBoostingClassifier, self).predict(img)
        cmap = self._convert3d(cls, M.shape[0], M.shape[1])
        super(HyperGradientBoostingClassifier, self)._set_cmap(cmap)
        return self.cmap

    def plot_feature_importances(self, path, suffix=''):
        _plot_feature_importances(self.feature_importances_, path, suffix=suffix)

    def display_feature_importances(self, suffix=''):
        _plot_feature_importances(self.feature_importances_, None, suffix=suffix)


class HyperRandomForestClassifier(RandomForestClassifier, HyperBaseClassifier):
    """
    Apply scikit-learn RandomForestClassifier on a hypercube.
    
    For the __init__ class contructor parameters: `see the sklearn.ensemble.RandomForestClassifier class parameters`

    The class is intrumented to be use with the scikit-learn cross validation.
    It use the plot and display methods from the class Output.
    """

    cmap = None

    def __init__(self,
                 n_estimators=10,
                 criterion="gini",
                 max_depth=None,
                 min_samples_split=2,
                 min_samples_leaf=1,
                 min_weight_fraction_leaf=0.,
                 max_features="auto",
                 max_leaf_nodes=None,
                 bootstrap=True,
                 oob_score=False,
                 n_jobs=1,
                 random_state=None,
                 verbose=0,
                 warm_start=False,
                 class_weight=None):
        super(HyperRandomForestClassifier, self).__init__(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            max_leaf_nodes=max_leaf_nodes,
            bootstrap=bootstrap,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            warm_start=warm_start,
            class_weight=class_weight)
        HyperBaseClassifier.__init__(self, 'HyperRandomForestClassifier')

    def fit(self, X, y):
        """
        Same as the sklearn.ensemble.RandomForestClassifier fit call.

        Parameters:
            X: `numpy array`
                A vector (n_samples, n_features) where each element *n_features* is a spectrum.

            y: `numpy array`
                Target values (n_samples,). A zero value is the background. A value of one or more is a class value.
        """
        super(HyperRandomForestClassifier, self)._set_n_clusters(int(np.max(y)))
        super(HyperRandomForestClassifier, self).fit(X, y)

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
        super(HyperRandomForestClassifier, self).fit(X, y)

    def classify(self, M):
        """
        Classify a hyperspectral cube.

        Parameters:
            M: `numpy array`
              A HSI cube (m x n x p).

        Returns: `numpy array`
              A class map (m x n x 1).
        """
        img = self._convert2D(M)
        cls = super(HyperRandomForestClassifier, self).predict(img)
        cmap = self._convert3d(cls, M.shape[0], M.shape[1])
        super(HyperRandomForestClassifier, self)._set_cmap(cmap)
        return self.cmap

    def plot_feature_importances(self, path, suffix=''):
        _plot_feature_importances(self.feature_importances_, path, suffix=suffix)

    def display_feature_importances(self, suffix=''):
        _plot_feature_importances(self.feature_importances_, None, suffix=suffix)
