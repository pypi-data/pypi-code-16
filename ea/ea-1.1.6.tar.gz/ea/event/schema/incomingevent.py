import ea.schema


class IncomingEventHeaderSchema(ea.schema.Schema):
    protocol_version = ea.schema.fields.String(
        required=True,
        load_from='protocol-version',
        dump_to='protocol-version',
    )

    id = ea.schema.fields.UUID(
        required=True,
        load_from='event-id',
        dump_to='event-id',
    )

    occurred = ea.schema.fields.Integer(
        required=True,
        load_from='event-occurred',
        dump_to='event-occurred',
    )

    type = ea.schema.fields.String(
        required=True,
        load_from='event-type',
        dump_to='event-type',
    )

    observer = ea.schema.fields.String(
        required=True,
        load_from='event-observer',
        dump_to='event-observer',
    )

    priority = ea.schema.fields.Integer(
        required=True,
        load_from='event-priority',
        dump_to='event-priority',
    )

    cid = ea.schema.fields.UUID(
        required=True,
        load_from='event-cid',
        dump_to='event-cid',
    )

    # Non-mandatory fields
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

    osi_level = ea.schema.fields.Integer(
        required=False,
        load_from='event-osi-level',
        dump_to='event-osi-level',
    )

    subject_id = ea.schema.fields.UUID(
        required=False,
        load_from='event-subject-id',
        dump_to='event-subject-id',
    )

    transaction_id = ea.schema.fields.UUID(
        required=False,
        load_from='event-transaction-id',
        dump_to='event-transaction-id',
    )
