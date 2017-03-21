from typing import Any, Dict, List, Tuple  # NOQA
import pprint

from collections import OrderedDict


# TODO(asilvers): I don't like re-defining these here.
STAT_TYPES = ['categorical', 'realAdditive', 'realMultiplicative',
              'proportion', 'void']


class ValueDefinition(object):
    def __init__(self, value, display_value=None):  # type: (str, str) -> None
        self.value = value
        self.display_value = display_value

    def __repr__(self):
        return pprint.pformat(self.to_json())

    def to_json(self):
        if self.display_value:
            return {'value': self.value, 'display_value': self.display_value}
        else:
            return {'value': self.value}


class ColumnDefinition(object):
    def __init__(
            self,
            name,                   # type: str
            stat_type,              # type: str
            stat_type_reason=None,  # type: str
            values=None,            # type: List[str]
            description=None,       # type: str
            display_name=None,      # type: str
            display_values=None     # type: Dict[str, str]
            ):                      # type: (...) -> None
        self.name = name
        self.description = description
        self.display_name = display_name
        self.set_stat_type(
            stat_type, stat_type_reason, values, display_values)

    @property
    def stat_type(self):
        return self._stat_type

    @property
    def values(self):
        if self._values is None:
            return None
        else:
            return list(self._values.values())

    def set_display_values(self,
                           display_values):  # type: (Dict[str, str]) -> None
        for v, dv in display_values.items():
            self._values[v].display_value = dv

    def set_stat_type(self, stat_type, stat_type_reason=None,
                      values=None, display_values=None):
        if stat_type not in STAT_TYPES:
            raise ValueError('%r is not a valid stat type' % (stat_type,))
        # TODO(asilvers): We could maybe be nice and, if your values are the
        # same, keep the display_values around.
        self._stat_type = stat_type
        self._stat_type_reason = stat_type_reason
        display_values = display_values or {}
        if stat_type == 'categorical':
            if values is None:
                raise ValueError(
                    '`values` must be provided for categorical columns')
            self._values = OrderedDict([
                (val, ValueDefinition(val, display_values.get(val)))
                for val in values])
        else:
            # Clear the values if we're not categorical
            self._values = None

    def __repr__(self):
        return pprint.pformat(self.to_json())

    def to_json(self, drop_reasons=False):
        col_def = {}
        col_def['name'] = self.name
        if self.display_name:
            col_def['display_name'] = self.display_name
        if self.description:
            col_def['description'] = self.description
        col_def['stat_type'] = self._stat_type
        if not drop_reasons and self._stat_type_reason:
            col_def['stat_type_reason'] = self._stat_type_reason
        if self._values:
            col_def['values'] = [val.to_json()
                                 for val in self._values.values()]
        return col_def


# TODO(asilvers): This thing needs better testing. It's currently only tested
# indirectly in session_test.py.
class PopulationSchema(object):
    """Represents a schema for a population.

    The set of columns is immutable. The API is super rough and subject to
    change.
    """

    def __init__(
            self,
            columns,     # type: Dict[str, ColumnDefinition]
            order=None   # type: List[str]
            ):           # type: (...) -> None
        """Create a schema from a dict of ColumnDefinitions.

        The order may be specified by passing `order`, which must contain
        exactly the keys in `columns`. If unspecified, the order of the columns
        is the same as the iteration order in `columns`, so passing an
        OrderedDict does the right thing.
        """
        order = order if order is not None else list(columns)
        self._columns = OrderedDict([(k, columns[k]) for k in order])
        self._identifying_columns = []  # type: List[str]

    def __getitem__(self, key):
        return self._columns[key]

    def __delitem__(self, key):
        del self._columns[key]

    def columns(self):  # type: () -> List[str]
        return list(self._columns.keys())

    @property
    def identifying_columns(self):  # type: () -> List[str]
        # Make a copy so callers can't modify our state.
        return list(self._identifying_columns)

    def set_identifying_columns(self, columns):  # type: (List[str]) -> None
        bad_cols = set(columns).difference(self._columns)
        if bad_cols:
            raise ValueError('%r are not columns' % (bad_cols,))
        self._identifying_columns = columns

    def __repr__(self):
        # pprint returns something a little more compact than json.dumps can
        # be made to produce.
        return pprint.pformat(self.to_json())

    def to_json(self, drop_reasons=False):  # type: (bool) -> Dict[str, Any]
        columns = [col.to_json(drop_reasons) for col in self._columns.values()]
        resp = {'columns': columns}
        if self._identifying_columns:
            resp['identifying_columns'] = self._identifying_columns
        return resp

    @staticmethod
    def from_json(json_schema):
        columns = OrderedDict()  # type: Dict[str, ColumnDefinition]
        for col in json_schema['columns']:
            name = col['name']
            values = None
            display_values = None
            if 'values' in col:
                values = []
                display_values = {}
                for v in col['values']:
                    values.append(v['value'])
                    if 'display_value' in v:
                        display_values[v] = v['display_value']
            col_def = ColumnDefinition(
                name=name,
                stat_type=col['stat_type'],
                stat_type_reason=col.get('stat_type_reason'),
                values=values,
                description=col.get('description'),
                display_name=col.get('display_name'),
                display_values=display_values
            )
            columns[name] = col_def
        schema = PopulationSchema(columns)
        if 'identifying_columns' in json_schema:
            schema.set_identifying_columns(json_schema['identifying_columns'])
        return schema
