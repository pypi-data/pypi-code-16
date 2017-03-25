from pyvdp.visadirect.request import VisaDirectRequest


API = 'reports'
METHOD = 'transactiondata'


def get(from_date, to_date):
    """Fetches transaction report for given dates range.

    :param str from_date: **Required**. Starting date *ddmmyyyy*
    :param str to_date: **Required**. Ending date *ddmmyyyy*
    :return: CSV-formatted list of transactions
    """
    query = '?fromDate=' + from_date + '&toDate=' + to_date
    c = VisaDirectRequest(api=API, method=METHOD, http_verb='get', query_string=query)
    return c.send()
