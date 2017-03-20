import asyncio
import websockets
import json
import urllib
import os
import base64
from watson_developer_cloud import SpeechToTextV1


class WSSpeechToTextV1(SpeechToTextV1):
    def recognize(self, file_name=None,
                  file_object=None,
                  content_type=None,
                  content_callback=None,
                  event_loop=None,
                  model=None,
                  customization_id=None,
                  inactivity_timeout=None,
                  keywords=None,
                  keywords_threshold=None,
                  max_alternatives=None,
                  word_alternatives_threshold=None,
                  word_confidence=None,
                  timestamps=None,
                  profanity_filter=None,
                  smart_formatting=None,
                  speaker_labels=None):
        """
        Returns the recognized text from the audio input
        The final transcript is returned by this method.

        Specify either a file name to open and send, or a file-like object.

        One of the parameters,  content_callback is a callable
        that takes an argument.  This callable is called asynchronously
        whenever a websocket message is recieved with an updated transcript.
        """

        if event_loop is None:
            event_loop = asyncio.get_event_loop()

        if model is None:
            model = 'en-US_BroadbandModel'

        authstring = "{0}:{1}".format(self.username, self.password)
        encoded_auth = base64.b64encode(authstring.encode('utf-8')).decode('utf-8')

        headers = {'Authorization': 'Basic {0}'.format(encoded_auth)}

        unfiltered_options = {
            'content_type': content_type,
            'inactivity_timeout': inactivity_timeout,
            'interim_results': True,
            'inactivity_timeout': inactivity_timeout,
            'word_confidence': word_confidence,
            'timestamps': timestamps,
            'max_alternatives': max_alternatives,
            'word_alternatives_threshold': word_alternatives_threshold,
            'profanity_filter': profanity_filter,
            'smart_formatting': smart_formatting,
            'keywords': keywords,
            'keywords_threshold': keywords_threshold,
            'max_alternatives': max_alternatives,
            'speaker_labels': speaker_labels}

        options = dict([(k, unfiltered_options[k])
                        for k
                        in unfiltered_options.keys()
                        if unfiltered_options[k] is not None])
        if file_object is None:
            with open(file_name, 'rb') as audiofile:
                return event_loop.run_until_complete(
                    self._convert(audiofile,
                                  headers,
                                  options,
                                  model,
                                  content_callback))
        else:
            return event_loop.run_until_complete(
                self._convert(file_object,
                              headers,
                              options,
                              model,
                              content_callback))

    async def _send_fileobj(self, fileobj, wsocket):
        while True:
            buffer = fileobj.read(1024)
            if not buffer:
                wsocket.send(json.dumps({'action': 'stop'}))
                break
            await wsocket.send(buffer)

    async def _convert(self, fileobj, headers, options, model, callback):
        parsed_url = urllib.parse.urlparse(self.url)
        url = "wss://{0}{1}/v1/recognize?model={2}".format(parsed_url.netloc,
                                                           parsed_url.path,
                                                           model)
        async with websockets.connect(url, extra_headers=headers) as websocket:
            send_res = await websocket.send(json.dumps(options))
            resp = await websocket.recv()
            asyncio.ensure_future(self._send_fileobj(fileobj, websocket))
            while True:
                resp = await websocket.recv()
                parsed_resp = json.loads(resp)
                if callback is not None:
                    callback(parsed_resp)
                if 'results' in parsed_resp:
                    if len(parsed_resp['results']) > 0:
                        if 'final' in parsed_resp['results'][0]:
                            if parsed_resp['results'][0]['final']:
                                websocket.close()
                                return parsed_resp