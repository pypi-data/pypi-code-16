from pandas import DataFrame  # type: ignore
from six.moves import urllib
from six.moves.urllib.parse import quote
from typing import Any, Dict, List, Union  # NOQA

# This is imported from `future` so its type checking is wonky
import html  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import six

from .edpclient import (
    EdpClient, ColumnAssociation, Visibility, CallableEndpoint)
from .edpclient import _artifact_id_from_response
from .population_schema import PopulationSchema  # NOQA
from .session_experimental import PopulationModelExperimental
from .guess import guess_schema

DEFAULT_LIMIT = 10


class Session(object):

    def __init__(self,
                 client=None,   # type: EdpClient
                 endpoint=None  # type: CallableEndpoint
                 ):             # type: (...) -> None
        self._client = client or EdpClient()
        if endpoint is None:
            url = (self._client.config.edp_url + '/rpc')
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        # Try and list so we raise an error if you're not auth'd
        self.list_populations()

    def list(self, keyword=None):
        models = self._endpoint.population_model.get().json()
        models_df = DataFrame({
            'id': [pm['id'] for pm in models],
            'name': [pm['name'] for pm in models],
            'parent_id': [pm.get('parent_id') for pm in models],
            'creation_time': [pd.to_datetime(pm['creation_time'], unit='s')
                              for pm in models],
            'status': [pm['build_progress']['status'] for pm in models],
        }, columns=['id', 'name', 'parent_id', 'creation_time', 'status'])
        return _filtered(models_df, keyword)

    def list_populations(self, keyword=None):
        pops = self._endpoint.population.get().json()
        pops_df = DataFrame({
            'id': [pop['id'] for pop in pops],
            'name': [pop['name'] for pop in pops],
            'creation_time': [pd.to_datetime(pop['creation_time'], unit='s')
                              for pop in pops],
            'num_models': [len(pop['models']) for pop in pops]
        }, columns=['id', 'name', 'creation_time', 'num_models'])
        return _filtered(pops_df, keyword)

    def population(self, pid):  # type: (str) -> Population
        """Returns the Population corresponding to `pid`."""
        return Population(pid, self._client)

    def popmod(self, pmid):  # type: (str) -> PopulationModel
        """Returns the PopulationModel corresponding to `pmid`."""
        return PopulationModel(pmid, self._client)

    def upload(self,
               data,            # type: DataFrame
               name,            # type: str
               schema=None,     # type: PopulationSchema
               autobuild=True,  # type: bool
               ):               # type: (...) -> Population
        """Create a population in EDP from uploaded data.

        Args:
            data: The data to create a population from.
            name: The name of the newly created population.
            schema: The schema describing the data. If not provided this will
                attempt to guess one for you.
            autobuild: If true, a number of model builds will be started
                automatically after creating the population
        """
        schema = schema or guess_schema(data)
        # TODO(asilvers): We require you to upload strings for categoricals so
        # that there's no ambiguity as to the representation as there could be
        # if they were floats. But this auto-conversion doesn't really solve
        # that issue, it just hides it from you. These issues go away when we
        # upload raw data and do assembly server-side, since presumably at that
        # point you're uploading strings anyway (e.g. CSV from a file).
        # TODO(asilvers): Also consider not doing this for numeric columns.
        stringed_df = data.copy()
        for col in data.columns:
            stringed_df[col] = stringed_df[col].astype(six.text_type)
        nulled_df = stringed_df.where(pd.notnull(data), None)
        json_data = nulled_df.to_dict(orient='list')
        pid = self._client.upload_population(
            data=json_data, schema=schema, name=name)
        pop = Population(pid=pid, client=self._client)
        if autobuild:
            pm_name = '[Auto-built on upload from %s]' % (name,)
            pop.build_model(name=pm_name, max_seconds=60)
            pop.build_model(name=pm_name, max_seconds=300)
        return pop


def _filtered(items, keyword):
    """Filter a data frame of population / population models."""
    if not keyword:
        return items

    idx = []
    for r in range(items.shape[0]):
        if (items.name[r].lower().find(keyword.lower()) != -1):
            idx.append(r)
    return items.loc[idx]


