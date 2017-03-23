def parse_observation(dict):
    observation = ObservationObject()

    if 'count' in dict:
        observation.set_count(dict['count'])

    if 'dateObserved' in dict:
        observation.set_date_observed(dict['dateObserved'])

    return observation


class ObservationObject(object):
    __slots__ = (
        '_count',
        '_date_observed'
    )

    def __init__(self):
        self._count = None
        self._date_observed = None

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    #
    # count
    #
    @property
    def count(self):
        """ """
        return self._count

    def set_count(self, data):
        """ Read-Only """
        self._count = self._uni(data)

    #
    # date observed
    #
    @property
    def date_observed(self):
        """ """
        return self._date_observed

    def set_date_observed(self, data):
        """ Read-Only """
        self._date_observed = self._uni(data)