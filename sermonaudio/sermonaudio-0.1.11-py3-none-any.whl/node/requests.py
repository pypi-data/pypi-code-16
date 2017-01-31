import requests

from posixpath import join as posixjoin

import dateutil.parser

from sermonaudio import get_base_url, get_request_headers
from sermonaudio.node import types

URL_PATH = 'node'

def _get_sermons_node(node_name: str, params: dict, preferred_language_override=None):
    """Calls an endpoint named node_name with params, and expects to get a list of sermons

    :param node_name: The name of the node to call
    :param params: A dictionary of query string parameters
    :param preferred_language_override: A preferred langauge code, if you don't want to use your system locale
    :rtype: [sermonaudio.types.Sermon]
    """
    url = posixjoin(get_base_url(), URL_PATH, node_name)
    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    sermons = [types.Sermon(result) for result in node.results]
    for sermon in sermons:
        assert isinstance(sermon, types.Sermon)

    return sermons


def get_sermon_info(sermon_id: str, preferred_language_override=None):
    """Calls the sermon_info node endpoint.

    :param sermon_id: The ID of the sermon you want to fetch
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: sermonaudio.types.Sermon or None
    """
    node_name = 'sermon_info'
    params = {
        'sermonID': sermon_id
    }
    sermons = _get_sermons_node(node_name, params, preferred_language_override)

    if len(sermons) > 0:
        return sermons[0]
    else:
        return None


def get_newest_audio_sermons(page: int = 1,
                             page_size: int = None,
                             preferred_language_override=None):
    """Calls the newest_audio_sermons node endpoint.

    Returned sermons are sorted by media upload date descending.

    :param page: The page number to load (defaults to 1).
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.Sermon]
    """
    node_name = 'newest_audio_sermons'
    params = {
        'page': page,
        'page_size': page_size
    }

    return _get_sermons_node(node_name, params, preferred_language_override)


def get_newest_video_sermons(page: int = 1,
                             page_size: int = None,
                             preferred_language_override=None):
    """Calls the newest_video_sermons node endpoint.

    Returned sermons are sorted by media upload date descending.

    :param page: The page number to load (defaults to 1)
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.Sermon]
    """
    node_name = 'newest_video_sermons'
    params = {
        'page': page,
        'page_size': page_size
    }

    return _get_sermons_node(node_name, params, preferred_language_override)


def get_sermons_by_source(source_id: str,
                          only_audio_ready: bool = False,
                          event_type: str = None,
                          series: str = None,
                          page: int = 1,
                          page_size: int = None,
                          preferred_language_override=None):
    """Calls the sermons_by_source node endpoint.

    Returned sermons are sorted by date descending.

    :param source_id: The ID of the source you want a listing from
    :param only_audio_ready: If set, this flag causes the endpoint to
    return only sermons with audio available (default is to return all sermons)
    :param event_type: Filter results by sermon event type (used only if a value is supplied)
    :param series: Filter results by series (used only if a value is supplied)
    :param page: The page number to load (defaults to 1)
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.Sermon]
    """
    node_name = 'sermons_by_source'
    params = {
        'sourceID': source_id,
        'page': page,
        'page_size': page_size,
        'only_audio_ready': only_audio_ready,
        'event_type': event_type,
        'series': series
    }

    return _get_sermons_node(node_name, params, preferred_language_override)


def get_sermons_by_speaker(speaker_name: str,
                           event_type: str = None,
                           series: str = None,
                           page: int = 1,
                           page_size: int = None,
                           preferred_language_override=None):
    """Calls the sermons_by_speaker node endpoint.

    Returned sermons are sorted by date descending.

    :param speaker_name: The name of the speaker
    :param event_type: Filter results by sermon event type (used only if a value is supplied)
    :param series: Filter results by series (used only if a value is supplied)
    :param page: The page number of results to load (defaults to 1)
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: list of sermonaudio.types.Sermon
    """
    node_name = 'sermons_by_speaker'
    url = posixjoin(get_base_url(), URL_PATH, node_name)
    params = {
        'page': page,
        'page_size': page_size,
        'speakerName': speaker_name,
        'event_type': event_type,
        'series': series
    }

    return _get_sermons_node(node_name, params, preferred_language_override)


