from txgoogleapi.base import GoogleApi, GoogleApiEndPoint, SET, BOOL, INT


class Playlists(GoogleApiEndPoint):
    _url = '/playlists'
    _methods = {
        'list': {
            'method': 'GET',
            'required': {
                'part': SET('id', 'snippet', 'status'),
            },
            'filter': {
                'channelId': str,
                'id': str,
                'mine': BOOL,
            },
            'optional': {
                'maxResults': INT,
                'onBehalfOfContentOwner': str,
                'onBehalfOfContentOwnerChannel': str,
                'pageToken': str
            },
        },
        'insert': {
            'method': 'POST',
            'required': {
                'part': SET('snippet', 'status'),
            },
            'optional': {
                'onBehalfOfContentOwner': str,
                'onBehalfOfContentOwnerChannel': str,
            },
        },
        'update': {
            'method': 'PUT',
            'required': {
                'part': SET('snippet', 'status'),
            },
            'optional': {
                'onBehalfOfContentOwner': str,
            },
        },
        'delete': {
            'method': 'DELETE',
            'required': {
                'id': str,
            },
            'optional': {
                'onBehalfOfContentOwner': str,
            },
        },
    }


class PlaylistItems(GoogleApiEndPoint):
    _url = '/playlistItems'
    _methods = {
        'list': {
            'method': 'GET',
            'required': {
                'part': SET('id', 'snippet', 'contentDetails', 'status'),
            },
            'filter': {
                'id': str,
                'playlistId': str,
            },
            'optional': {
                'maxResults': INT,
                'onBehalfOfContentOwner': str,
                'pageToken': str,
                'videoId': str,
            },
        },
        'insert': {
            'method': 'POST',
            'required': {
                'part': SET('snippet', 'contentDetails', 'status'),
            },
            'optional': {
                'onBehalfOfContentOwner': str,
            },
        },
        'update': {
            'method': 'PUT',
            'required': {
                'part': SET('snippet', 'contentDetails', 'status'),
            },
        },
        'delete': {
            'method': 'DELETE',
            'required': {
                'id': str,
            },
        },
    }


class YoutubeV3(GoogleApi):
    _url = '/youtube/v3'
    _apis = {
        'playlists': Playlists,
        'playlistItems': PlaylistItems,
    }
