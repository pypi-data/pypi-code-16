from sulfur import check_url, check_ok, check_2xx, check_3xx, check_4xx, \
    check_404, check_5xx


class URLCheckerClientMixin:
    """
    A class oriented interface to urlchecker.

    The URLCheckerClient object reuses the client object passed to contructor.
    """

    def _call_function(self, func, *args, **kwargs):
        kwargs['client'] = self
        return func(*args, **kwargs)

    def check_url(self, *args, **kwargs):
        """
        Accepts the same arguments as :method:`check_url`.
        """
        return self._call_function(check_url, *args, **kwargs)

    def check_ok(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is either in the
        2xx or in the 3xx range.
        """
        return self._call_function(check_ok, *args, **kwargs)

    def check_2xx(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is in the 2xx
        range.
        """
        return self._call_function(check_2xx, *args, **kwargs)

    def check_3xx(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is in the 3xx
        range.
        """
        return self._call_function(check_3xx, *args, **kwargs)

    def check_4xx(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is in the 4xx
        range.
        """
        return self._call_function(check_4xx, *args, **kwargs)

    def check_404(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is 404.
        """
        return self._call_function(check_404, *args, **kwargs)

    def check_5xx(self, url, *args, **kwargs):
        """
        Like :method:`check_url`, but checks if response code is in the 5xx
        range.
        """
        return self._call_function(check_5xx, *args, **kwargs)

    # Aliases
    def check_success(self, url, *args, **kwargs):
        """
        Alias to :method:`check_2xx`.
        """
        return self.check_2xx(url, *args, **kwargs)

    def check_redirect(self, url, *args, **kwargs):
        """
        Alias to :method:`check_3xx`.
        """
        return self.check_3xx(url, *args, **kwargs)

    def check_client_error(self, url, *args, **kwargs):
        """
        Alias to :method:`check_4xx`.
        """
        return self.check_4xx(url, *args, **kwargs)

    def check_server_error(self, url, *args, **kwargs):
        """
        Alias to :method:`check_5xx`.
        """
        return self.check_5xx(url, *args, **kwargs)
