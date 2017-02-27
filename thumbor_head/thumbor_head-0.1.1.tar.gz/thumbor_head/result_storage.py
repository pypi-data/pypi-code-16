from tornado import (
    httpclient
)


from thumbor.result_storages.file_storage import (
    Storage
)

from thumbor.config import (
    Config
)


class Storage(Storage):
    def __init__(self, context):
        super(Storage, self).__init__(
            context
        )

        self.client = httpclient.HTTPClient()

    def _request(self, u, m="HEAD", h=None, b=None):
        request = httpclient.HTTPRequest(
            url=u,
            method=m,
            headers=h,
            body=b,
            connect_timeout=self.context.config.HTTP_LOADER_CONNECT_TIMEOUT,
            request_timeout=self.context.config.HTTP_LOADER_REQUEST_TIMEOUT,
            follow_redirects=self.context.config.HTTP_LOADER_FOLLOW_REDIRECTS,
            max_redirects=self.context.config.HTTP_LOADER_MAX_REDIRECTS
        )

        return request


    def is_expired(self, path):
        request = self._request(
            self.context.request.image_url
        )

        try:
            if self.client.fetch(request).code in (200, 302, 304):
                return super(Storage, self).is_expired(
                    path
                )

        except httpclient.HTTPError as e:
            return True
