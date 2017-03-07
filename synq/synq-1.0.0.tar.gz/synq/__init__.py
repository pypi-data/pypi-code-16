#!/usr/bin/env python

"""Python client library for the SYNQ API

SYNQ-Python is a client library that wraps the SYNQ API.

For more information, see:

https://www.synq.fm/docs/

"""

import json
import re
import pprint
import requests

#Default base url for the SYNQ HTTP API
VIDEO_API_URL = "https://api.synq.fm/v1/video"

UUID_REGEX = re.compile(r"^[0-9a-f]{32}$")

PRETTY_PRINTER = pprint.PrettyPrinter(indent=4)

class ArgumentTypeWrongError(Exception):
    pass

class ArgumentContentWrongError(Exception):
    pass

class ArgumentMissingError(Exception):
    pass

class SynqApiError(Exception):
    pass



class VideoAPI(object):

    def __init__(self, api_key, host=None):
        if not isinstance(api_key, str):
            raise ArgumentTypeWrongError('Wrong type for argument "api_key". expected "{1}", got "{2}"'.format(str, type(api_key)))
        elif not UUID_REGEX.match(api_key):
            raise ArgumentContentWrongError('argument "api_key" is in an invalid format')
        self.__api_key = api_key
        if host is None:
            self.host = VIDEO_API_URL
        else:
            self.host = host

    def __post(self, endpoint, args, required, optional):
        data = {'api_key':self.__api_key}
        url = self.host + endpoint

        # make sure required arguments are supplied
        # and that the arguments have the correct format
        for item in required + optional:

            item_name = item[0]
            item_type = item[1]

            if item_name in args:

                item_value = args[item_name]

                if item_type == 'string':
                    if not isinstance(item_value, str):
                        raise ArgumentTypeWrongError('Wrong type for argument "{0}". expected "{1}", got "{2}"'.format(item_name, str, type(item_value)))

                elif item_type == 'uuid':
                    if not isinstance(item_value, str):
                        raise ArgumentTypeWrongError('Wrong type for argument "{0}". expected "{1}", got "{2}"'.format(item_name, str, type(item_value)))
                    elif not UUID_REGEX.match(item_value):
                        raise ArgumentContentWrongError('argument "{0}" is in an invalid format'.format(item_name))

                elif item_type == 'json':
                    if not isinstance(item_value, dict):
                        raise ArgumentTypeWrongError('Wrong type for argument "{0}". expected "{1}", got "{2}"'.format(item_name, dict, type(item_value)))
                    try:
                        item_value = json.dumps(item_value)
                    except Exception:
                        raise ArgumentContentWrongError('argument "{0}" is not JSON serializable'.format(item_name))

                data[item_name] = item_value

            elif item in required:
                raise ArgumentMissingError('Missing required argument "{0}"'.format(item_name))

        request = requests.post(url, data=data)
        if request.status_code == 400:
            raise SynqApiError('SYNQ API error object:\n{0}'.format(PRETTY_PRINTER.pformat(request.json())))
        else:
            request.raise_for_status()

        return request.json()

    def create(self, userdata=None):
        """
        Create a new video object, optionally setting some userdata fields
        """
        endpoint = '/create'
        args = {}
        if not userdata is None:
            args['userdata'] = userdata
        required = []
        optional = [['userdata', 'json']]
        return self.__post(endpoint, args, required, optional)

    def details(self, video_id):
        """
        Return details about one video
        """
        endpoint = '/details'
        args = {'video_id': video_id}
        required = [['video_id', 'uuid']]
        optional = []
        return self.__post(endpoint, args, required, optional)

    def query(self, filter):
        """
        Perform a JavaScript query to return video objects matching any desired criteria
        """
        endpoint = '/query'
        args = {'filter': filter}
        required = [['filter', 'string']]
        optional = []
        return self.__post(endpoint, args, required, optional)

    def update(self, video_id, source):
        """
        Update a video's metadata through JavaScript code.
        """
        endpoint = '/update'
        args = {'video_id': video_id, 'source': source}
        required = [['video_id', 'uuid'], ['source', 'string']]
        optional = []
        return self.__post(endpoint, args, required, optional)

    def upload(self, video_id=None):
        """
        Get parameters needed for uploading a video file
        """
        endpoint = '/upload'

        if video_id is None:
            video_id = self.create()["video_id"]

        args = {'video_id': video_id}

        required = [['video_id', 'uuid']]
        optional = []
        return self.__post(endpoint, args, required, optional)

    def uploader(self, video_id=None, timeout=None):
        """
        Return embeddable url to an uploader widget.
        """
        endpoint = '/uploader'

        if video_id is None:
            video_id = self.create()["video_id"]

        args = {'video_id': video_id}
        if not timeout is None:
            args['timeout'] = timeout

        required = [['video_id', 'uuid']]
        optional = [['timeout', 'string']]
        return self.__post(endpoint, args, required, optional)

    def query_simple(self, key, value):
        """
        Perform a query that returns every video with a desired value in a key.
        """
        try:
            value = json.dumps(value)
        except Exception:
            raise ArgumentContentWrongError('argument "{0}" is not JSON serializable'.format("value"))

        query_string = "return (_.isEqual(_.get(video,'{0}'),{1})) ? video : undefined;".format(key, value)
        return self.query(query_string)
