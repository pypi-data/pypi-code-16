from pyvdp.visadirect.request import VisaDirectRequest


API = 'fundstransfer'
METHOD = 'pullfundstransactions'


def send(transaction, multi=False):
    """Submits a PullFundsTransactions request.

    :param transaction: **Required**. Instance of :func:`~visa.visadirect.fundstransfer.data.PullFundsTransaction` or :func:`~visa.visadirect.fundstransfer.data.MultiPullFundsTransaction`.
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiPullFundsTransaction`)
    :return: Dictionary with VDP API response

    **Example:**
        ..  code-block:: python

            from visa.visadirect.data.transaction import PullTransaction
            from visa.visadirect.fundstransfer import pull_funds

            ca = CardAcceptor(name='Acceptor 1',
                              country='RU',
                              terminal_id='TID-9999',
                              id_code='CA-IDCode-77765')

            t = PullFundsTransaction(stan=123456,
                                     amount=123.45,
                                     sender_pan='12345678123456678',
                                     sender_card_expiry_date='12-2020',
                                     sender_currency_code='USD',
                                     card_acceptor=ca)

            result = pull_funds.send(transaction=t)
    """
    method = METHOD

    if multi:
        method = 'multipullfundstransactions'

    c = VisaDirectRequest(api=API, method=method, http_verb='post', data=transaction)
    return c.send()


def get(status_id, multi=False):
    """Fetches a status of previously submitted :func:`~visa.visadirect.fundstransfer.data.PullFundsTransaction` by
    transaction identifier.

    :param str status_id: **Required**. Transaction status identifier.
    :param bool multi: **Conditional**. Indicates that transaction is a batch (:func:`~visa.visadirect.fundstransfer.data.MultiPullFundsTransaction`)
    :return: Dictionary with VDP API response

    **Example:**
        ..  code-block:: python

                from visa.visadirect.data.transaction import PullTransaction, MultiPullTransaction
                from visa.visadirect.fundstransfer import pull_funds
                from visa.exceptions import VisaTimeoutError

                ca = CardAcceptor(name='Acceptor 1',
                                  country='RU',
                                  terminal_id='TID-9999',
                                  id_code='CA-IDCode-77765')

                atom = PullFundsTransaction(stan=123456,
                                            amount=123.45,
                                            sender_pan='12345678123456678',
                                            sender_card_expiry_date='12-2020',
                                            sender_currency_code='USD',
                                            card_acceptor=ca)

                # Let's pretend its a batch
                transactions = [atom]
                mpt = MultiPullFundsTransaction(transactions=transactions)

                try:
                    # This will return HTTP 202 (multi always does)
                    pull_funds.send(transaction=mpt, multi=true)
                except VisaTimeoutError as e:
                    # Grab an exception message and use it as an argument
                    result = pull_funds.get(status_id=e.message)
    """
    method = METHOD

    if multi:
        method = 'multipullfundstransactions'

    query_string = '/' + status_id

    c = VisaDirectRequest(api=API, method=method, http_verb='get', query_string=query_string)
    return c.send()
