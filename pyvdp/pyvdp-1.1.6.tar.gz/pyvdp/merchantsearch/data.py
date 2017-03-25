import time

from datetime import datetime


class MerchantSearchData(object):
    """Visa Merchant Search data object model.

    :param dict header: **Required**. A dictionary with header parameters. See :func:`~visa.merchantsearch.data.MerchantSearchData.MerchantSearchHeader`
        for possible keys.
    :param dict search_attrs: **Required**. A dictionary with search atttributes. See :func:`~visa.merchantsearch.data.MerchantSearchData.MerchantSearchAttrList`
        for possible keys.
    :param list response_attrs: **Required**. A list with attributes (Group Names) to include in response.
    :param dict options: **Required**. A dictionary with search options. See :func:`~visa.merchantsearch.data.MerchantSearchData.MerchantSearchOptions`
        for possible keys.

    **Example:**
        ..  code-block:: json

            {
                "header": {
                    "messageDateTime": "2017-03-18T03:39:08.903",
                    "requestMessageId": "Request_001",
                    "startIndex": "0"
                },
                "searchAttrList": {
                    "merchantName": "cmu edctn materials cntr",
                    "merchantStreetAddress": "802 industrial dr",
                    "merchantCity": "Mount Pleasant",
                    "merchantState": "MI",
                    "merchantPostalCode": "48858",
                    "merchantCountryCode": "840",
                    "merchantPhoneNumber": "19897747123",
                    "merchantUrl": "http://www.emc.cmich.edu",
                    "businessRegistrationId": "386004447",
                    "acquirerCardAcceptorId": "424295031886",
                    "acquiringBin": "476197"
                },
                "responseAttrList": [
                    "GNSTANDARD"
                ],
                "searchOptions": {
                    "maxRecords": "5",
                    "matchIndicators": "true",
                    "matchScore": "true",
                    "proximity": [
                        "merchantName"
                    ],
                    "wildCard": [
                        "merchantName"
                    ]
                }
            }
    """

    def __init__(self, header, search_attrs, response_attrs, options):
        self.header = self.MerchantSearchHeader(**header)
        self.searchAttrList = self.MerchantSearchAttrList(**search_attrs)
        self.responseAttrList = response_attrs
        self.searchOptions = self.MerchantSearchOptions(**options)


    class MerchantSearchHeader(object):
        """MerchantSearch header data object model.

        Part of MerchantSearchData object.

        :param str message_id: **Optional**. Unique string ID for service request. String 50 characters max. Default
            'Request_' + epoch
        :param int startIndex: **Optional**. Starting records index in response.
        """

        def __init__(self, **kwargs):
            self.messageDateTime = self._get_datetime()

            if kwargs and 'message_id' in kwargs:
                self.requestMessageId = kwargs['message_id']
            else:
                self.requestMessageId = self._get_message_id()

            if kwargs and 'start_index' in kwargs:
                self.startIndex = kwargs['start_index']
            else:
                self.startIndex = 0

        @staticmethod
        def _get_datetime():
            date_format = '%Y-%m-%dT%H:%M:%S.%f'
            now = datetime.now()
            return now.strftime(date_format)[:-3]

        @staticmethod
        def _get_message_id():
            return 'Request_' + str(int(time.time()))

    class MerchantSearchAttrList(object):
        """MerchantSearch searchAttrList data object model.

        Part of MerchantSearchData object.

        :param str merchant_name: **Conditional**. Name of the merchant. Optional when any one of VisaMerchantId or
            VisaStoreId or BusinessRegistrationId or MerchantUrl or AcquirerCardAcceptorId is provided.
        :param str merchant_street_address: **Conditional**. Merchant street adress.
        :param str merchant_city: **Conditional**. City of the registered merchant.
        :param str merchant_state: **Conditional**. Merchant state code. 2 characters string.
        :param str merchant_postal_code: **Conditional**. Merchant postal code.
        :param int merchant_country_code: **Conditional**. Merchant country code, mandatory with merchant_name.
        :param int merchant_phone_number: **Conditional**. Merchant phone number.
        :param str merchant_url: **Conditional**. Merchant registered URL. Optional when any one of MerchantName or
            VisaMerchantId or VisaStoreId or BusinessRegistrationId or AcquirerCardAcceptorId is provided.
        :param int visa_merchant_id: **Conditional**. Merchant ID provided by VISA. Optional when any one of MerchantName
            or VisaStoreId or BusinessRegistrationId or MerchantUrl or AcquirerCardAcceptorId is provided. 8 characters
            double.
        :param int visa_store_id: **Conditional**. Merchant store/branch ID, provided by VISA. Optional when any one of
            MerchantName or VisaMerchantId or BusinessRegistrationId or MerchantUrl or AcquirerCardAcceptorId is provided.
            9 characters double.
        :param str business_registration_id: **Conditional**. Merchant business/tax registration ID. Optional when any
            one of MerchantName or VisaMerchantId or VisaStoreId or MerchantUrl or AcquirerCardAcceptorId is provided.
        :param str merchant_url: **Conditional**. Merchant registered URL. Optional when any one of MerchantName or
            VisaMerchantId or VisaStoreId or BusinessRegistrationId or AcquirerCardAcceptorId is provided.
        :param str acquirer_card_acceptor_id: **Conditional**. Acquirer card acceptor ID. Optional when any one of
            MerchantName or VisaMerchantId or VisaStoreId or BusinessRegistrationId or MerchantUrl is provided. 15 digits
            string. Prepend 0 if less than 15 digits.
        :param int acquiring_bin: **Conditional**. Acquirer business identification number. Required when
            AcquirerCardAcceptorId is provided.
        """

        ATTR_MAPPINGS = {
            'merchant_name': 'merchantName',
            'merchant_street_address': 'merchantStreetAddress',
            'merchant_city': 'merchantCity',
            'merchant_state': 'merchantState',
            'merchant_postal_code': 'merchantPostalCode',
            'merchant_country_code': 'merchantCountryCode',
            'merchant_phone_number': 'merchantPhoneNumber',
            'merchant_url': 'merchantUrl',
            'visa_merchant_id': 'visaMerchantId',
            'visa_store_id': 'visaStoreId',
            'business_registration_id': 'businessRegistrationId',
            'acquirer_card_acceptor_id': 'acquirerCardAcceptorId',
            'acquiring_bin': 'acquiringBin',
        }

        def __init__(self, **kwargs):
            self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

    class MerchantSearchOptions(object):
        """MerchantSearch searchOptions data object model.

        Part of MerchantSearch data object.

        :param int max_records: **Optional**. Maximum number of records in response. Default 25.
        :param bool match_indicators: **Optional**. Show request attributes, that match a record.
        :param bool match_score: **Optional**. Add matchScore and order response per matchScore.
        :param list proximity: **Optional**. Proximity search on merchant name. If wildcards are used, proximity is ignored.
        :param list wildcards: **Optional**. Wildcard search on merchant name.
        """

        ATTR_MAPPINGS = {
            'max_records': 'maxRecords',
            'match_indicators': 'matchIndicators',
            'match_score': 'matchScore',
        }

        def __init__(self, proximity=None, wildcards=None, **kwargs):
            self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

            if proximity:
                self.proximity = proximity

            if wildcards:
                self.wildCards = wildcards
