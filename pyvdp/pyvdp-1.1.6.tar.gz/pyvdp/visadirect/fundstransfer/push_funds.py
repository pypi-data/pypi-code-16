from pyvdp.visadirect.request import VisaDirectRequest


API = 'fundstransfer'
METHOD = 'pushfundstransactions'


def send(transaction, multi=False):
    """Submits a PushFundsTransactions request.

    :param transaction: **Required**. Instance of :func:`~visa.visadirect.fundstransfer.data.PushFundsTransaction` or :func:`~visa.visadirect.fundstransfer.data.MultiPushFundsTransaction`.
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiPushFundsTransaction`).
    :return: Dictionary with VDP API response.

    **Example:**
        ..  code-block:: python

                from visa.visadirect.data.card_acceptor import CardAcceptor
                from visa.visadirect.fundstransfer.data.push_transaction import PushTransaction

                ca = CardAcceptor(name='Acceptor 1',
                                  country='USA',
                                  terminal_id='TID-9999',
                                  id_code='CA-IDCode-77765',
                                  zip_code='12345',
                                  state='CA')

                t = PushFundsTransaction(stan=123456,
                                         amount=123.45,
                                         transaction_currency_code='USD',
                                         card_acceptor=ca,
                                         sender_pan='1234567812345678',
                                         recipient_pan='8765432187654321',
                                         recipient_name='Test')

                result = push_funds.send(transaction=t)
    """
    method = METHOD

    if multi:
        method = 'multipushfundstransactions'

    c = VisaDirectRequest(api=API, method=method, http_verb='post', data=transaction)
    return c.send()


def get(status_id, multi=False):
    """Fetches a status of previously submitted :func:`~visa.visadirect.fundstransfer.data.PushFundsTransaction` by
    transaction identifier.

    :param str status_id: **Required**. Transaction status identifier
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiPushFundsTransaction`)
    :return: Dictionary with VDP API response

    **Example:**
        ..  code-block:: python

                from visa.visadirect.data.card_acceptor import CardAcceptor
                from visa.visadirect.data.transaction import PushTransaction, MultiPushTransaction
                from visa.visadirect.fundstransfer import push_funds
                from visa.exceptions import VisaTimeoutError

                ca = CardAcceptor(name='Acceptor 1',
                                  country='USA',
                                  terminal_id='TID-9999',
                                  id_code='CA-IDCode-77765',
                                  zip_code='12345',
                                  state='CA')

                atom = PushFundsTransaction(stan=123456,
                                            amount=123.45,
                                            transaction_currency_code='USD',
                                            card_acceptor=ca,
                                            sender_pan='1234567812345678',
                                            recipient_pan='8765432187654321',
                                            recipient_name='Test')

                # Let's pretend its a batch
                mpt = [atom]
                t = MultiPushTransaction(transactions=mpt)

                try:
                    # This will return HTTP 202 (multi always does)
                    push_funds.send(transaction=mpt, multi=true)
                except VisaTimeoutError as e:
                    # Grab an exception message and use it as an argument
                    result = push_funds.get(status_id=e.message)
    """
    method = METHOD

    if multi:
        method = 'multipushfundstransactions'

    query_string = '/' + status_id

    c = VisaDirectRequest(api=API, method=method, http_verb='get', query_string=query_string)
    return c.send()