class Population(object):

    def __init__(self,
                 pid,           # type: str
                 client,        # type: EdpClient
                 endpoint=None  # type: CallableEndpoint
                 ):             # type: (...) -> None
        self._pid = pid
        self._client = client
        if endpoint is None:
            url = (self._client.config.edp_url +
                   '/rpc/population/%s' % quote(self._pid))
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        self.name  # Cause an error if this population doesn't exist

    def __str__(self):
        return ('Population(id=%r, name=%r)' %
                (self._pid, self.name))

    def _repr_html_(self):
        return (('<span>%s</span><br>' %
                (html.escape(self.name),)) +
                '<span>Models:</span>'
                '<ul>' +
                ''.join([('<li>' + m._repr_html_() + '</li>')
                         for m in self.models]) +
                '</ul>')

    def rename(self, name):  # type: (str) -> None
        """Rename this population."""
        self._endpoint.rename.post(json=name)

    def add_user_metadata(self, key, value):  # type(str, str) -> None
        """Add a single key-value pair of metadata to this population."""
        self._endpoint.add_metadata.post(json={key: value})

    def _metadata(self):  # type: () -> Dict[str, Any]
        # TODO(asilvers): Half of this metadata (e.g. creation_time) doesn't
        # ever change, so making a call for each access is unnecessary and
        # wasteful. But if it's causing problems we probably have bigger
        # problems. Think about this at some point.
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pid

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def models(self):  # type: () -> List[PopulationModel]
        return [PopulationModel(model['id'], self._client)
                for model in self._metadata()['models']]

    @property
    def latest(self):  # type: () -> PopulationModel
        """Returns this population's most recently built model.

        Raises `ValueError` if this population has no built models.
        """
        # TODO(asilvers): This is actually looking at models' creation times,
        # not how recently they finished building. That's probably not quite
        # right.
        models = self._metadata()['models']
        if len(models) == 0:
            raise ValueError('This population has no models')
        built = [m for m in models if m['build_progress']['status'] == 'built']
        if len(built) == 0:
            raise ValueError('This population has no built models')
        latest = max(built, key=lambda m: m['creation_time'])
        return PopulationModel(latest['id'], self._client)

    def build_model(self,
                    name=None,           # type: str
                    num_models=16,       # type: int
                    iterations=100,      # type: int
                    max_seconds=None,    # type: int
                    builder='crosscat',  # type: str
                    seed=None            # type: int
                    ):                   # type: (...) -> PopulationModel
        """Build a model from this population.

        Args:
            name: The name of the newly built model
            num_models: The number of models to build
            iterations: The number of iterations to build for
            max_seconds: If set, the model build will attempt to take no longer
                than this many seconds to build. This is not a hard limit.
            builder: Which builder to use. Currently only 'crosscat'
            seed: Specify a random seed to allow for deterministic model
                builds.
        """
        name = name or self.name
        req = {'name': name,
               'build_def': {'num_models': num_models,
                             'builder': builder,
                             'duration': {'iterations': iterations}
                             }
               }  # type: Dict[str, Any]
        if seed is not None:
            req['build_def']['random_seed'] = seed
        if max_seconds is not None:
            req['build_def']['duration']['max_seconds'] = max_seconds
        resp = self._endpoint.build.post(json=req)
        pmid = _artifact_id_from_response(resp)
        return PopulationModel(pmid, self._client)


