from pyvdp.visadirect.request import VisaDirectRequest


API = 'mvisa'
METHOD = 'cashinpushpayments'


def send(transaction):
    """Sends VisaDirect mVISA CashinPushPayments POST request.

    :param transaction: **Required**. Instance of PushTransaction or MultiPushTransaction.
    :return: Dictionary with VDP API response.
    """

    c = VisaDirectRequest(api=API, method=METHOD, http_verb='post', data=transaction)
    return c.send()


def get(status_id: str):
    """Sends VisaDIrect mVISA CashinPushPayments GET request.

    :param str status_id: **Required**. Transaction status identifier
    :return: Dictionary with VDP API response
    """

    query_string = '/' + status_id

    c = VisaDirectRequest(api=API, method=METHOD, http_verb='get', query_string=query_string)
    return c.send()
