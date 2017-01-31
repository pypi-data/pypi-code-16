from .repository import DjangoStoredEventRepository
from .unifiedtranscoder import UnifiedTranscoder
from django.core.serializers.json import DjangoJSONEncoder
from eventsourcing.application.base import EventSourcingApplication
from eventsourcing.infrastructure.event_sourced_repo import EventSourcedRepository


class EventSourcingWithDjango(EventSourcingApplication):
    def __init__(self, **kwargs):
        kwargs.setdefault('json_encoder_cls', DjangoJSONEncoder)
        super().__init__(**kwargs)
        self.on_init()

    def on_init(self):
        """
        Override at subclass. For example, initialize repositories that this
        app would use.
        """

    def create_stored_event_repo(self, **kwargs):
        return DjangoStoredEventRepository(**kwargs)

    def create_transcoder(self, always_encrypt, cipher, json_decoder_cls, json_encoder_cls):
        return UnifiedTranscoder(json_encoder_cls=json_encoder_cls)

    def get_repo_for_entity(self, entity_cls):
        """
        Returns EventSourcedRepository class for given entity.
        """
        clsname = '%sRepository' % entity_cls.__name__
        repo_cls = type(clsname, (EventSourcedRepository,), {'domain_class': entity_cls})
        return repo_cls(event_store=self.event_store)
