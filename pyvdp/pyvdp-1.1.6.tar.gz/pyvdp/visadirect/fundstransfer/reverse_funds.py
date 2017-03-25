from pyvdp.visadirect.request import VisaDirectRequest


API = 'fundstransfer'
METHOD = 'reversefundstransactions'


def send(transaction, multi=False):
    """Submits a ReverseFundsTransactions request.

    :param ReverseTransaction|MultiReverseTransaction transaction: **Required**. Instance of :func:`~visa.visadirect.fundstransfer.data.PushFundsTransaction` or
        :func:`~visa.visadirect.fundstransfer.data.MultiPushFundsTransaction`.
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiReverseFundsTransaction`).
    :return: Dictionary with VDP response

    **Example:**
        ..  code-block:: python

            from visa.visadirect.data.card_acceptor import CardAcceptor
            from visa.visadirect.data.original_data_elements import OriginalDataElements
            from visa.visadirect.fundstransfer.data.reverse_transaction import ReverseTransaction

            from visa.visadirect.fundstransfer import reverse_funds

            ca = CardAcceptor(name='Acceptor 1',
                              country='RU',
                              terminal_id='TID-9999',
                              id_code='CA-IDCode-77765')

            ode = OriginalDataElements(stan=123456,
                                       approval_code='20304B',
                                       transmission_datetime='2017-02-16T12:59:26')

            t = ReverseTransaction(stan=123456,
                                   ode=ode,
                                   sender_pan='1234567812345678',
                                   sender_currency_code='USD',
                                   amount=123.45,
                                   sender_card_expiry_date='02-2020',
                                   transaction_identifier='123456,
                                   card_acceptor=ca)

            result = reverse_funds.send(transaction=t)
    """
    method = METHOD

    if multi:
        method = 'multireversefundstransactions'

    c = VisaDirectRequest(api=API, method=method, http_verb='post', data=transaction)
    return c.send()


def get(status_id, multi=False):
    """Fetches a status of previously submitted :func:`~visa.visadirect.fundstransfer.data.ReverseFundsTransaction` by
    transaction identifier.

    :param str status_id: **Required**. Transaction status identifier.
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiReverseFundsTransaction`)
    :return: Dictionary with VDP API response

    **Example:**
        ..  code-block:: python

            from visa.visadirect.data.card_acceptor import CardAcceptor
            from visa.visadirect.data.original_data_elements import OriginalDataElements

            from visa.visadirect.fundstransfer.data.reverse_transaction import ReverseFundsTransaction, MultiReverseFundsTransaction

            from visa.visadirect.fundstransfer import reverse_funds

            ca = CardAcceptor(name='Acceptor 1',
                              country='RU',
                              terminal_id='TID-9999',
                              id_code='CA-IDCode-77765')

            ode = OriginalDataElements(stan=123456,
                                       approval_code='20304B',
                                       transmission_datetime='2017-02-16T12:59:26')

            atom = ReverseTransaction(stan=123456,
                                      ode=ode,
                                      sender_pan='1234567812345678',
                                      sender_currency_code='USD',
                                      amount=123.45,
                                      sender_card_expiry_date='02-2020',
                                      transaction_identifier=12345,
                                      card_acceptor=ca)

            mrt = [atom]
            t = MultiReverseTransaction(transactions=mrt)

            try:
                # This will return HTTP 202 (multi always does)
                reverse_funds.send(transaction=t, multi=True)
            except VisaTimeoutError as e:
                # Grab an exception message and use it as an argument
                result = reverse_funds.get(status_id=e.message)
    """
    method = METHOD

    if multi:
        method = 'multireversefundstransactions'

    query_string = '/' + status_id

    c = VisaDirectRequest(api=API, method=method, http_verb='get', query_string=query_string)
    return c.send()
