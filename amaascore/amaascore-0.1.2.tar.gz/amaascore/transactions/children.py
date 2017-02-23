from decimal import Decimal

from amaascore.core.amaas_model import AMaaSModel


class Charge(AMaaSModel):

    def __init__(self, charge_value, currency, active=True, net_affecting=True, version=1, *args, **kwargs):
        self.charge_value = charge_value
        self.currency = currency
        self.active = active
        self.net_affecting = net_affecting
        self.version = version
        super(Charge, self).__init__(*args, **kwargs)

    @property
    def charge_value(self):
        return self._charge_value

    @charge_value.setter
    def charge_value(self, value):
        """
        Force the charge_value to always be a decimal
        :param value:
        :return:
        """
        self._charge_value = Decimal(value)


class Code(AMaaSModel):

    def __init__(self, code_value, active=True, version=1, *args, **kwargs):
        self.code_value = code_value
        self.active = active
        self.version = version
        super(Code, self).__init__(*args, **kwargs)


class Comment(AMaaSModel):

    def __init__(self, comment_value, active=True, version=1, *args, **kwargs):
        self.comment_value = comment_value
        self.active = active
        self.version = version
        super(Comment, self).__init__(*args, **kwargs)


class Link(AMaaSModel):

    def __init__(self, linked_transaction_id, active=True, version=1, *args, **kwargs):
        self.linked_transaction_id = linked_transaction_id
        self.active = active
        self.version = version
        super(Link, self).__init__(*args, **kwargs)


class Party(AMaaSModel):

    def __init__(self, party_id, active=True, version=1, *args, **kwargs):
        self.party_id = party_id
        self.active = active
        self.version = version
        super(Party, self).__init__(*args, **kwargs)
