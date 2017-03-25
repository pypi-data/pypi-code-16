from pyvdp.request import VisaRequest


class VisaPavRequest(VisaRequest):
    """Instantiates connection to PaymentAccountValidation VDP API endpoint.

    :param str method: **Required**. VDP method name.
    :param str http_verb: **Required**. HTTP verb (GET, POST).
    :param str query_string: **Conditional**. Query string to append to URL.
    :param object data: **Conditional**. Object to submit as POST/PUT payload.
    :param dict headers: **Optional**. Additional headers as dictionary.
    """
    def __init__(self, method, http_verb, query_string='', data=None, headers=None):
        super(VisaPavRequest, self).__init__(resource='pav', api='', method=method, http_verb=http_verb,
                                             query_string=query_string, data=data, headers=headers)
