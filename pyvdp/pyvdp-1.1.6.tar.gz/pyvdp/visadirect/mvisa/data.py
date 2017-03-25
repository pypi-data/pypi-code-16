"""
Definitions of data object models for VisaDirect mVISA operations.
"""
from pyvdp.visadirect.data import config, VisaDirectTransaction


class CashinPushPaymentTransaction(VisaDirectTransaction):
    """Data model for mVISA CashinPushPayments API.

    :param int stan: **Required**. Systems trace audit number. 6 digits positive integer.
    :param str recipient_pan: **Required**. Recipient primary account number (PAN). 13-19 characters string.
    :param float amount: **Required**. Transaction amount. 12 digits, 3 fractions.
    :param CardAcceptor card_acceptor: **Required**. Instance of :func:`~visa.visadirect.data.CardAcceptor` data object
    :param str transaction_currency_code: **Required**. Transaction `ISO currency code <https://developer.visa.com/request_response_codes#isoCodes>`_. 3 characters string.
    :param str sender_account_number: **Optional**.
    :param str sender_name: **Optional**. Sender name in Latin characters. Max 30 characters string.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "643",
                "acquiringBin": "400171",
                "amount": "124.05",
                "businessApplicationId": "CI",
                "cardAcceptor": {
                    "address": {
                        "city": "Bangalore",
                        "country": "IND"
                    },
                    "idCode": "ID-Code123",
                    "name": "Card Accpector ABC"
                },
                "localTransactionDateTime": "2017-03-17T05:42:01",
                "merchantCategoryCode": "4829",
                "recipientPrimaryAccountNumber": "4123640062698797",
                "retrievalReferenceNumber": "430000367618",
                "senderAccountNumber": "4541237895236",
                "senderName": "Mohammed Qasim",
                "senderReference": "1234",
                "systemsTraceAuditNumber": "313042",
                "transactionCurrencyCode": "USD",
                "transactionIdentifier": "381228649430015"
            }

    ..  seealso::

        `VisaDirect mVISA CashinPushPayments Reference <https://developer.visa.com/products/visa_direct/reference#visa_direct__mvisa__v1__cash_in_push_payments>`_

    """
    # Mappings between constructor arguments and VISA API fields
    # {'constructor argument': 'VISA API field name'}
    ATTR_MAPPINGS = {
        'amount': 'amount',
        'recipient_pan': 'recipientPrimaryAccountNumber',
        'transaction_currency_code': 'transactionCurrencyCode',
        'sender_name': 'senderName',
        'sender_account_number': 'senderAccountNumber',
        'card_acceptor': 'cardAcceptor'
    }

    def __init__(self, **kwargs):
        super(CashinPushPaymentTransaction, self).__init__(kwargs['stan'])

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
        self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
        self.businessApplicationId = config.get('MVISA', 'cashin_business_application_id')


class CashoutPushPaymentTransaction(VisaDirectTransaction):
    """Data model for mVISA CashoutPushPayments API.

    :param int stan: **Required**. Systems trace audit number. 6 digits positive integer.
    :param str recipient_pan: **Required**. Recipient primary account number (PAN). 13-19 characters string.
    :param float amount: **Required**. Transaction amount. 12 digits, 3 fractions.
    :param CardAcceptor card_acceptor: **Required**. Instance of :func:`~visa.visadirect.data.CardAcceptor` data object
    :param str transaction_currency_code: **Required**. Transaction `ISO currency code <https://developer.visa.com/request_response_codes#isoCodes>`_. 3 characters string.
    :param str sender_account_number: **Optional**.
    :param str sender_name: **Optional**. Sender name in Latin characters. Max 30 characters string.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "643",
                "acquiringBin": "400171",
                "amount": "124.05",
                "businessApplicationId": "CO",
                "cardAcceptor": {
                    "address": {
                        "city": "mVisa cashout",
                        "country": "IND"
                    },
                    "idCode": "CA-IDCode-77765",
                    "name": "mVisa cashout"
                },
                "localTransactionDateTime": "2017-03-17T05:46:12",
                "merchantCategoryCode": "6012",
                "recipientPrimaryAccountNumber": "4123640062698797",
                "retrievalReferenceNumber": "412123412878",
                "senderAccountNumber": "456789123456",
                "senderName": "Mohammed Qasim",
                "senderReference": "REFNUM123",
                "systemsTraceAuditNumber": "567889",
                "transactionCurrencyCode": "USD",
                "transactionIdentifier": "381228649430015"
            }

    ..  seealso::

        `VisaDirect mVISA CashoutPushPayments Reference <https://developer.visa.com/products/visa_direct/reference#visa_direct__mvisa__v1__cash_out_push_payments_post>`_

    """
    # Mappings between constructor arguments and VISA API fields
    # {'constructor argument': 'VISA API field name'}
    ATTR_MAPPINGS = {
        'amount': 'amount',
        'recipient_pan': 'recipientPrimaryAccountNumber',
        'transaction_currency_code': 'transactionCurrencyCode',
        'sender_name': 'senderName',
        'sender_account_number': 'senderAccountNumber',
        'card_acceptor': 'cardAcceptor'
    }

    def __init__(self, **kwargs):
        super(CashoutPushPaymentTransaction, self).__init__(kwargs['stan'])

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
        self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
        self.businessApplicationId = config.get('MVISA', 'cashout_business_application_id')


