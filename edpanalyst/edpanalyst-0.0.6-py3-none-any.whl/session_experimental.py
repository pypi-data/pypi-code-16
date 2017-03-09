from pandas import DataFrame  # type: ignore
from typing import Any, Dict, List, Tuple  # NOQA

# This is imported from `future` so its type checking is wonky
import itertools
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import six

DEFAULT_LIMIT = 10


class PopulationModelExperimental(object):
    """A collection of less nailed-down APIs on PopulationModels.

    You should generally not create one of these yourself. Instead, get one via
    a PopulationModel's `.experimental` property.
    """
    def __init__(self, population_model):
        self._popmod = population_model

    def confidence_overlay(self,
                           targets=None,         # type: List[str]
                           rowids=None,          # type: List[int]
                           infer_present=False,  # type: bool
                           select=None           # type: List[str]
                           ):                    # type: (...) -> DataFrame
        """
        Basically just calls likelihood and infer and returns a data frame
        containing the results of both calls joined together.

        Args:
            targets: The columns to infer.
            rowids: The rowids to restrict results to. If not specified
                returns all rows.
            infer_present: True to infer results for values which are present
                in the underlying data. False will cause them to be returned as
                NA.
            select: A list of additional columns to select and return in the
                data frame.
        """
        targets = self._popmod._columns_from_arg(targets)
        # TODO(asilvers): It's fast becoming time to introduce 'ALL'
        rowids = self._popmod._rowids_from_arg(rowids)
        likelihood = self._popmod.likelihood(
            targets=targets, rowids=rowids, select=select,
            probability_suffix='_p')

        inferred = self._popmod.infer(
            targets=targets, rowids=rowids, infer_present=infer_present,
            confidence_suffix='_conf')

        column_order = (select or []) + self._popmod._id_cols()
        for c in targets:
            column_order.extend((c,
                                 c + '_p',
                                 c + '_inferred',
                                 c + '_conf'))
        overlay = likelihood.join(inferred, rsuffix='_inferred')
        return overlay[column_order]

    def unlikely_values(self,
                        target_column,          # type: str
                        given_columns=None,     # type: List[str]
                        num_outliers=10,        # type: int
                        num_relevant=0,         # type: int
                        rowids=None,            # type: List[int]
                        select=None,            # type: List[str]
                        probability_column='p'  # type: str
                        ):                      # type: (...) -> DataFrame
        """
        Find the `num_outliers` rows whose value in `target_column` is least
        likely given the values in the rest of its columns.

        Args:
            target_column: The column in which to find outliers.
            given_columns: The columns on which to condition the logpdf call
                when computing likelihood. Defaults to all modeled columns
                other than target_column. It is an error to include
                `target_column` in this list.
            num_outliers: The number of outliers to return.
            select: A list of additional columns to select and return in the
                data frame.
            num_relevant: A number of columns to include in addition to the
                select columns, chosen by their column_relevance to target.
            rowids: The rowids to restrict the search to. If not specified
                looks for outliers across all rows.
            probability_column: The name of the column in which to return the
                likelihoods.
        """
        if num_relevant > 0:
            # relevant_columns will return the target, so +1.
            relevant = self._popmod.relevant_columns(
                target_column, num_relevant + 1)
            relevant = list(relevant.column)
            relevant.remove(target_column)
            select = (select or []) + relevant
        df = self._popmod.joint_likelihood(
            targets=[target_column],
            given_columns=given_columns,
            rowids=rowids,
            probability_column=probability_column,
            select=select)
        df.sort_values(by=probability_column, ascending=True, inplace=True)
        df = df[0:num_outliers]
        return df

    def column_value_probabilities(
            self,
            target_column,          # type: str
            given=None,             # type: Dict[str, Any]
            probability_column='p'  # type: str
            ):                      # type: (...) -> DataFrame
        """Return the probability of the possible values in a column.

        Returns a data frame containing two columns: `target_column` whose
        values correspond to the possible values of that column, and
        `probability_column`. The `probability_column` column's value
        represents the probability that `target_column` takes on the value
        in that row under the given conditions.

        Currently only works on categorical columns.
        """
        col_def = self._popmod.schema[target_column]
        if col_def.stat_type != 'categorical':
            raise ValueError('Column must be categorical')

        vals = [v.value for v in col_def.values]
        targets = {target_column: vals}
        df = self._popmod.joint_probability(
            targets=targets, given=given,
            probability_column=probability_column)
        return df.sort_values(probability_column, ascending=False)

    def _display_value_map(self,
                           col   # type: str
                           ):    # type: (...) -> Dict[str, str]
        """Return a map from values to their display values for a column.

        This maps a value to its `display_value` if it exists, or just itself
        otherwise.
        """
        col_def = self._popmod.schema[col]
        return {v.value: v.display_value or v.value
                for v in col_def.values}

    def wheres_the_info(self,
                        col1,        # type: str
                        col2,        # type: str
                        num_cells=5  # type: int
                        ):
        # type: (...) -> List[Tuple[str, str, float]]
        """Returns the values for which the MI is the highest.

        The values are returned as a list of (val1, val2, mi) tuples) of
        length `num_cells`.

        Suppose you're efficiently encoding data distributed by the joint
        distribution of col1 and col2. Then, `mi` is the number of bits you'll
        save on average for each datum for attributable to (val1, val2) being
        encoded efficiently relative to the product of the marginals. If `mi`
        is negative, that amount of efficiency is _lost_ encoding that
        particular combination.

        Currently only works on two categorical columns.
        """
        pt = self._joint_probability_table(col1, col2)
        marg_pt = self._product_of_marginal_probabilities_table(pt)
        # Log base 2 so we get bits, not nats
        mi_table = pt * np.log2(pt / marg_pt)
        total_mi = np.sum(np.sum(mi_table))
        assert total_mi >= 0
        # Total MI is non-negative, but the individual elements don't have to
        # be. Make them all positive for sorting purposes.
        mi_abs_table = np.absolute(mi_table)

        # Use display_values if they exist.
        # TODO(asilvers): Probably want a more general way of doing this
        # and want to start using it in other methods
        mi_abs_table = mi_abs_table.rename(
            index=self._display_value_map(col1),
            columns=self._display_value_map(col2))

        largest = mi_abs_table.stack().nlargest(num_cells)
        res = []
        for (c1v, c2v), mi_abs in largest.iteritems():
            # Sort based on mi_abs, but then look up the original mi
            mi = mi_table[c2v][c1v]
            res.append((c1v, c2v, mi))
        return res

    def wheres_the_r2(self,
                      col1,        # type: str
                      col2,        # type: str
                      num_cells=5  # type: int
                      ):
        # type: (...) -> List[Tuple[str, str, float]]
        """Returns values where the joint and and marginal product differ.

        For a pair of columns, returns the values in the observed data for
        which the difference between the joint probability and the product of
        the marginal probabilities is the highest.

        The values are returned as a list of (val1, val2, difference) tuples
        of length `num_cells`.

        Currently only works on two categorical columns.
        """
        pt = self._joint_probability_table(col1, col2)
        marg_pt = self._product_of_marginal_probabilities_table(pt)

        # Compute a table of the differences so we can preserve the sign and
        # figure out whether values are higher or lower than `marg_pt`. The
        # values are (actual - `marg_pt`), so positive values mean that that
        # cell occurs more often than the product of the marginals.
        diff_table = pt - marg_pt
        # Square the table so we can sort ignoring sign.
        diff2_table = diff_table ** 2

        # Use display_values if they exist.
        # TODO(asilvers): Probably want a more general way of doing this
        # and want to start using it in other methods
        diff2_table = diff2_table.rename(
            index=self._display_value_map(col1),
            columns=self._display_value_map(col2))

        largest = diff2_table.stack().nlargest(num_cells)
        res = []
        for (c1v, c2v), diff2 in six.iteritems(largest):
            # Sort based on diff2, but then look up the original diff
            diff = diff_table[c2v][c1v]
            res.append((c1v, c2v, diff))
        return res

    def _joint_probability_table(self,
                                 col1,  # type: str
                                 col2   # type: str
                                 ):     # type: (...) -> DataFrame
        """Returns a table of the joint probabilities between two columns.

        Only works for categorical columns. asilvers@ is trying to think of the
        right abstraction for continuous columns.
        """
        col1_def = self._popmod.schema[col1]
        col2_def = self._popmod.schema[col2]
        if (col1_def.stat_type != 'categorical' or
                col2_def.stat_type != 'categorical'):
            raise NotImplementedError(
                'Both columns must be categorical for now')
        col1_vals = [v.value for v in col1_def.values]
        col2_vals = [v.value for v in col2_def.values]
        targets = {col1: [], col2: []}  # type: Dict[str, List[str]]
        for c1v, c2v in itertools.product(col1_vals, col2_vals):
            targets[col1].append(c1v)
            targets[col2].append(c2v)

        jpt = self._popmod.joint_probability(targets=targets)
        jpt = jpt.set_index([col1, col2])
        ps = jpt['p']
        assert 0.999 < np.sum(ps) < 1.001
        shape = (len(col1_vals), len(col2_vals))
        ct = DataFrame(ps.values.reshape(shape),
                       columns=col2_vals, index=col1_vals)
        return ct

    def _product_of_marginal_probabilities_table(self, probability_table):
        # type: (DataFrame) -> DataFrame
        """Returns a table of joint likelihoods assuming independence.

        Returns a table where each cell represents the probability of the
        respective columns taking on the values in that cell, assuming
        independence. The probabilities for each column are the marginal
        likelihoods for each column, so the table is the cartesian product
        of the marginals.

        This is one half of the terms in an unnormalized chi^2 table if that
        makes it clearer, where the other half is `_joint_probability_table`.
        """
        pt = probability_table
        col1_vals = pt.index
        col2_vals = pt.columns
        # This is essentially
        # marg_pt = (scipy.stats.chi2_contingency(np.reshape(ps, shape)))[3]
        # but without the scipy dep.
        c1_margs = {v: sum(pt.ix[v]) for v in col1_vals}
        c2_margs = {v: sum(pt[v]) for v in col2_vals}
        marginals = []
        for c1v, c2v in itertools.product(col1_vals, col2_vals):
            marginals.append(c1_margs[c1v] * c2_margs[c2v])
        marg_pt = pd.DataFrame(np.reshape(marginals, pt.shape),
                               columns=col2_vals, index=col1_vals)
        return marg_pt
