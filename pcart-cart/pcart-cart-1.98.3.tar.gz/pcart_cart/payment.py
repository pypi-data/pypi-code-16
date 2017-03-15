from django.utils.translation import ugettext_lazy as _


class BasePayment:
    title = None

    def __init__(self, config={}):
        self.title = config.get('title', self.title)

    def get_title(self):
        return self.title


class SimplePayment(BasePayment):
    title = _('Simple payment method')
