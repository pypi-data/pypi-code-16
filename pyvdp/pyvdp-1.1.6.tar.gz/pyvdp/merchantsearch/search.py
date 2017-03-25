from pyvdp.merchantsearch.request import VisaMerchantSearchRequest
from pyvdp.merchantsearch.data import MerchantSearchData


def send(data):
    """Submits a merchant search request.

    :param MerchantSearchData data: **Required**. Instance of :func:`~visa.merchantsearch.data.MerchantSearchData`.
    :return: A response from VDP.

    **Example:**
        ..  code-block:: python

            from visa.merchantsearch.data import MerchantSearchData
            from visa.merchantsearch import search

            # See docs for MerchantSearchAttrList to find out how to build search_attrs
            search_attrs = {
                'merchant_name': 'Acme Inc',
                'visa_merchant_id': 12345678,
                'visa_store_id': 123456789,
                'business_registration_id': 386004447,
                'merchant_url': 'http://www.emc.cmich.edu',
                'acquirer_card_acceptor_id': 424295031886,
                'acquiring_bin': 476197
            }

            response_attrs = ['GNSTANDARD']

            search_options = {
                'max_records': 5,
                'match_indicators': True,
                'match_score': True,
                'proximity': list('Acme'),
                'wildcard': list('*cme*')
            }

            data = MerchantSearchData(search_attrs=search_attrs,
                                      response_attrs=response_attrs,
                                      options=search_options)

            result = search.send(data=data)
    """
    c = VisaMerchantSearchRequest(data=data)
    return c.send()
