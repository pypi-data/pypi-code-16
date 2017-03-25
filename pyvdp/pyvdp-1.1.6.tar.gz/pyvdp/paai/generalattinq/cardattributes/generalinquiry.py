from pyvdp.paai.request import PaaiRequest


API = 'generalattinq'
METHOD = 'cardattributes/generalinquiry'


def send(data):
    """Submits General Card Attributes Inquiry request.

    :param data: **Required**. Instance of :func:`~visa.paai.generalattinq.cardattributes.data.GeneralInquiryData`
    :return: Dictionary with VDP response

    **Example:**
        ..  code-block:: python

            from visa.paai.generalattinq.cardattributes.data import GeneralInquiryData
            from visa.paai.generalattinq.cardattributes import generalinquiry

            data = GeneralInquiryData(pan="4957030420210512")

            result = generalinquiry.send(data=data)
    """
    c = PaaiRequest(api=API, method=METHOD, http_verb='POST', data=data)
    return c.send()
