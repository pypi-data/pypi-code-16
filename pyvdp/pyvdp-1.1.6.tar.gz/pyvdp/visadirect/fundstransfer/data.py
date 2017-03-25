from pyvdp.visadirect.data import config, VisaDirectTransaction, VisaDirectTransactionBatch


class PullFundsTransaction(VisaDirectTransaction):
    """VisaDirect FundsTransfer PullFunds data object model.

    :param int stan: **Required**. systemsTraceAuditNumber, 6 digits integer.
    :param float amount: **Required**. Transaction amount nnn.mmm.
    :param str sender_pan: **Required**. Sender PAN (Primary Account Number), 13-19 characters.
    :param datetime sender_card_expiry_date: **Required**. Sender card expiration date, YYYY-MM.
    :param str sender_currency_code: **Required**. Sender currency code, 3 characters ISO currency code.
    :param bool multi: **Conditional**. If True, this transaction is a part of batch. See :func:`~visa.visadirect.fundstransfer.data.MultiPullFundsTransaction`

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "840",
                "acquiringBin": "408999",
                "amount": "124.02",
                "businessApplicationId": "AA",
                "cardAcceptor": {
                    "address": {
                        "country": "USA",
                        "county": "San Mateo",
                        "state": "CA",
                        "zipCode": "94404"
                    },
                    "idCode": "ABCD1234ABCD123",
                    "name": "Visa Inc. USA-Foster City",
                    "terminalId": "ABCD1234"
                    },
                "cavv": "0700100038238906000013405823891061668252",
                "foreignExchangeFeeTransaction": "11.99",
                "localTransactionDateTime": "2017-03-17T08:20:42",
                "retrievalReferenceNumber": "330000550000",
                "senderCardExpiryDate": "2015-10",
                "senderCurrencyCode": "USD",
                "senderPrimaryAccountNumber": "4895142232120006",
                "surcharge": "11.99",
                "systemsTraceAuditNumber": "451001"
            }

    """
    ATTR_MAPPINGS = {
        'amount': 'amount',
        'sender_pan': 'senderPrimaryAccountNumber',
        'sender_card_expiry_date': 'senderCardExpiryDate',
        'sender_currency_code': 'senderCurrencyCode',
        'card_acceptor': 'cardAcceptor'
    }

    def __init__(self, multi=False, **kwargs):
        super(PullFundsTransaction, self).__init__(kwargs['stan'])

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        # Acquirer details are only populated for individual pull transactions, not batches
        if not multi:
            self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
            self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
            self.businessApplicationId = config.get('FUNDSTRANSFER', 'business_application_id')


class MultiPullFundsTransaction(VisaDirectTransactionBatch):
    """VisaDirect FundsTransfer MultiPullFunds data object model.

    It is container object, which incorporate PullFundsTransaction objects under the same acquirer
    credentials.

    :param list transactions: **Required**. List of :func:`~visa.visadirect.fundstransfer.data.PullFundsTransaction` objects

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "608",
                "acquiringBin": "408999",
                "businessApplicationId": "AA",
                "localTransactionDateTime": "2017-03-17T09:11:08",
                "merchantCategoryCode": "6012",
                "request": [
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "cavv": "0700020718799100000002980179911000000000",
                        "localTransactionDateTime": "2017-03-17T09:11:08",
                        "retrievalReferenceNumber": "401010101011",
                        "senderCardExpiryDate": "2020-12",
                        "senderCurrencyCode": "USD",
                        "senderPrimaryAccountNumber": "4895140000066666",
                        "systemsTraceAuditNumber": "101011"
                    },
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "cavv": "0700020718799100000002980179911000000000",
                        "localTransactionDateTime": "2017-03-17T09:11:08",
                        "retrievalReferenceNumber": "401010101011",
                        "senderCardExpiryDate": "2020-12",
                        "senderCurrencyCode": "USD",
                        "senderPrimaryAccountNumber": "4895140000066666",
                        "systemsTraceAuditNumber": "101011"
                    }
                ]
            }
    """
    def __init__(self, transactions):
        super(MultiPullFundsTransaction, self).__init__(transactions=transactions)
        self.businessApplicationId = config.get('FUNDSTRANSFER', 'business_application_id')


