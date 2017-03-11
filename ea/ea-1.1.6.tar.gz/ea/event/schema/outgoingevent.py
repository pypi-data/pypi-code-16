import uuid

import ea.schema


class OutgoingEventHeaderSchema(ea.schema.Schema):
    protocol_version = ea.schema.fields.String(
        required=False,
        missing="1",
        default="1",
        load_from='protocol-version',
        dump_to='protocol-version',
    )
    id = ea.schema.fields.UUID(
        required=False,
        default=uuid.uuid4,
        missing=uuid.uuid4,
        load_from='event-id',
        dump_to='event-id',
    )
    type = ea.schema.fields.String(
        required=False,
        load_from='event-type',
        dump_to='event-type',
    )
    cid = ea.schema.fields.UUID(
        required=False,
        default=uuid.uuid4,
        missing=uuid.uuid4,
        load_from='event-cid',
        dump_to='event-cid',
    )
    subject_id = ea.schema.fields.UUID(
        required=False,
        load_from='event-subject-id',
        dump_to='event-subject-id',
    )
    observer = ea.schema.fields.String(
        required=False,
        load_from='event-observer',
        dump_to='event-observer',
    )
    received = ea.schema.fields.Integer(
        required=False,
        load_from='event-received',
        dump_to='event-received',
    )
    timestamp = ea.schema.fields.Integer(
        required=False,
        load_from='event-timestamp',
        dump_to='event-timestamp',
    )
    occurred = ea.schema.fields.Integer(
        required=False,
        load_from='event-occurred',
        dump_to='event-occurred',
    )
    osi_level = ea.schema.fields.Integer(
        required=False,
        load_from='event-osi-level',
        dump_to='event-osi-level',
    )
    priority = ea.schema.fields.Integer(
        required=False,
        default=0,
        missing=0,
        load_from='event-priority',
        dump_to='event-priority',
    )
    transaction_id = ea.schema.fields.UUID(
        required=False,
        missing=lambda: str(uuid.UUID(int=0)),
        default=lambda: str(uuid.UUID(int=0)),
        load_from='event-transaction-id',
        dump_to='event-transaction-id',
    )
