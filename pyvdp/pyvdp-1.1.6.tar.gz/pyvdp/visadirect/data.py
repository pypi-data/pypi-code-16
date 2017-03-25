import os

from datetime import datetime

try:
    import configparser as parser
except ImportError:
    import ConfigParser as parser

# Current directory
BASE_DIR = os.path.dirname(__file__)

config = parser.ConfigParser()
config_file = os.path.join(BASE_DIR, '../configuration.ini')

if os.path.exists(config_file):
    config.read(config_file)
else:
    # use example config as a stub for tests
    config.read(os.path.join(BASE_DIR, '../configuration.ini.example'))

transaction_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class VisaDirectTransaction(object):
    """Abstract VISA Transaction object model.

    Constructs and populates general attributes, such as systemsTraceAuditNumber (stan), retrievalReferenceNumber
    (rrn) and localTransactionDateTime.

    :param str stan: **Required**. Systems Trace Audit Number (STAN), 6 digits integer.
    """
    def __init__(self, stan):

        self.systemsTraceAuditNumber = stan
        self.localTransactionDateTime = transaction_datetime
        self.retrievalReferenceNumber = self.get_rrn()

    def get_rrn(self):
        """Generates RRN (retrievalReferenceNumber).

        :return: str rrn: Last digit of current year + number of current day in the year + current hour + STAN
        """
        now = datetime.now()
        year_last_digit = now.strftime('%Y')[3]
        day_of_the_year = now.strftime('%j')
        current_hour = now.strftime('%H')
        return year_last_digit + day_of_the_year + current_hour + str(self.systemsTraceAuditNumber)


class VisaDirectTransactionBatch(object):
    """Abstract TransactionBatch object model.

    Constructs and populates a 'transaction of transactions', normally submitted with `multi` requests.
    This class is not supposed to be instantiated on its own, it is just providing a `shell` for batch requests

    :param list transactions: **Required**. List of :func:`~visa.visadirect.data.VisaDirectTransaction` objects.
    """
    def __init__(self, transactions):
        self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
        self.acquirerCountryCode = config.get('ACQUIRER', 'acquirer_country_code')
        self.localTransactionDateTime = transaction_datetime
        self.request = transactions


class CardAcceptor(object):
    """Card Acceptor object model.

    https://en.wikipedia.org/wiki/ISO_8583

    :param str name: **Required**. Card Acceptor name.
    :param str terminal_id: **Required**. Card Acceptor terminal ID.
    :param str id_code: **Required**. Card Acceptor ID code.
    :param dict address: **Conditional**. Card acceptor address dictionary. See :func:`CardAcceptorAddress` attributes
        for details.
    """

    ATTR_MAPPINGS = {
        'name': 'name',
        'terminal_id': 'terminalId',
        'id_code': 'idCode',
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)

        try:
            self.address = self.CardAcceptorAddress(**kwargs['address'])
        except KeyError:
            # If address is missing, skip silently, errors will be handled by VDP
            pass

    class CardAcceptorAddress(object):
        """Card Acceptor address object model (part of :func:`~visa.visadirect.data.CardAcceptor` object).

        Populated from `address` dictionary argument for :func:`~visa.visadirect.data.CardAcceptor` class.

        :param str country: **Required**. Address country ISO code.
        :param str zip_code: **Conditional**. Address ZIP code.
        :param str state: **Condtional**. Address state name.
        """
        ATTR_MAPPINGS = {
            'country': 'country',
            'zip_code': 'zipCode',
            'state': 'state',
            'city': 'city'
        }

        def __init__(self, **kwargs):
            self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)


class OriginalDataElements(object):
    """Object model for Original Data Elements object, used for reverse transactions.

    :param int stan: **Required**. Systems trace audit number, 6 digits integer.
    :param datetime transmission_datetime: **Required**. Original AFT Datetime YYYY-MM-DDThh:mm:ss
    :param str approval_code: **Optional**. Approval code from original AFT, 6 characters string.
    """
    ATTR_MAPPINGS = {
        'stan': 'systemsTraceAuditNumber',
        'approval_code': 'approvalCode',
        'transmission_datetime': 'transmissionDateTime',
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
        self.acquiringBin = config.get('ACQUIRER', 'acquiring_bin')
