class PavTransaction(object):
    """Visa Payment Account Validation Object data object model.

    :param int stan: **Required**. Systems Trace Audit Number (STAN), 6-digits integer.
    :param str pan: **Required**. Primary Account Number (PAN), 13-19 digits string.
    :param str expiry_date: **Required**. Card expiration date, YYYY-MM.
    :param str cvv2: **Required**. Card CVV2 value. 3-4 characters string.

    **Example:**
        ..  code-block:: json

            {
                "addressVerificationResults": {
                    "postalCode": "T4B 3G5",
                    "street": "2881 Main Street Sw"
                },
                "cardAcceptor": {
                    "address": {
                        "city": "fostr city",
                        "country": "PAKISTAN",
                        "county": "CA",
                        "state": "CA",
                        "zipCode": "94404"
                    },
                    "idCode": "111111",
                    "name": "rohan",
                    "terminalId": "123"
                },
                "cardCvv2Value": "672",
                "cardExpiryDate": "2018-06",
                "primaryAccountNumber": "4957030000313108",
                "retrievalReferenceNumber": "015221743720",
                "systemsTraceAuditNumber": "743720"
            }
    """
    ATTR_MAPPINGS = {
        'stan': 'systemsTraceAuditNumber',
        'pan': 'primaryAccountNumber',
        'expiry_date': 'cardExpiryDate',
        'cvv2': 'cardCvv2Value'
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
