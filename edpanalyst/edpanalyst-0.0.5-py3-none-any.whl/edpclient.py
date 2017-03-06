from collections import OrderedDict
from typing import Any, Dict, List, NamedTuple, Optional  # NOQA
import os
import re

from configparser import RawConfigParser  # type: ignore
from pandas import DataFrame  # type: ignore
from pandas import Series  # NOQA
from six.moves.urllib.parse import quote, unquote
import requests

from .population_schema import PopulationSchema  # NOQA

ID_REGEX = '^[a-z]+-[a-z0-9]{16}$'  # matches pids and pmids


VisibilityTuple = NamedTuple(
    'Visibility', [('owner', str), ('public', bool), ('readers', List[str])])
"""The visibility of a population or population model"""


class Visibility(VisibilityTuple):
    @staticmethod
    def from_json(json):  # type: (Dict[str, Any]) -> Visibility
        return Visibility(json['owner'], json['public'], json['readers'])


_Config = NamedTuple(
    '_Config', [('edp_url', str), ('username', str), ('bearer_token', str)])
"""Authentication configuration from ~/.edp_auth or EdpClient.__init__"""


class EdpClient(object):

    """Provides a python API to the Empirical Data Platform."""
    def __init__(self,
                 profile_name=None,  # type: str
                 edp_url=None,       # type: str
                 bearer_token=None   # type: str
                 ):                  # type: (...) -> None
        """Create an EDP client.

        This class is thread-safe if requests.Session is thread-safe. It very
        much seems that it should be, but the requests developers are hesitant
        to declare it so. See
        https://github.com/kennethreitz/requests/issues/1871
        https://github.com/kennethreitz/requests/issues/2766 and
        http://stackoverflow.com/questions/18188044/is-the-session-object-from-pythons-requests-library-thread-safe
        Nevertheless, we're treating it as thread-safe until we discover
        otherwise.

        Args:
            profile_name: The name of a profile to use. If not provided then
                the "default" profile is used.
            bearer_token: The JWT to be used for authentication soon.
            edp_url: An endpoint to connect to.
        """
        self.config = self._config(profile_name=profile_name, edp_url=edp_url,
                                   bearer_token=bearer_token)
        self._session = requests.Session()
        if self.config.bearer_token:
            self._session.headers.update(
                {'Authorization': 'Bearer ' + self.config.bearer_token})

    @staticmethod
    def _config(profile_name=None, edp_url=None, bearer_token=None):
        # type: (str, str, str) -> _Config
        """Returns a `_Config`, looking up fields in a variety of places.

        Usually, values will come from the "default" profile in ~/.edp_auth,
        which can be overridden by either `profile_name` or, if that is unset,
        `EDP_PROFILE` in the environment.

        You can override individual `_Config` fields by passing arguments to
        this constructor, which passes them to this function.
        """
        profile_name = profile_name or os.environ.get('EDP_PROFILE', 'default')
        config = EdpClient._read_edp_auth(profile_name)
        username = config.get('username', None)
        edp_url = (edp_url or
                   config.get('edp_url') or
                   'https://betaplatform.empirical.com')
        bearer_token = bearer_token or config.get('bearer_token')
        if not bearer_token:
            raise ValueError(
                'No bearer_token found in %r section of ~/.edp_auth, nor '
                'was it passed to EdpClient constructor.' % (profile_name,))
        return _Config(edp_url=edp_url, username=username,
                       bearer_token=bearer_token)

    @staticmethod
    def _read_edp_auth(profile_name):
        # type: (str) -> Dict[str, Any]
        """Returns the named section of ~/.edp_auth or {} if not found."""
        config_path = os.path.expanduser('~/.edp_auth')
        if not os.path.isfile(config_path):
            return {}
        config = RawConfigParser()
        config.read(config_path)
        if profile_name not in config.sections():
            return {}
        return dict(config.items(profile_name))

    def get_username(self):  # type: () -> str
        """Get the authenticated user's email address."""
        resp = self._session.get(self.config.edp_url + '/auth/username')
        _raise_for_error(resp)
        return resp.text

    def upload_population(
            self,
            data,           # type: Dict[str, List[Optional[str]]]
            schema,         # type: PopulationSchema
            name,           # type: str
            this_is_a_lot_of_data_but_i_know_what_im_doing=False  # type: bool
            ):              # type: (...) -> str
        """Upload a population to EDP.

        Returns:
            str: The ID of the newly uploaded population.

        Args:
            data: The data to be uploaded.
            schema: A schema describing the uploaded data.
            name: Name of the newly created population.
        """
        url = self.config.edp_url + '/rpc/population'
        if len(data) == 0:
            raise ValueError('`data` must not be empty')
        if name is None:
            raise ValueError('`name` must not be None')
        # Grab an arbitrary row's length. If the row lengths are inconsistent
        # the server will yell at us.
        num_rows = len(list(data.values())[0])
        postdata = {
            'name': name,
            'data': {'num_rows': num_rows, 'columns': data},
            'schema': schema.to_json()
        }  # type: Dict[str, Any]
        if this_is_a_lot_of_data_but_i_know_what_im_doing:
            postdata['this_is_a_lot_of_data_but_i_know_what_im_doing'] = True
        resp = self._session.post(url, json=postdata)
        _raise_for_error(resp)
        return _artifact_id_from_response(resp)

    # TODO(asilvers): This is only hanging around because we use it in tests.
    # Delete it after that.
    def _upload_population_as_generator(self, generator, name):
        # type: (bytes, str) -> str
        """Upload a population (as a generator) to EDP."""
        if not isinstance(generator, bytes):
            raise ValueError('generator must be a bytes')
        url = self.config.edp_url + '/rpc/population/upload_generator'
        # The (None, 'foo') syntax is request.post's way of passing non-file
        # params in a multipart/form-data request.
        formdata = {'name': (None, name), 'file': generator}
        resp = self._session.post(url, files=formdata)
        _raise_for_error(resp)
        return _artifact_id_from_response(resp)


