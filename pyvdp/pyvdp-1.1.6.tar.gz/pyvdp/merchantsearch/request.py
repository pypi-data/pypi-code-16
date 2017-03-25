from pyvdp.request import VisaRequest


class VisaMerchantSearchRequest(VisaRequest):
    """Implements HTTP requests to Visa MerchantSearch APIs.

    https://developer.visa.com/products/merchant_search/guides

    :param str query_string: **Conditional**. Query string to append to URL
    :param object data: **Conditional**. Payload for POST/PUT requests
    :param dict headers: **Optional**. Additional headers as dictionary
    """

    def __init__(self, query_string='', data=None, headers=None):

        super(VisaMerchantSearchRequest, self).__init__(resource='merchantsearch',
                                                        api='',
                                                        method='search',
                                                        http_verb='post',
                                                        query_string=query_string,
                                                        data=data,
                                                        headers=headers)

