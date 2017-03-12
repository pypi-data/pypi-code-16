import ea.schema

from wizards.config.schema.base import BaseConfigSchema


class LoggingSchema(BaseConfigSchema):
    """Specifies the general logging settings for SG generated
    applications.
    """
    level = ea.schema.fields.String(
        required=False,
        missing='INFO',
        validate=ea.schema.validate.OneOf(['DEBUG','INFO','WARNING',
            'CRITICAL','EXCEPTION'])
    )