class PushFundsTransaction(VisaDirectTransaction):
    """VisaDirect FundsTransfer PushFunds data object model.

    :param int stan: **Required**. Systems Trace Audit Number (STAN), 6 digits integer.
    :param float amount: **Required**. Transaction amount, nnn.mmm.
    :param str transaction_currency_code: **Required**. Transaction currency ISO code, 3 characters.
    :param str sender_pan: **Required**. Sender primary account number (PAN), 13-19 digits.
    :param str recipient_pan: **Required**. Recipient primary account number (PAN), 13-19 digits.
    :param str recipient_name: **Required**. Recipient name.
    :param str sender_name: **Conditional**. Sender name.
    :param str sender_address: **Conditional**. Sender address.
    :param str sender_city: **Conditional**. Sender city.
    :param str sender_country_code: **Conditional**. Sender ISO country code, 3 characters.
    :param str sender_state_code: **Conditional**. Sender country state code.
    :param bool multi: **Conditional**. If True, constructs object, used as a part of batch. See :func:`~visa.visadirect.fundstransfer.data.MultiPushFundsTransaction`.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "840",
                "acquiringBin": "408999",
                "amount": "124.05",
                "businessApplicationId": "AA",
                "cardAcceptor": {
                    "address": {
                        "country": "USA",
                        "county": "San Mateo",
                        "state": "CA",
                        "zipCode": "94404"
                    },
                    "idCode": "CA-IDCode-77765",
                    "name": "Visa Inc. USA-Foster City",
                    "terminalId": "TID-9999"
                },
                "localTransactionDateTime": "2017-03-17T09:01:14",
                "merchantCategoryCode": "6012",
                "pointOfServiceData": {
                    "motoECIIndicator": "0",
                    "panEntryMode": "90",
                    "posConditionCode": "00"
                },
                "recipientName": "rohan",
                "recipientPrimaryAccountNumber": "4957030420210462",
                "retrievalReferenceNumber": "412770451018",
                "senderAccountNumber": "4957030420210454",
                "senderAddress": "901 Metro Center Blvd",
                "senderCity": "Foster City",
                "senderCountryCode": "124",
                "senderName": "Mohammed Qasim",
                "senderReference": "",
                "senderStateCode": "CA",
                "sourceOfFundsCode": "05",
                "systemsTraceAuditNumber": "451018",
                "transactionCurrencyCode": "USD",
                "transactionIdentifier": "381228649430015"
            }
    """

    ATTR_MAPPINGS = {
        'amount': 'amount',
        'transaction_currency_code': 'transactionCurrencyCode',
        'sender_pan': 'senderAccountNumber',
        'sender_name': 'senderName',
        'sender_address': 'senderAddress',
        'sender_city': 'senderCity',
        'sender_country_code': 'senderCountryCode',
        'sender_state_code': 'senderStateCode',
        'recipient_pan': 'recipientPrimaryAccountNumber',
        'recipient_name': 'recipientName',
        'card_acceptor': 'cardAcceptor'
    }

    def __init__(self, multi=False, **kwargs):
        super(PushFundsTransaction, self).__init__(kwargs['stan'])

        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        # Acquirer details are only populated for individual push transactions, not batches
        if not multi:
            self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
            self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
            self.businessApplicationId = config.get('FUNDSTRANSFER', 'business_application_id')


class MultiPushFundsTransaction(VisaDirectTransactionBatch):
    """VisaDirect FundsTransfer MultiPushFunds data object model.

    It is container object, which incorporate PushFundsTransaction objects under the same acquirer
    credentials.

    :param list transactions: **Required**. List of :func:`~visa.visadirect.fundstransfer.data.PushFundsTransaction` objects

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "840",
                "acquiringBin": "408999",
                "businessApplicationId": "AA",
                "localTransactionDateTime": "2017-03-17T09:12:46",
                "merchantCategoryCode": "6012",
                "request": [
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "feeProgramIndicator": "123",
                        "localTransactionDateTime": "2017-03-17T09:12:46",
                        "recipientName": "Akhila",
                        "recipientPrimaryAccountNumber": "4957030420210454",
                        "retrievalReferenceNumber": "401010101011",
                        "senderAccountNumber": "4005520000011126",
                        "senderAddress": "My Address",
                        "senderCity": "My City",
                        "senderCountryCode": "USA",
                        "senderName": "Mr Name",
                        "senderReference": "",
                        "senderStateCode": "CA",
                        "sourceOfFundsCode": "01",
                        "systemsTraceAuditNumber": "101011",
                        "transactionCurrencyCode": "USD",
                        "transactionIdentifier": "234234234234234"
                    },
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "feeProgramIndicator": "123",
                        "localTransactionDateTime": "2017-03-17T09:12:46",
                        "recipientName": "Akhila",
                        "recipientPrimaryAccountNumber": "4957030420210454",
                        "retrievalReferenceNumber": "401010101012",
                        "senderAccountNumber": "4840920103511221",
                        "senderAddress": "My Address",
                        "senderCity": "My City",
                        "senderCountryCode": "USA",
                        "senderName": "Mr Name",
                        "senderReference": "",
                        "senderStateCode": "CA",
                        "sourceOfFundsCode": "01",
                        "systemsTraceAuditNumber": "101012",
                        "transactionCurrencyCode": "USD",
                        "transactionIdentifier": "234234234234234"
                    }
                ]
            }
    """
    def __init__(self, transactions):
        super(MultiPushFundsTransaction, self).__init__(transactions=transactions)
        self.businessApplicationId = config.get('FUNDSTRANSFER', 'business_application_id')


