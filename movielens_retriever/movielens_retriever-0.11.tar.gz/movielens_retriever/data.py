#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import sys
from scipy import io
import os
import zipfile
import pandas as pd
import numpy as np
import requests
import scipy.sparse as sp


__author__ = "David Solís, Juan Galán Páez, José Antonio Guerrero"
__copyright__ = "Copyright 2017, Datrik Intelligence, S.A. (Spain)"
__credits__ = ["David Solís", "Juan Galán Paez", "Jose Antonio Guerrero"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Datrik Intelligence"
__email__ = "info@datrik.com"
__status__ = "Production"


if sys.version_info[0] < 3:
    from StringIO import StringIO as IOReader
else:
    from io import BytesIO as IOReader

class MoviLens:

    DS10K = "100k"
    DS20M = "20m"

    def __init__(self, dataset_type, threshold=None, save_interaction_matrix=True,
                 protocol=5, protocol_sorted=True):

        self.dataset_type = dataset_type
        self.threshold = threshold
        self.save_interaction_matrix = save_interaction_matrix
        self.validation_size = 0.3
        self.protocol = protocol
        self.protocol_sorted = protocol_sorted



    def _download_data(self, dest_path):
        """
        Download the dataset.
        """

        print("Downloading data... ")
        url = 'http://files.grouplens.org/datasets/movielens/ml-%s.zip' % self.dataset_type
        req = requests.get(url, stream=True)

        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))

        with open(dest_path, 'wb') as fd:
            for chunk in req.iter_content(chunk_size=1024):
                fd.write(chunk)


    def _get_raw_data(self):
        """
        Return the raw lines of the train and test files.
        """

        path = self.__get_raw_path(self.dataset_type)

        if not os.path.isfile(path):
            self._download_data(path)

        if self.dataset_type == MoviLens.DS10K:

            with zipfile.ZipFile(path) as datafile:
                return (pd.read_csv(IOReader(datafile.read('ml-100k/ua.base')), sep="\t"),
                        pd.read_csv(IOReader(datafile.read('ml-100k/ua.test')), sep="\t"))

        else:
            with zipfile.ZipFile(path) as datafile:
                data = pd.read_csv(IOReader(datafile.read('ml-20m/ratings.csv')), sep=",")

            if self.protocol_sorted:
                # create a order column (order of each rating by user)
                data['order'] = data.sort_values(by=['timestamp']).groupby(by='userId').cumcount()
            else:
                # create a order column (order of each rating by user)
                data['order'] = data.reindex(np.random.permutation(data.index)).groupby(by='userId').cumcount()

            #split by users
            users = data.userId.unique()
            users_split = len(users) - int(len(users) * self.validation_size)
            ds_train = data[data.userId.isin(users[:users_split])]
            ds_test = data[data.userId.isin(users[users_split:])]


            # given protocol: first N ratings will be using to train
            if self.protocol > 0:
                ds_train = pd.concat((ds_train, ds_test[ds_test.order <= self.protocol]), axis=0)
                ds_test = ds_test[ds_test.order > self.protocol]

            # all_but protocol: first N ratings will be using to test (rest to train)
            else:
                ds_train = pd.concat((ds_train, ds_test[ds_test.order >= abs(self.protocol)]), axis=0)
                ds_test = ds_test[ds_test.order < abs(self.protocol)]


            del ds_train['order']
            del ds_test['order']

            return ds_train, ds_test

    def __build_interaction_matrix(self, rows, cols, data):
        """
        Build the training matrix (no_users, no_items),
        with ratings >= threshold being marked as positive and
        the rest as negative.
        """

        if not self.threshold:
            mat = sp.coo_matrix((data.iloc[:, 2], (data.iloc[:, 0], data.iloc[:, 1])),
                                shape=(rows, cols), dtype=np.int32)

            return mat
        else:
            mat = sp.lil_matrix((rows, cols), dtype=np.int32)

            for uid, iid, rating in zip(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2]):

                if self.threshold:
                    rating = 1.0 if rating >= self.threshold else -1.0

                mat[uid, iid] = rating

            return mat.tocoo()

    def __get_raw_path(self, dataset_type):
        """
        Get path to the movielens dataset file.
        """

        return os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
                            'ml-%s.zip' % dataset_type )

    def _get_matrix_paths(self):
        train_path, test_path = "ml-train_%s" % self.dataset_type, "ml-test_%s" % self.dataset_type

        if self.threshold:
            train_path = "%s_th%0.2f" % (train_path, self.threshold)
            test_path = "%s_th%0.2f" % (test_path, self.threshold)

        train_path, test_path = train_path + '.mtx', test_path + '.mtx'

        return os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),train_path), \
               os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),test_path)



    def get_data(self):
        """
        Return the train a test interaction matrix
        """

        m_train_path, m_test_path = self._get_matrix_paths()

        if not os.path.exists(m_test_path):
            print("Reading matrices... ")
            train_data, test_data = self._get_raw_data()

            rows = max(train_data.iloc[:, 0].max(), test_data.iloc[:, 0].max()) + 1
            cols = max(train_data.iloc[:, 1].max(), test_data.iloc[:, 1].max()) + 1

            print("Building interaction matrices... ")
            m_train, m_test = (self.__build_interaction_matrix(rows, cols, train_data),
                               self.__build_interaction_matrix(rows, cols, test_data))

            if self.save_interaction_matrix:
                print("Saving interaction matrices... ")
                io.mmwrite(m_train_path, m_train)
                io.mmwrite(m_test_path, m_test)

        else:
            print("Reading interaction matrices... ")
            m_train, m_test = io.mmread(m_train_path) , io.mmread(m_test_path)


        return m_train, m_test