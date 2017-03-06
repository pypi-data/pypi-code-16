"""

Base module.

"""

import numpy as np
import pandas as pd

from sklearn.base import TransformerMixin


class DataFrameDummies(TransformerMixin):

    """

    Attributes
    ----------

    cat_cols : list
        List of categorical columns

    final_cols : list
        List of all columns with dummy values

    """

    def __init__(self):

        self.cat_cols = []
        self.final_cols = []

    def fit(self, df):

        """

        Parameters
        ----------

        df : pd.DataFrame
            Provides the column names to be used.

        Returns
        -------

        DataFrameDummies
            Itself.

        """

        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)

        self.cat_cols = list(df.columns)

        self.final_cols = list(pd.get_dummies(df).columns)

        return self

    def transform(self, df):

        """

        Parameters
        ----------

        df : pd.DataFrame
            Data to be dummified.

        Returns
        -------

        pd.DataFrame
            Transformed data

        """

        if isinstance(df, pd.Series):
            df = pd.DataFrame(df)

        df = df.copy()

        # check if all values are null
        if pd.isnull(df).all().all():

            # return empty dataframe
            for col in self.final_cols:
                df[col] = np.nan

            return df[self.final_cols]

        dfd = pd.get_dummies(df)

        # insert categories not present in the transformed dataframe
        for col in self.final_cols:
            if col not in dfd.columns:
                dfd[col] = 0

        # replace values with nan where the original dataframe was null
        for cat_col in self.cat_cols:
            dfd.loc[df[cat_col].isnull(), dfd.columns.str.startswith(cat_col)] = np.nan

        return dfd[self.final_cols]


class NPArrayDummies(TransformerMixin):

    """

    Attributes
    ----------

    labels : list
        List of labels

    """

    def __init__(self):

        self.labels = []

    def fit(self, X):

        """

        Parameters
        ----------

        X : np.ndarray
            Provides the labels.

        Returns
        -------

        NPArrayDummies
            Itself.

        """

        self.labels = np.unique(X[pd.notnull(X)])

        return self

    def transform(self, X):

        """

        Parameters
        ----------

        X : np.ndarray
            Data to be dummified.

        Returns
        -------

        Xt : np.ndarray
            Transformed data

        """

        Xt = np.empty([len(X), len(self.labels)])

        for idx, label in enumerate(self.labels):
            Xt[:, idx] = np.ravel((X == label).astype(int))

        Xt[np.ravel(pd.isnull(X)), :] = np.nan

        return Xt
