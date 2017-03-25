from pyvdp.pav.request import VisaPavRequest
from pyvdp.pav.data import PavTransaction


def send(data: PavTransaction):
    """Submits a payment account validation request.

    :param PavTransaction data: **Required**. Instance of :func:`~visa.pav.data.PavTransaction`.
    :return: A response from VDP.

    **Example:**
        ..  code-block:: python

            from visa.pav.data import PavTransaction
            from visa.pav import cardvalidation

            data = PavTransaction(stan=123456,
                                  pan='1234567812345678',
                                  expiry_date='2020-04',
                                  cvv2='123')

            result = cardvalidation.send(data=data)
    """
    c = VisaPavRequest(method='cardvalidation', http_verb='post', data=data)
    return c.send()