def get_sermons_by_bibref(bibbook: str,
                          bibchapter: int = None,
                          bibchapterend: int = None,
                          bibverse: int = None,
                          bibverseend: int = None,
                          page: int = 1,
                          page_size: int = None,
                          preferred_language_override=None):

    """Lists sermons preached on the specific text supplied. Text can
    either be specific, or in a range from bibchapter:bibverse to
    bibchapterend:bibverseend (with searches not spanning across
    books).

    Note that bibref does not use preferred_language_override, because
    the bibbook parameter is an OSIS paratext abbreviation and never
    localized.

    :param bibbook: The book of the Bible to search for (in three-letter OSIS paratext abbreviation format)
    :param bibchapter: Optional, limits results to this chapter of the book
    :param bibchapterend: Optional, indicates a range from bibchapterto bibchapterend
    :param bibverse: Optional, limits the results
    :param bibverseend: Optional, indicates a range from bibverse to bibverseend
    :param page: The page number of results to load (defaults to 1)
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :rtype: list of sermonaudio.types.Sermon
    """

    node_name = 'sermons_by_bibref'

    # these aren't optional/have defaults...
    params = {
        'page': page,
        'page_size': page_size,
        'bibbook': bibbook
    }
    
    #... but these are/do
    if bibchapter:
        params['bibchapter'] = bibchapter
    if bibchapterend:
        params['bibchapterend'] = bibchapterend
    if bibverse:
        params['bibverse'] = bibverse
    if bibverseend:
        params['bibverseend'] = bibverseend

    return _get_sermons_node(node_name, params, None)

def get_sermons_by_language(language_code: str,
                            page: int = 1,
                            page_size: int = None,
                            preferred_language_override=None):
    """Calls the sermons_by_language node endpoint.

    Returned sermons are sorted by date descending.

    :param language_code: An ISO 639 language code
    :param page: The page number to load (defaults to 1)
    :param page_size: The number of items per page (currently defaults to 50 if omitted).
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.Sermon]
    """
    node_name = 'sermons_by_language'
    params = {
        'languageCode': language_code,
        'page': page,
        'page_size': page_size
    }

    return _get_sermons_node(node_name, params, preferred_language_override)


def get_source_info(source_id: str, preferred_language_override=None):
    """Calls the source_info node endpoint.

    :param source_id: The ID of the source you want info on.
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: sermonaudio.types.Source
    """
    node_name = 'source_info'
    url = posixjoin(get_base_url(), URL_PATH, node_name)
    params = {
        'sourceID': source_id
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    if len(node.results) > 0:
        source = types.Source(node.results[0])
        assert isinstance(source, types.Source)

        return source
    else:
        return None


def get_webcasts_in_progress(source_id: str = None,
                             preferred_language_override=None):
    """Calls the webcasts_in_progress node endpoint.

    :param source_id: You can omit this since it defaults to API key.
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: [sermonaudio.types.WebcastInfo]
    """
    node_name = 'webcasts_in_progress'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {}
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url,
                            params=params,
                            headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    webcasts = [types.WebcastInfo(result) for result in node.results]

    for webcast in webcasts:
        assert isinstance(webcast, types.WebcastInfo)

    return webcasts


def get_sources_near_location(latitude: float, longitude: float, meters: int, preferred_language_override=None):
    """Calls the source_info node endpoint.

    :param latitude: The latitude of the search origin
    :param longitude: The longitude of the search origin
    :param meters: The distance from the origin to search
    :param preferred_language_override: An optional override to the Accept-Language header for a single request
    :rtype: sermonaudio.types.Source
    """
    node_name = 'sources_near_location'
    url = posixjoin(get_base_url(), URL_PATH, node_name)
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'meters': meters
    }

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))

    node = types.Node(response.json())
    assert node.node_type == node_name

    sources_near_location = [types.SourceNearLocation(result) for result in node.results]

    for source_near_location in sources_near_location:
        assert isinstance(source_near_location, types.SourceNearLocation)

    return sources_near_location


def get_series_list_for_source(source_id: str=None, preferred_language_override=None):
    """Returns the series for the source.
    
    :param source_id: You can omit this since it defaults to API key.
    :rtype: [Series]
    """
    node_name = 'series_list'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {}
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    series = [types.SermonSeries(result) for result in node.results]
    assert node.node_type == 'series_list'
    return series


