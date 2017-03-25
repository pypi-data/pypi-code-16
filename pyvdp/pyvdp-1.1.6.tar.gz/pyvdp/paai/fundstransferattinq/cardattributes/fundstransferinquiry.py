from pyvdp.paai.request import PaaiRequest


API = 'fundstransferattinq'
METHOD = 'cardattributes/fundstransferinquiry'


def send(data):
    """Submits Funds Transfer Inquiry request.

    :param data: **Required**. Instance of :func:`~visa.paai.fundstransferattinq.cardattributes.data.FundsTransferInquiryData`
    :return: Dictionary with VDP response

    **Example:**
        ..  code-block:: python

            from visa.paai.fundstransferattinq.cardattributes.data import FundsTransferInquiryData
            from visa.paai.fundstransferattinq.cardattribute import fundstransferinquiry

            data = FundsTransferInquiryData(stan=123456,
                                            rrn="330000123456",
                                            pan="4957030420210512")

            result = fundstransferinquiry.send(data=data)
    """
    c = PaaiRequest(api=API, method=METHOD, http_verb='POST', data=data)
    return c.send()