class CallableEndpoint(object):
    """A helper class to make it easy to mock out HTTP calls.

    Call like:
        endpoint = CallableEndpoint('http://test.com/base', session)
        endpoint.logpdf_rows.post(json=request)
    and it will issue:
        session.post('http://test.com/base/logpdf_rows', json=request)

    Unlike just using requests, this will automatically raise on HTTP error
    codes. If for some reason you need that to not happen I'd be ok adding a
    `autoraise` parameter to the methods.
    """
    def __init__(self,
                 url,     # type: str
                 session  # type: requests.Session
                 ):       # type: (...) -> None
        self.url = url
        self._session = session

    def get(self, *args, **kwargs):
        resp = self._session.get(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def post(self, *args, **kwargs):
        resp = self._session.post(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def patch(self, *args, **kwargs):
        resp = self._session.patch(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    # This isn't just an attempt to make a cute API. It'd be less strange to
    # have a `sub_url()` method that did this, but python's mock can't mock
    # based on args, so you couldn't mock `ce.sub_url('select')` and
    # `ce.sub_url('logpdf_rows')` separately. This gets around that by letting
    # you mock `ce.select` and `ce.logpdf_rows`.
    def __getattr__(self, attr):
        new_url = self.url + '/' + quote(attr)
        return CallableEndpoint(new_url, self._session)


def _artifact_id_from_response(resp):  # type: (requests.Response) -> str
    """Figure out the id of the population or model.

    This should be the last part of the path of the URL.
    """
    # This obviously depends on the format of the URL in the response, but so
    # does actually constructing the URLs when making the requests, so it's not
    # horrendous.
    #
    # TODO(asilvers): Really though this is going to break if/when we start
    # appending colon-separated names to the URLs. We should probably just
    # return the ID in another header. I wonder if there's a standard for that.
    location = unquote(resp.headers['location'])
    artifact_id = location.split('/')[-1]
    assert re.match(ID_REGEX, artifact_id)
    return artifact_id


# TODO(asilvers): This isn't actually getting exposed publicly anywhere
# anymore. It's just used as an intermediate representation before being turned
# into a data frame. But I don't love the data frame representation, so it's
# possible someone will want this. Let it hang around for now.
class ColumnAssociation(object):
    """Provides a reasonable interface to a column association response"""
    def __init__(self, json):
        # Map from column name to index
        self._name_index = OrderedDict(
            [(v, k) for k, v in enumerate(json['target'])])
        self._elements = json['elements']

    def between(self,
                colName1,  # type: str
                colName2   # type: str
                ):         # type: (...) -> float
        """Returns the value of the column association."""
        colIndex1 = self._name_index[colName1]
        colIndex2 = self._name_index[colName2]
        j1 = min(colIndex1, colIndex2)
        j2 = max(colIndex1, colIndex2)
        return self._elements[_T(j2) + j1]

    def as_series(self):  # type: (...) -> Series
        """Returns the full column association table as a series.

        The returned series has a multi-index of (X, Y) which are the
        column names for that row, and the values of the series at that
        index is the value of the column association between those
        columns.
        """
        columns = list(self._name_index)
        # Building the data frame then returning a series from it is easier
        # than building the multi-index by hand.
        df = DataFrame([(c1, c2, self.between(c1, c2))
                       for c1 in columns for c2 in columns],
                       columns=['X', 'Y', 'I'])
        df = df.set_index(['X', 'Y'])
        return df['I']


def _T(k):  # type: (int) -> int
    """kth triangular number"""
    return (int)(k * (k + 1) / 2)


def _raise_for_error(response):
    """Raise an error if response indicates an HTTP error code.

    Like requests.raise_for_status(), but additionally tries to raise a
    more sensible error if we can parse out what happened from the response.

    Raises:
        NoSuchGeneratorError: If the response was a 404
        ValueError: If the request was bad due to user error, e.g. bad columns
            or too large a sample size
        HTTPError: If the response is any other 4XX or 5XX error
    """
    # TODO(asilvers): This may turn some other 404s into NoSuchGeneratorErrors
    # if, say, we start building bad URLs and 404ing due to structural issues
    # in the requests. We should work out a signalling this exact case in the
    # body of the 404 to get rid of that ambiguity.
    if response.status_code == 404:
        raise NoSuchGeneratorError
    if response.status_code == 403:
        raise AuthenticationError(
            'You are not authenticated to EDP. Do you have a token from '
            'https://betaplatform.empirical.com/tokens?')
    if response.status_code == 400:
        # Some errors return nice json for us
        try:
            respjson = response.json()
            error = respjson['error']
        except ValueError:
            # But if not, raise a ValueError and hope that there was some
            # useful text in the HTML. It's better than swallowing the response
            # text which is what `raise_for_status` does.
            raise ValueError(response.content)
        if error == 'MODEL_NOT_BUILT':
            raise ModelNotBuiltError()
        if error == 'N_TOO_LARGE':
            raise ValueError('Request\'s \'n\' was too large.')
        if error == 'NO_SUCH_COLUMN':
            raise ValueError('No such column in %s: %s' %
                             (respjson['field'], respjson['columns']))
        # Got JSON but we're not handling its error code. Still better than
        # raising a 400.
        raise ValueError(respjson)
    response.raise_for_status()


class EdpError(Exception):
    pass


class NoSuchGeneratorError(EdpError):
    pass


class ModelNotBuiltError(EdpError):
    pass


class AuthenticationError(EdpError):
    pass
