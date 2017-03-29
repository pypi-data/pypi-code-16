from voluptuous import Any, Schema
from . import ModelApiResource

_subscription_deserialize = Schema({
    'id': Any(None, str, unicode),
    'model_id': Any(str, unicode),
    'event': Any(str, unicode),
    'subscriber_email': Any(str, unicode),
    'options': dict
})

_subscription_serialize = Schema({
    'id': Any(None, str, unicode),
    'model_id': Any(str, unicode),
    'event': Any(str, unicode),
    'subscriber_email': Any(str, unicode),
    'options': dict
})


class Subscription(ModelApiResource):

    _path = '/models/{model_id}/subscriptions'

    _deserialize = _subscription_deserialize

    _serialize = _subscription_serialize

    _args = Schema({
        'event': Any(str, unicode)
    })

    @classmethod
    def find(cls, id_=None, **kwargs):
        if id_ is not None:
            return _SubscriptionById.find(id_)
        return super(Subscription, cls).find(**kwargs)


class _SubscriptionById(ModelApiResource):

    _path = '/subscriptions'

    _deserialize = _subscription_deserialize

    _serialize = _subscription_serialize