class PopulationModel(object):

    def __init__(self,
                 pmid,          # type: str
                 client,        # type: EdpClient
                 endpoint=None  # type: CallableEndpoint
                 ):             # type: (...) -> None
        self._pmid = pmid
        self._client = client
        if endpoint is None:
            url = (self._client.config.edp_url +
                   '/rpc/population_model/%s' % quote(self._pmid))
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint

        self.name  # Cause an error if this population model doesn't exist
        self._schema = None  # type: PopulationSchema

        self._return_identifying_columns = True

        self.experimental = PopulationModelExperimental(self)
        """Access to experimental methods on this PopulationModel."""

    @property
    def schema(self):  # type: () -> PopulationSchema
        if self._schema is None:
            resp = self._endpoint.schema.get()
            self._schema = PopulationSchema.from_json(resp.json())

        return self._schema

    def _metadata(self):  # type: () -> Dict[str, Any]
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pmid

    @property
    def parent_id(self):  # type: () -> str
        return self._metadata()['parent_id']

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def build_progress(self):  # type: () -> Dict[str, Any]
        return self._metadata()['build_progress']

    def add_user_metadata(self, key, value):  # type: (str, str) -> None
        """Add a single key-value pair of metadata to this population model."""
        self._endpoint.add_metadata.post(json={key: value})

    def visibility(self):  # type: () -> Visibility
        """Fetches visibility for this population model."""
        resp = self._endpoint.visibility.get()
        respjson = resp.json()
        return Visibility(
            respjson['owner'], respjson['public'], respjson['readers'])

    def make_public(self):  # type: () -> Visibility
        """Make this population model public.

        Returns the ACL for the model after the modification.
        """
        req = {'public': True}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader(self, reader):  # type: (str) -> Visibility
        """Add `reader` to this population model's reader list.

        Args:
            reader: The email of the user who should be able to read the model.

        Returns the ACL for this model after the modification.
        """
        req = {'readers': [reader]}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def _modeled_columns(self):
        return [cname for cname in self.schema.columns()
                if self.schema[cname].stat_type != 'void']

    def __str__(self):
        return ('PopulationModel(id=%r, name=%r, %d columns)' %
                (self._pmid, self.name,
                 len(self.schema.columns())))

    def _repr_html_(self):
        url = '%s/explorer/population_model/%s' % (
            self._client.config.edp_url,
            urllib.parse.quote(self._pmid))
        text = html.escape(self.name)
        # TODO(asilvers): This isn't ideal, because unbuilt models will just
        # 400 when you open explorer.
        if self.build_progress['status'] != 'built':
            text += ' (unbuilt)'
        return ('<a href="%s" target="_blank">Explore %s</a>' % (
            html.escape(url), text))

    def columns(self):
        return DataFrame([(self.schema[c].name, self.schema[c].stat_type,
                           _abbreviate_values(self.schema[c].values))
                          for c in self.schema.columns()],
                         columns=['name', 'stat_type', 'values'])

    def _columns_from_arg(self, columns):
        """Given a columns argument, return a list of column names. Handles
        None and non-list sequences."""
        self._check_column_list(columns)
        if not columns:
            columns = self._modeled_columns()
        return list(columns)

    def _check_column_list(self, columns):
        """Make sure someone didn't accidentally pass a string as a list."""
        if isinstance(columns, six.string_types):
            raise ValueError('`columns` takes a sequence, not a single string')
        return columns

    def _rowids_from_arg(self, rowids):  # type: (List[int]) -> List[int]
        """Return `rowids` if non-None or all the rowids if None."""
        effective_rowids = (
            rowids if rowids is not None else self.select(targets=[]).index)
        return _ensure_rowids_are_real_ints(effective_rowids)

    def _id_cols(self):
        """Returns identifying columns if we have them and we want to be using
        them, or an empty list otherwise.
        """
        if self._return_identifying_columns:
            return self.schema.identifying_columns or []
        else:
            return []

    def return_identifying_columns(self, return_them=True):
        # type: (bool) -> None
        """Set whether methods add identifying_columns to data frames."""
        self._return_identifying_columns = return_them

    def select(self,
               targets=None,  # type: List[str]
               where=None,    # type: Dict[str, Union[str, int, float]]
               rowids=None,   # type: List[int]
               limit=None,    # type: int
               ):             # type: (...) -> DataFrame
        """Return a subset of a population's data.

        The response DataFrame's index corresponds to the population's rowids.

        Args:
            targets: The list of columns to select. If not specified, returns
                all columns.
            where: Limit the results to those rows where the values of the
                specified columns match the values in `where`. If not
                specified, `select` returns all rows.
            rowids: The rowids to restrict results to. If not specified
                returns all rows.
            limit: Return at most `limit` rows. If this would otherwise return
                more than that, the rows to return are chosen randomly.
        """
        targets = self._columns_from_arg(targets)
        req = {'target': targets}  # type: Dict[str, Any]
        if rowids is not None:
            req['rowids'] = _ensure_rowids_are_real_ints(rowids)
        if where:
            req['where'] = where
        if limit is not None:
            req['limit'] = int(limit)
        resp = self._endpoint.select.post(json=req)
        respjson = resp.json()
        return DataFrame(respjson['columns'], index=respjson['rowids'])

    def simulate(
            self,
            targets=None,           # type: List[str]
            rowid=None,             # type: int
            given=None,             # type: Dict[str, Union[str, int, float]]
            n=DEFAULT_LIMIT         # type: int
            ):                      # type: (...) -> DataFrame
        """Draw a sample of size `n` from the population model.

        Each returned row is a random draw from the posterior predictive. To
        the extent that there is model uncertainty, drawn rows come from
        independent draws from the model's posterior.

        Args:
            targets: The list of columns to simulate.
            rowid: If present, the simulation will be conditioned on all values
                present in that row except for columns specified in `targets`.
                Givens specified in `given` will also take precedence.
            given: Values to condition the simulation on. If a column is in
                both `target` and a key in `given` that column will be the
                given value in every resulting row.
            n: The number of results to simulate.
        """
        targets = self._columns_from_arg(targets)
        given = given or {}
        effective_givens = {}
        # TODO(asilvers): I am uncomfortable with this magic
        if rowid:
            df = self.select(rowids=[rowid])
            # Each column is only length 1 since we only requested a single row
            # If you specified a rowid and that row has values for the target
            # columns, you probably don't mean to condition on those targets
            # and get boring deterministic results back. So we do the right
            # thing and drop them from the givens. This kind of magic is
            # coincidentally why I'm wary of handling rowids server-side.
            givens_from_row = {col: df[col][rowid] for col in df
                               if pd.notnull(df[col][rowid]) and
                               col not in targets}
            effective_givens.update(givens_from_row)
        # Have existing givens take precedence
        effective_givens.update(given)

        req = {'target': targets,
               'n': n}
        if effective_givens:
            req['given'] = effective_givens
        resp = self._endpoint.simulate_row.post(json=req)
        respjson = resp.json()
        assert 'rowids' not in respjson
        return DataFrame(respjson['columns'])

    def mutual_information(self,
                           columns=None,        # type: List[str]
                           given_columns=None,  # type: List[str]
                           given_values=None    # type: Dict[str, Any]
                           ):
        # type: (...) -> DataFrame
        """Returns the mutual information between a collection of columns.

        See `column_association` for documentation about column association
        calls in general.
        """
        return self.column_association(columns, 'mutual information',
                                       given_columns=given_columns,
                                       given_values=given_values)

    def column_relevance(self,
                         columns=None,        # type: List[str]
                         given_values=None,   # type: Dict[str, Any]
                         distribution=0.1,    # type: float
                         given_columns=None   # type: List[str]
                         ):
        # type: (...) -> DataFrame
        """Return the MI-based dep prob of a collection of columns.

        See `column_association` for documentation about column association
        calls in general.

        This MI-based dep prob is the probability that the MI is greater than
        `distribution`.
        """
        mi_cdf = self.column_association(
            columns, 'mutual information', given_columns=given_columns,
            given_values=given_values, distribution=distribution)
        # This returns a CDF-like probability of MI being less than
        # `distribution`. But we want the probability that it's greater, so
        # reverse it.
        mi_cdf = 1 - mi_cdf
        return mi_cdf

    def classic_dep_prob(self,
                         columns=None  # type: List[str]
                         ):            # type: (...) -> DataFrame
        """Returns the "classic dep prob" of a collection of columns.

        See `column_association` for documentation about column association
        calls in general.
        """
        # Conditional classic dep prob doesn't make sense.
        return self.column_association(columns, statistic='classic dep prob')

    def correlation_squared(self,
                            columns=None,      # type: List[str]
                            given_values=None  # type: Dict[str, Any]
                            ):                 # type: (...) -> DataFrame
        """Return a DataFrame containing R-squared.

        See `column_association` for documentation about column association
        calls in general.
        """
        return self.column_association(columns, 'R squared',
                                       given_values=given_values)

    def column_association(self,
                           columns,             # type: List[str]
                           statistic,           # type: str
                           given_columns=None,  # type: List[str]
                           given_values=None,   # type: Dict[str, Any]
                           distribution=None    # type: float
                           ):
        # type: (...) -> pd.Series
        """Return a measure of the column association for a list of columns.

        Returns a Series of the column association between all columns or
        the provided `columns`. The series has a multi-index of (X, Y) which
        are the column names for that row, and the value of the series at that
        index is the value of the chosen column association measure between
        those columns.

        Args:
            columns: The columns to find the column association of. If None,
                return all non-given columns.
            statistic: Which column association statistic to use.
            given_columns: The columns to condition on. That is, compute
                `col_assoc(X, Y | G_1, G_2, ..., G_n)` where
                `given_columns = {G_1, G_2, ..., G_n}`.
            given_values: The column values to condition on. That is, compute
                `col_assoc(X, Y | G_1 = g_1, G_2 = g_2, ..., G_n = g_n)` where
                `given_values = {G_1: g_1, G_2: g_2, ..., G_n: g_n}`.
            distribution: If None, the returned values will be the mean of the
                column association across models. If not None, the return
                values will be the probability that the column association is
                less than `distribution`.
        """
        cols_used_in_givens = (
            set(given_columns or []) | set(given_values or []))
        # Use `columns` if provided, otherwise use all non-given columns
        if columns is not None:
            columns = self._columns_from_arg(columns)
        else:
            columns = [c for c in self._modeled_columns()
                       if c not in cols_used_in_givens]

        overlapping_cols = set(columns).intersection(
            given_columns or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `columns` and `given_columns`' %
                (overlapping_cols,))
        overlapping_cols = set(columns).intersection(
            given_values or [])
        if overlapping_cols:
            raise ValueError(
                '%s in both `columns` and `given_values`' %
                (overlapping_cols,))

        req = {
            'statistic': statistic,
            'target': columns
        }  # type: Dict[str, Any]

        if given_columns:
            req['given_columns'] = given_columns
        if given_values:
            req['given'] = given_values
        if distribution is not None:
            req['distribution'] = distribution
        resp = self._endpoint.column_association.post(json=req)
        return ColumnAssociation(resp.json()).as_series()

    def relevant_columns(self, target_column, num_cols=10,
                         statistic='classic dep prob'):
        """Return the `num_cols` columns with the highest column association
        (based on the chosen statistic) relative to `target_column`.
        """
        cols = self._modeled_columns()
        ca = self.column_association(cols, statistic=statistic)
        col_dependence = [(c, ca.ix[target_column, c]) for c in cols]
        col_dependence.sort(key=lambda v: -v[1])  # descending by dependence
        return DataFrame(col_dependence[0:num_cols],
                         columns=['column', 'depprob'])

    def joint_probability(
            self,
            targets,                # type: Dict[str, Any]
            given=None,             # type: Dict[str, Any]
            probability_column='p'  # type: str
            ):                      # type: (...) -> DataFrame
        """The joint probability of a list of hypothetical rows.

        TODO(asilvers): Somehow emphasize that this is the joint probability of
        each row individually, vectorized, not the probability of all of them
        occurring together.

        Returns a data frame with a column for each key in `targets` containing
        the target values, plus a column, `probability_column`.
        `probability_column`s value represents the joint probability of the
        values in that row, conditioned on `givens.
        """
        req = {'targets': targets}
        if given:
            req['given'] = given
        resp = self._endpoint.logpdf_rows.post(json=req)
        lps = [lp if lp is not None else float('nan') for lp in resp.json()]
        resp_vals = targets.copy()
        resp_vals[probability_column] = np.exp(lps)
        return DataFrame(resp_vals)

    def _internal_likelihood(self,
                             targets,        # type: List[str]
                             given_columns,  # type: List[str]
                             rowids          # type: List[int]
                             ):              # (...) -> type: List[float]
        req = {'targets': targets,
               'givens': given_columns,
               'rowids': _ensure_rowids_are_real_ints(rowids)}
        resp = self._endpoint.logpdf_observed.post(json=req)
        lps = [lp if lp is not None else float('nan') for lp in resp.json()]
        return np.exp(lps)

    def joint_likelihood(self,
                         targets=None,           # type: List[str]
                         given_columns=None,     # type: List[str]
                         rowids=None,            # type: List[int]
                         select=None,            # type: List[str]
                         probability_column='p'  # type: str
                         ):                      # type: (...) -> DataFrame
        """The joint likelihood of a list of observed rows.

        TODO(asilvers): Somehow emphasize that this is the joint likelihood of
        each row individually, vectorized, not the probability of all of them
        occurring together.

        Returns a data frame containing the data in columns and rowids and
        a single additional column, `probability_column`, containing the joint
        likelihood of the values in that row, conditional on the values in the
        in the given columns. The given columns are `given_columns` if
        provided, or all modeled columns not in `targets` otherwise. It is an
        error to pass a column in both `targets` and `given_columns`.

        If you want one likelihood column per column, you want `likelihood`.

        Args:
            targets: The list of columns to find the likelihood of.
            given_columns: The list of columns to condition the likelihood on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_column: The name of the column in which to return the
                likelihoods.
        """
        targets = self._columns_from_arg(targets)
        if probability_column in targets:
            raise ValueError(
                "Probability column, %r, is already a column in targets." %
                (probability_column,))
        # Use the given columns if provided, otherwise use all non-target
        # columns
        given_cols = (self._columns_from_arg(given_columns)
                      if given_columns is not None else
                      [c for c in self._modeled_columns() if c not in targets])
        overlapping_cols = set(targets).intersection(given_cols)
        if overlapping_cols:
            raise ValueError('%s in both `targets` and `given_columns`' %
                             (overlapping_cols,))
        if isinstance(rowids, six.string_types):
            raise ValueError('`rowids` takes a sequence, not a single string')
        select_df = self.select(targets=targets, rowids=rowids)
        # Pull the rowids back out of the select results in case they were None
        rowids = select_df.index.tolist()
        p = self._internal_likelihood(targets, given_cols, rowids)

        probs_df = DataFrame({probability_column: p}, index=select_df.index)
        column_order = targets + [probability_column]
        res = pd.concat([probs_df, select_df], axis=1)[column_order]
        return self.add_data_columns(res, select)

    def likelihood(self,
                   targets=None,            # type: List[str]
                   given_columns=None,      # type: List[str]
                   rowids=None,             # type: List[int]
                   select=None,             # type: List[str]
                   probability_suffix='_p'  # type: str
                   ):                       # type: (...) -> DataFrame
        """The likelihood of the individual values in a list of observed rows.

        Returns a data frame containing marginal likelihoods for the values
        in the requested columns and rowids, conditional on the values in the
        given columns. The given columns are `given_columns` if provided, or
        all modeled columns not in `targets` otherwise, minus the single target
        column. It is _not_ an error to pass a column in both `targets` and
        `given_columns`.

        The data frame will have 2*len(columns) columns, one for each column,
        and one for each column's values' probabilities.  These are the
        marginal conditional likelihoods of each cell's value, not a joint
        conditional likelihood across all columns for a given row.

        If you want a single likelihood per row, you want `joint_likelihood`.

        Args:
            targets: The list of columns to find the likelihood of.
            given_columns: The list of columns to condition the likelihood on.
                Defaults to all non-target columns.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            probability_suffix: The string to append to each column name to
                generate its corresponding likelihood column's name.
        """
        targets = self._columns_from_arg(targets)
        given_columns = self._columns_from_arg(given_columns)
        if isinstance(rowids, six.string_types):
            raise ValueError('`rowids` takes a sequence, not a single string')
        for col in targets:
            if (col + probability_suffix) in targets:
                raise ValueError(
                    "Column %r's probability column would clash with %r" %
                    (col, col + probability_suffix))
        df = self.select(targets=targets, rowids=rowids)
        # Pull the rowids back out of the select results in case they were None
        rowids = df.index.tolist()

        for col in targets:
            given_cols = sorted([c for c in given_columns if c != col])
            p = self._internal_likelihood(
                targets=[col], given_columns=given_cols, rowids=rowids)
            df[col + probability_suffix] = p

        # Re-order the columns so the confidence columns are next to the data.
        column_order = []  # type: List[str]
        for c in targets:
            column_order.extend((c, c + probability_suffix))
        res = df[column_order]
        return self.add_data_columns(res, select)

    # TODO(asilvers): I don't think this really belongs on PopulationModel.
    # Maybe we return a DataFrame extended with this method?
    def add_data_columns(
            self,
            df,                              # type: DataFrame
            columns=None,                    # type: List[str]
            return_identifying_columns=None  # type: bool
            ):                               # type: (...) -> DataFrame
        """Return a DataFrame with additional columns from the population.

        Args:
            df: The data frame to add columns to.
            columns: The columns to fetch.
            return_identifying_columns: An optional override to the
                return_identifying_columns optional on this instance.
        """
        self._check_column_list(columns)
        return_id_cols = (return_identifying_columns
                          if return_identifying_columns is not None
                          else self._return_identifying_columns)
        id_cols = self.schema.identifying_columns if return_id_cols else []
        cols_to_fetch = id_cols + (columns or [])
        # It's reasonable to call this and not have any columns to fetch.
        if not cols_to_fetch:
            return df

        # Filter out columns we already have
        cols_to_fetch = [col for col in cols_to_fetch
                         if col not in df.columns]
        rowids = df.index.tolist()
        select_results = self.select(targets=cols_to_fetch, rowids=rowids)
        # Put our columns first, except don't re-order id columns that we
        # didn't re-fetch.
        column_order = cols_to_fetch + list(df.columns)
        return df.join(select_results)[column_order]

    def infer(self,
              targets=None,              # type: List[str]
              rowids=None,               # type: List[int]
              select=None,               # type: List[str]
              infer_present=False,       # type: bool
              confidence_suffix='_conf'  # type: str
              ):                         # type: (...) -> DataFrame
        """Infer values from this population model.

        Infer values for the columns in `targets` for `rowids`, given the other
        values in that row. If `infer_present` is False, this will only infer
        values for cells which are missing in the data. If `infer_present` is
        True, this will act as though each column in `targets` is missing
        across all rows and so infer a value for every row.

        Args:
            targets: The list of columns to infer.
            rowids: The rowids to restrict results to.  If not specified
                returns all rows.
            select: A list of additional columns to select and return in the
                data frame.
            infer_present: True to infer results for values which are present
                in the underlying data. False will cause them to be returned as
                NA.
            confidence_suffix: The string to append to each column name to
                generate its corresponding confidence column's name.

        Returns:
            A data frame containing 2*len(targets) columns, one for each column
            and one for each column's confidence. If a cell is present in the
            data and `infer_present` is false, both the cell and its
            corresponding confidence cell will contain NA.
        """
        targets = self._columns_from_arg(targets)
        rowids = self._rowids_from_arg(rowids)

        for col in targets:
            if (col + confidence_suffix) in targets:
                raise ValueError(
                    "Column %r's confidence column would clash with %r" %
                    (col, col + confidence_suffix))

        req = {'target': targets,
               'rowids': rowids,
               'infer_present': infer_present}
        resp = self._endpoint.infer.post(json=req)
        respjson = resp.json()

        df = DataFrame(respjson['columns'], index=respjson['rowids'])
        for colname, uncertainty in respjson['uncertainty'].items():
            df[colname + confidence_suffix] = uncertainty

        # Re-order the columns so the confidence columns is next to the data
        column_order = []  # type: List[str]
        for c in targets:
            column_order.extend((c, c + confidence_suffix))
        res = df[column_order]
        return self.add_data_columns(res, select)


def _ensure_rowids_are_real_ints(rowids):
    # numpy int64s aren't JSON serializable, even though they look like
    # ints in pretty much every other way. Convert them. Yes, this also
    # casts strings, but if they successfully cast, so be it.
    return [int(r) for r in rowids]


def _abbreviate_values(values, max_len=40):
    if values is None:
        return None
    values_str = ''
    for i, d in enumerate(values):
        v = d.value
        vv = v if i == 0 else ', ' + v
        if len(values_str + vv) < (max_len - 7):
            values_str += vv
        elif i == 0:
            return '{...}'
        else:
            return '{%s, ...}' % (values_str,)
    return '{%s}' % (values_str,)
