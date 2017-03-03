import json

from werkzeug.exceptions import UnsupportedMediaType
from werkzeug.utils import cached_property
from werkzeug.wrappers import AcceptMixin
from werkzeug.wrappers import BaseRequest
from werkzeug.wrappers import CommonRequestDescriptorsMixin


class Request(BaseRequest, AcceptMixin, CommonRequestDescriptorsMixin):

    @cached_property
    def json(self):
        try:
            # JSON is always in UTF-8
            return json.loads(self.get_data().decode('utf-8'))
        except ValueError:
            raise UnsupportedMediaType

    def is_valid_content_type(self, content_types):
        """Return a boolean indicating if any of the given list
        of strings `content_types` is accepted by the client.
        """
        return any([x in self.accept_mimetypes for x in content_types])
