import uuid

from ea.lib.datastructures import ImmutableDTO
import ea.schema


class CommandStorageSchema(ea.schema.Schema):
    dto_class = ImmutableDTO

    id = ea.schema.fields.UUID(
        required=True
    )
    name = ea.schema.fields.String(
        required=True
    )
    sid = ea.schema.fields.UUID(
        required=True,
        load_from='subject'
    )

    cid = ea.schema.fields.UUID(
        required=True
    )

    tid = ea.schema.fields.UUID(
        required=True,
        missing=uuid.UUID(int=0),
        default=uuid.UUID(int=0)
    )

    issued = ea.schema.fields.Integer(
        required=True
    )

    #expires = ea.schema.fields.Integer(
    #    required=False,
    #    allow_none=False,
    #    missing=0,
    #    default=0
    #)