class MerchantPushPaymentTransaction(VisaDirectTransaction):
    """Data model for mVISA MerchantPushPayments API.

    :param int stan: **Required**. Systems trace audit number. 6 digits positive integer.
    :param str recipient_pan: **Required**. Recipient primary account number (PAN). 13-19 characters string.
    :param float amount: **Required**. Transaction amount. 12 digits, 3 fractions.
    :param CardAcceptor card_acceptor: **Required**. Instance of :func:`~visa.visadirect.data.card_acceptor.CardAcceptor` data object
    :param str transaction_currency_code: **Required**. Transaction `ISO currency code <https://developer.visa.com/request_response_codes#isoCodes>`_. 3 characters string.
    :param PurchaseIdentifier purchase_identifier: **Required**. Instance of :func:`~visa.visadirect.mvisa.data.purchase_identifier.PurchaseIdentifier` data object
    :param str sender_account_number: **Required**. Consumer account number. Max 34 characters string.
    :param str sender_name: **Required**. Sender name in Latin characters. Max 30 characters string.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "356",
                "acquiringBin": "408972",
                "amount": "124.05",
                "businessApplicationId": "MP",
                "cardAcceptor": {
                    "address": {
                        "city": "KOLKATA",
                        "country": "IND"
                    },
                    "idCode": "CA-IDCode-77765",
                    "name": "Visa Inc. USA-Foster City"
                },
                "feeProgramIndicator": "123",
                "localTransactionDateTime": "2017-03-17T05:51:16",
                "purchaseIdentifier": {
                    "referenceNumber": "REF_123456789123456789123",
                    "type": "1"
                },
                "recipientName": "Jasper",
                "recipientPrimaryAccountNumber": "4123640062698797",
                "retrievalReferenceNumber": "412770451035",
                "secondaryId": "123TEST",
                "senderAccountNumber": "4027290077881587",
                "senderName": "Jasper",
                "senderReference": "",
                "systemsTraceAuditNumber": "451035",
                "transactionCurrencyCode": "INR",
                "transactionIdentifier": "381228649430015"
            }

    ..  seealso::

        `VisaDirect mVISA MerchantPushPayments Reference <https://developer.visa.com/products/visa_direct/reference#visa_direct__mvisa__v1__merchant_push_payments_post>`_

    """

    # Mappings between constructor arguments and VISA API fields
    # {'constructor argument': 'VISA API field name'}
    ATTR_MAPPINGS = {
        'amount': 'amount',
        'recipient_pan': 'recipientPrimaryAccountNumber',
        'transaction_currency_code': 'transactionCurrencyCode',
        'sender_name': 'senderName',
        'sender_account_number': 'senderAccountNumber',
        'purchase_identifier': 'purchaseIdentifier',
        'card_acceptor': 'cardAcceptor',
    }

    def __init__(self, **kwargs):
        super(MerchantPushPaymentTransaction, self).__init__(kwargs['stan'])

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
        self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
        self.businessApplicationId = config.get('MVISA', 'mp_business_application_id')


class PurchaseIdentifier(object):
    """Data model for VisaDirect mVISA PurchaseIdentifier object.

    Used as a part of :func:`~visa.visadirect.mvisa.data.MerchantPushPaymentTransaction`.

    :param str type: **Required**. Primary ID as defined by mVISA. 1 character string.
    :param str reference_number: **Required**. Key data element for matching a message to others within a given
        transaction set. Value will be the same as what has been provided in the request. Max 13 characters string.
    """

    ATTR_MAPPINGS = {
        'type': 'type',
        'reference_number': 'referenceNumber',
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