def get_sermon_event_list(preferred_language_override=None):
    """Returns the list of event types which can be used as a filter
    in the various get_source_by_* defs.

    :rtype: [String]
    """
    node_name = 'sermon_event_type_list'
    url = posixjoin(get_base_url(), URL_PATH, node_name)
    
    params = {}
    response = requests.get(url, params={}, headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'sermon_event_type_list'
    return node.results


def get_gallery_list(source_id: str = None):
    """Returns a list of gallery categories for the source.

    Note that preferred_language_override does not apply to this call.

    :param source_id: You can omit this since it defaults to API key.
    :rtype: [String]
    """
    node_name = 'gallery_list_categories'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {}
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'gallery_category_list'
    return node.results


def get_gallery_cover_image_for_category(cat: str,
                                         source_id: str = None,
                                         preferred_language_override=None):
    """Returns the cover image for a gallery, or None if there isn't one.

    Note that preferred_language_override does not apply to this call.

    :cat: Category for which to get cover image.
    :param source_id: You can omit this since it defaults to API key.
    :rtype: sermonaudio.types.GalleryItem or None
    """
    node_name = 'gallery_cover_image_for_category'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {'category': category}
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'gallery_cover_image'
    return types.GalleryItem(node.results) if node.results is not None else None


def get_gallery_items_for_category(cat: str,
                                   includecover: bool = True,
                                   source_id: str = None,
                                   preferred_language_override=None):
    """Returns a list of images for the gallery category, optionally
    omitting the cover image.

    Note that preferred_language_override does not apply to this call.

    :param cat: Gallery category to list.
    :param includecover: Flag indicating whether to include cover image or not.
    :param source_id: You can omit this since it defaults to API key.
    :rtype: [sermonaudio.types.GalleryItem]
    """
    node_name = 'gallery_items_for_category'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {
        'category': category,
        'include_cover_image': includecover
    }
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url, params=params,
                            headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'gallery_items_list'
    return [types.GalleryItem(item) for item in node.results]


def get_event_list(upcoming: bool = True,
                   source_id: str = None,
                   preferred_language_override=None):
    """Returns a list of events for the source. Typically, you will
    want only upcoming events, not historical ones which are already
    over, but a flag is procided to get all events.

    Note that preferred_language_override does not apply to this call.

    :param upcoming: Normally defaults to true, but can be set to false to show historical events.
    :param source_id: You can omit this since it defaults to API key.
    :rtype: [String]
    """
    node_name = 'event_list'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {'upcoming': upcoming}
    if source_id:
        params['sourceID'] = source_id

    response = requests.get(url, params=params, headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'event_list'
    return node.results


def get_event_item(event_id: str,
                   source_id: str = None,
                   preferred_language_override=None):
    """Returns an event item for a given event ID

    Note that preferred_language_override does not apply to this call.

    :param event_id: The event ID to look up.
    :param source_id: You can omit this since it defaults to API key.
    :rtype: types.EventItem
    """
    node_name = 'event_info'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {'eventID': event_id}
    if source_id:
        myparams['sourceID'] = source_id

    response = requests.get(url, params=params,
                            headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'event_info'
    return types.EventItem(node.results) if node.results is not None else None


def get_spurgeon_devotional(type: str,
                            month: int,
                            day_of_month: int,
                            preferred_language_override=None):
    """Returns the Spurgeon devotional for a given month and day
    
    :param type: The type of devotional (one of the values in types.SPURGEON_DEVOTIONAL_TYPES)
    :param month: The month to return
    :param day_of_month: The day of month to return 
    :rtype: types.SpurgeonDevotional
    """
    assert type in types.SPURGEON_DEVOTIONAL_TYPES
    
    node_name = 'spurgeon_devotional'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {
        'type': type,
        'month': month,
        'day_of_month': day_of_month
    }

    response = requests.get(url, params=params,
                            headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    assert node.node_type == 'spurgeon_devotional'
    return types.SpurgeonDevotional(node.results) if node.results is not None else None


def _get_event_source(event_id: str,
                      preferred_language_override=None):
    node_name = 'event_source'
    url = posixjoin(get_base_url(), URL_PATH, node_name)

    params = {'eventID': event_id}

    response = requests.get(url, params=params,
                            headers=get_request_headers(preferred_language_override))
    node = types.Node(response.json())
    return node.results['source']