class ReverseFundsTransaction(PullFundsTransaction):
    """VisaDirect FundsTransfer ReverseFunds data object model.

    :param int stan: **Required**. Systems Trace Audit Number, required, 6 digits integer.
    :param str sender_pan: **Required**. Sender Primary Account Number, 13-19 characters sender PAN.
    :param str sender_card_expiry_date: **Required**. Sender Card Expiry Date,, YYYY-MM sender card expiration date.
    :param str sender_currency_code: **Required**. Sender Currency Code, required, 3 characters ISO currency code.
    :param float amount: **Required**. Transaction amount.
    :param int transaction_identifier: **Required**. Transaction Identifier, 15 digits integer.
    :param OriginalDataElements ode: **Required**. Instance of :func:`~visa.visadirect.data.OriginalDataElements` object.

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "608",
                "acquiringBin": "408999",
                "amount": "24.01",
                "cardAcceptor": {
                    "address": {
                        "country": "USA",
                        "county": "San Mateo",
                        "state": "CA",
                        "zipCode": "94404"
                    },
                    "idCode": "VMT200911026070",
                    "name": "Visa Inc. USA-Foster City",
                    "terminalId": "365539"
                },
                "localTransactionDateTime": "2017-03-17T09:02:32",
                "originalDataElements": {
                    "acquiringBin": "408999",
                    "approvalCode": "20304B",
                    "systemsTraceAuditNumber": "897825",
                    "transmissionDateTime": "2017-03-17T09:02:32"
                },
                "pointOfServiceCapability": {
                    "posTerminalEntryCapability": "2",
                    "posTerminalType": "4"
                },
                "pointOfServiceData": {
                    "motoECIIndicator": "0",
                    "panEntryMode": "90",
                    "posConditionCode": "00"
                },
                "retrievalReferenceNumber": "330000550000",
                "senderCardExpiryDate": "2015-10",
                "senderCurrencyCode": "USD",
                "senderPrimaryAccountNumber": "4895100000055127",
                "systemsTraceAuditNumber": "451050",
                "transactionIdentifier": "381228649430011"
            }
    """
    ATTR_MAPPINGS = {
        'sender_pan': 'senderPrimaryAccountNumber',
        'sender_card_expiry_date': 'senderCardExpiryDate',
        'sender_currency_code': 'senderCurrencyCode',
        'amount': 'amount',
        'transaction_identifier': 'transactionIdentifier',
        'card_acceptor': 'cardAcceptor',
        'ode': 'originalDataElements'
    }

    def __init__(self, ode, **kwargs):
        super(ReverseFundsTransaction, self).__init__(**kwargs)
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
        self.originalDataElements = ode


class MultiReverseFundsTransaction(MultiPullFundsTransaction):
    """VisaDirect FundsTransfer MultiReverseFunds data object model.

    It is container object, which incorporate ReverseFundsTransaction objects under the same acquirer
    credentials.

    :param list transactions: **Required**. List of :func:`~visa.visadirect.fundstransfer.data.ReverseFundsTransaction` objects

    **Example:**
        ..  code-block:: json

            {
                "acquirerCountryCode": "840",
                "acquiringBin": "408999",
                "localTransactionDateTime": "2017-03-17T09:09:05",
                "request": [
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "localTransactionDateTime": "2017-03-17T09:09:05",
                        "originalDataElements": {
                            "acquiringBin": "408999",
                            "approvalCode": "1ABCDE",
                            "systemsTraceAuditNumber": "228112",
                            "transmissionDateTime": "2017-03-17T09:09:05"
                        },
                        "retrievalReferenceNumber": "401010101011",
                        "senderCardExpiryDate": "2020-12",
                        "senderCurrencyCode": "USD",
                        "senderPrimaryAccountNumber": "4485810000000131",
                        "systemsTraceAuditNumber": "101011",
                        "transactionIdentifier": "101010101010"
                    },
                    {
                        "amount": "100.00",
                        "cardAcceptor": {
                            "address": {
                                "country": "USA",
                                "county": "00",
                                "state": "CA",
                                "zipCode": "94454"
                            },
                            "idCode": "5678",
                            "name": "Mr Smith",
                            "terminalId": "1234"
                        },
                        "localTransactionDateTime": "2017-03-17T09:09:05",
                        "originalDataElements": {
                            "acquiringBin": "408999",
                            "approvalCode": "1ABCDE",
                            "systemsTraceAuditNumber": "228112",
                            "transmissionDateTime": "2017-03-17T09:09:05"
                        },
                        "retrievalReferenceNumber": "401010101011",
                        "senderCardExpiryDate": "2020-12",
                        "senderCurrencyCode": "USD",
                        "senderPrimaryAccountNumber": "4485810000000131",
                        "systemsTraceAuditNumber": "101011",
                        "transactionIdentifier": "101010101010"
                    }
                ]
            }
    """
    def __init__(self, transactions):
        super(MultiReverseFundsTransaction, self).__init__(transactions=transactions)
        self.businessApplicationId = config.get('FUNDSTRANSFER', 'business_application_id')

