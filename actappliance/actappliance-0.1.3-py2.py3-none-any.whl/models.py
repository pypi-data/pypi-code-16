import numbers
import logging
import six

from actappliance.act_errors import act_errors, ACTError

"""
This module contains the primary objects that power actappliance.
"""

logger = logging.getLogger('models')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ActResponse(dict):
    """
    Dictionary class that allows parsing and raising errors on public Actifio API responses.
    """

    def __init__(self, *arg, **kwarg):
        # py2 compliance optional argument 'actifio_command'
        self.command = kwarg.pop('actifio_command', None)
        super(ActResponse, self).__init__(*arg, **kwarg)
        self.errorcode = None
        self.errormessage = None

    def raise_for_error(self):
        """Raise ACTError if one occurred"""
        try:
            self.errorcode = self['errorcode']
        except KeyError:
            logger.debug('No errorcode found in ActResponse.')

        try:
            self.errormessage = self['errormessage']
        except KeyError:
            # Handle ui responses
            try:
                self.errormessage = self['msg']
            except KeyError:
                logger.debug('No errormessage found in ActResponse.')

        if self.errorcode or self.errormessage:
            if self.errorcode in act_errors:
                raise act_errors[self.errorcode](self)
            else:
                raise ACTError(self)

    def parse(self, k=None, m_k=None, m_v=None, index=0, warnings=True):
        """
        Takes appliance api response and returns a desired value or dictionary.

        It will first search outside the result for the key. Then it will search inside the result.
        If only a key is given it will return the value of that key from the desired index (default 0).
        If given a match_key and match_value it will search for the first matching dictionary inside the result list
        and return the key from that dictionary.

        Index is ignored without warning if match_key and match_value are provided.

        It is outside the scope of this method to return multiple dictionaries. Parsing multiple systems shouldn't use
        this method.

        "Bad" keyword arguments were chosen for this function as it will be exposed to Robot Framework and may be used
        in conjunction with a cmd. The keys selected for parse have to never be relevant to any command. Polluting the
        namespace of key and value is too risky. Once Key became k and value became v, matching_k and matching_v looked
        out of place so were changed to m_k and m_v respectively.

        Example uses:
        Get information about a host:
        - r = appliance.cmd('udsinfo lshost -filtervalue hostid=<id>')
        - appliance.parse(r.json()) # returns the whole dictionary
        - appliance.parse(r.json(), 'ipaddress') # returns the ipaddress of the host
        :param self: python object response from appliance api (most commonly json decoded from method cmd)
        :param k: the key; corresponding value will be returned
        :param m_k: match key to find the indexes
        :param m_v: match value to find the indexes
        :param index: index of the list of dictionaries to return. If string last, tail or final is passed in it will
        grab the last index
        :param warnings: boolean of whether to raise warning or not
        :return: string if key provided; dictionary if key is not provided
        """
        # find last index if user asked
        if index in ['last', 'final', 'tail']:
            index = len(self['result']) - 1
            logger.debug('The last index is {} and will be grabbed.'.format(index))

        # Is the result empty?
        try:
            if not self['result']:
                value = self._get_external_value(k)
                if warnings:
                    logger.warning('No result found. Returning nothing from parse.')
                return value
        # safety net against strange responses
        except (IndexError, TypeError):
            logger.exception('Are you sure you wanted to parse this? You gave no key and there is no result.')
            raise
        except KeyError:
            logger.info('No result dictionary found.')
            return
        # Is the result just an id or response?
        if isinstance(self['result'], (six.string_types, numbers.Integral)):
            logger.debug('result looks like an id or name; returning immediately')
            return self['result']
        # Is the result just info on a single object?
        if isinstance(self['result'], dict):
            if k is None:
                return self['result']
            else:
                return self['result'][k]
        # Is the result several objects?
        if isinstance(self['result'], list):
            # get matching indexes
            if m_k is not None and m_v is not None:
                indexes = []
                for i, dictionary in enumerate(self['result']):
                    if dictionary.get(m_k) == m_v:
                        indexes.append(i)
                if not indexes:
                    logger.info('Nothing found matching {} and {}'.format(m_k, m_v))
                    return
                index = indexes[0]
            if k is None:
                # return dictionary
                return self['result'][index]
            else:
                # Return value
                try:
                    return self.get('result')[index][k]
                except IndexError:
                    logger.error("Index {} doesn't exist. If you manually entered an index, try using matching key "
                                 "and value instead.".format(index))
                    raise
                except KeyError:
                    return self._get_external_value(k)

    def _get_external_value(self, k):
        # Is the response outside of result?
        if k is not None:
            if k in self:
                value = self[k]
                if k in ['status', 'result']:
                    logger.info('There is a top level matching key {}. Using this variable is not a supported use of '
                                'parse.'.format(k))
                    logger.debug('Top level key {} is: {}.'.format(k, value))
                    return
                logger.debug("The top level value for {} is: {}".format(k, value))
                return value
        return


class GetAttr(type):
    """
    Metaclass to make classes subscriptable.
    """

    def __getitem__(cls, x):
        return getattr(cls, x)
