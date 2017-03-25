from pyvdp.visadirect.request import VisaDirectRequest


def send(data):
    """Submits a WatchlistInquiry request.

    :param WatchlistObject data: **Required**. Instance of :func:`~visa.visadirect.watchlist.data.WatchlistObject`.
    :return: Dictionary with VDP API response

    **Example:**
        ..  code-block:: python

            from visa.visadirect.watchlist import watchlistinquiry
            from visa.visadirect.watchlist.data import WatchlistObject

            data = WatchlistObject(name='Pavel Pokrovskiy',
                                   city='Moscow',
                                   issuer_country_code='RU')

            result = watchlistinquiry.send(data)
    """
    c = VisaDirectRequest(api='watchlistscreening', method='watchlistinquiry', http_verb='post', data=data)
    return c.send()
