import string
import random


class WatchlistObject(object):
    """VisaDirect WatchlistScreening WatchlistInquiry data object model.

    :param str name: **Required**. Name of the person, to receive WLM score. 1-255 characters latin string.
    :param str city: **Required**. Client city, part of :func:`~visa.visadirect.watchlist.data.WatchlistObjectAddress`.
        1-25 characters string.
    :param str issuer_country_code: **Required**. Card issuer 3 characters `ISO country code <https://developer.visa.com/request_response_codes#isoCodes>`_,
        part of :func:`~visa.visadirect.watchlist.data.WatchlistObjectAddress`.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "840",
                "acquiringBin": "408999",
                "address": {
                    "cardIssuerCountryCode": "USA",
                    "city": "San Francisco"
                },
                "name": "Mohammed Qasim",
                "referenceNumber": "330000550000"
            }
    """
    ATTR_MAPPINGS = {
        'name': 'name'
    }

    def __init__(self, city, issuer_country_code, **kwargs):

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
        self.referenceNumber = self.__get_reference()
        self.address = WatchlistObjectAddress(city=city, issuer_country_code=issuer_country_code)

    @staticmethod
    def __get_reference():
        """Generates random 12-digit reference to tie together a WLM score request and WLM score response service calls.

        :return: reference
        """
        return ''.join(random.choice(string.digits) for _ in range(12))


class WatchlistObjectAddress(object):
    """Watchlist address object model, part of :func:`~visa.visadirect.watchlist.data.WatchlistObject`.

    :param str city: **Required**. Client city name.
    :param str issuer_country_code: **Required**. Card issuer 3 characters ISO country code.
    """
    ATTR_MAPPINGS = {
        'city': 'city',
        'issuer_country_code': 'cardIssuerCountryCode'
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
