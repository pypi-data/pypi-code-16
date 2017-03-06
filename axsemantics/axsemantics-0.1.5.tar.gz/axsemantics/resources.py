from axsemantics import constants
from axsemantics.base import (
    APIResource,
    ListResource,
)
from axsemantics.mixins import(
    ContentGenerationMixin,
    CreateableMixin,
    DeleteableMixin,
    ListableMixin,
    RincewindMixin,
    UpdateableMixin,
)
from axsemantics.net import RequestHandler
from axsemantics.utils import create_object

import datetime
import json
import requests
import time
# import websocket


class ThingList(ListResource):
    class_name = 'thing'

    def __init__(self, cp_id, *args, **kwargs):
        self.cp_id = cp_id
        super(ThingList, self).__init__(*args, **kwargs)

    def __next__(self):
        if self.current_index >= len(self.current_list):
            if self.next_page:
                self._update()
            else:
                raise StopIteration
        self.current_index += 1
        return create_object(
            self.current_list[self.current_index - 1],
            api_token=self.api_token,
            _type=ThingList.class_name,
            cp_id=self.cp_id,
        )


class Thing(CreateableMixin, UpdateableMixin, DeleteableMixin, ListableMixin, ContentGenerationMixin, APIResource):
    class_name = 'thing'
    required_fields = ['uid', 'name', 'content_project']
    list_class = ThingList

    def __init__(self, cp_id=None, **kwargs):
        super(Thing, self).__init__(**kwargs)
        self['content_project'] = cp_id

    def instance_url(self):
        url = '/{}/content-project/{}/thing/'.format(
            constants.API_VERSION,
            self['content_project'],
        )
        if self['id']:
            url += '{}/'.format(self['id'])
        return url


class ContentProject(CreateableMixin, DeleteableMixin, ListableMixin, ContentGenerationMixin, APIResource):
    class_name = 'content-project'
    required_fields = ['name', 'engine_configuration']

    def __init__(self, api_token=None, **kwargs):
        super(ContentProject, self).__init__(api_token=api_token, **kwargs)

    def things(self):
        if self['id']:
            thing_url = '{}thing/'.format(self.instance_url())
            return ThingList(
                cp_id=self['id'],
                api_token=self.api_token,
                class_name=self.class_name,
                initial_url=thing_url,
            )


class ContentProjectList(ListResource):
    initial_url = ContentProject.class_url()
    class_name = 'content-project'

    def __init__(self, api_token=None):
        super(ContentProjectList, self).__init__(
            class_name=self.class_name,
            api_token=api_token,
            initial_url='/v1/content-project/',
        )


class Training(RincewindMixin, APIResource):
    class_name = 'training'

    @classmethod
    def class_url(cls):
        return '/{}/{}s/'.format(constants.API_VERSION, cls.class_name)

    @property
    def promoted(self):
        requestor = RequestHandler(token=self.api_token, api_base=self.api_base)
        url = '{}get-promoted/'.format(self.instance_url())
        return requestor.request('get', url, None)

    @classmethod
    def import_atml3(self, data, api_base=None, api_token=None):
        api_base = api_base or constants.API_BASE_RINCEWIND
        api_token = api_token or constants.API_TOKEN_RINCEWIND
        requestor = RequestHandler(token=api_token, api_base=api_base)
        url = '{}import/'.format(self.class_url())
        return requestor.request('post', url, data)

    def update_atml3(self, data):
        requestor = RequestHandler(token=self.api_token, api_base=self.api_base)
        url = '{}import/'.format(self.instance_url())
        return requestor.request('put', url, data)

    def _get_promoted(self, output=None):
        """
        this is an internal endpoint, not intended for customer use
        """
        requestor = RequestHandler(token=self.api_token, api_base=self.api_base)
        url = '{}get-promoted/'.format(self.instance_url())
        if output and hasattr(output, 'write') and callable(output.write):
            # print(self.instance_url())
            requestor.download_with_progressbar(url, label='Download Training')
        else:
            return requestor.request('get', url, None)

    def export_atml3(self):
        url = '{}download_export/'.format(self.instance_url())
        # ws_url = '{}/ws/trainings/'.format(self.ws_base)
        # if self.get('id', None):
        #     id = self['id']
        #     ws_url = '{}{}/'.format(ws_url, requests.utils.quote(str(id)))

        # print(ws_url)
        requestor = RequestHandler(token=self.api_token, api_base=self.api_base)
        start = datetime.datetime.utcnow()
        # ws = websocket.create_connection(ws_url)

        requestor.request('post', url, None)
        while True:
            time.sleep(0.5)
            self.refresh()
            current = self.get('lastExportProcessed', None)
            if current is None:
                continue
            dt = datetime.datetime.strptime(current, "%Y-%m-%dT%H:%M:%S.%fZ")
            if start < dt:
                break
        # ws.close()
        export = requestor.request('get', url, None, parse_json=False)
        return export


class TrainingList(RincewindMixin, ListResource):
    initial_url = Training.class_url()
    class_name = 'training'

    def __init__(self, api_token=None):
        super(TrainingList, self).__init__(
            class_name=self.class_name,
            api_token=api_token,
            initial_url=self.initial_url,
        )
