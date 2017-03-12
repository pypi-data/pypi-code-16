import ea.schema

from wizards.config.schema.base import BaseConfigSchema



class EventPublisherSchema(BaseConfigSchema):
    """Configures settings related to the event publisher."""
    channels = ea.schema.fields.List(
        ea.schema.fields.String,
        required=False,
        missing=list
    )



class EventSchema(BaseConfigSchema):
    """Configures settings related to the receiving and publishing
    of event messages by SG applications.
    """
    publisher = ea.schema.fields.Nested(
        nested=EventPublisherSchema,
        required=False,
        missing=EventPublisherSchema.defaults
    )
