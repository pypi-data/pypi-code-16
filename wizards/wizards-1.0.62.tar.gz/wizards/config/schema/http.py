import ea.schema

from wizards.config.schema.base import BaseConfigSchema


class HTTPSchema(BaseConfigSchema):
    """Contains settings for the HTTP interface of SG generated
    applications.
    """
    enabled = ea.schema.fields.Boolean(
        required=False,
        missing=True
    )
    workers = ea.schema.fields.Integer(
        required=False,
        missing=1
    )
    bind = ea.schema.fields.String(
        required=False,
        missing="0.0.0.0:8000"
    )
    user = ea.schema.fields.String(
        required=False,
        missing='nobody'
    )
    nogroup = ea.schema.fields.String(
        required=False,
        missing='nogroup'
    )