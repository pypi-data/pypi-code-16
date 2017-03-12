import ea.schema

from wizards.config.schema.base import BaseConfigSchema
from wizards.config.schema.general import GeneralSettingsSchema
from wizards.config.schema.logging import LoggingSchema
from wizards.config.schema.http import HTTPSchema
from wizards.config.schema.event import EventSchema


class ConfigSchema(BaseConfigSchema):
    """Captures the complete user-configuration for SG
    generated applications.
    """
    general = ea.schema.fields.Nested(
        nested=GeneralSettingsSchema,
        required=False,
        missing=GeneralSettingsSchema.defaults
    )

    logging = ea.schema.fields.Nested(
        nested=LoggingSchema,
        required=False,
        missing=LoggingSchema.defaults
    )

    http = ea.schema.fields.Nested(
        nested=HTTPSchema,
        required=False,
        missing=HTTPSchema.defaults
    )

    event = ea.schema.fields.Nested(
        nested=EventSchema,
        required=False,
        missing=EventSchema.defaults
    )