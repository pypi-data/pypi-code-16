from commonconf.exceptions import NotConfigured


class ConfProxy(object):
    backend = None
    overrides = {}

    @classmethod
    def set_overrides(cls, overrides):
        ConfProxy.overrides = overrides

    @classmethod
    def clear_overrides(cls):
        ConfProxy.overrides = {}

    def __getattr__(self, key):
        if key in ConfProxy.overrides:
            return ConfProxy.overrides[key]

        backend = self.get_backend()

        return backend.get(key)

    def get_backend(self):
        if not ConfProxy.backend:
            try:
                guess_backend()
            except:
                raise NotConfigured("Must configure a commonconf backend")

        return ConfProxy.backend


def guess_backend():
    from django.conf import settings
    from commonconf.backends import use_django_backend
    use_django_backend()
