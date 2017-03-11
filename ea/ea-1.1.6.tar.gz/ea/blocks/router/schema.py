from ea import schema
from ea.blocks.router.criterion import Criterion
from ea.blocks.router.rule import Rule


class CriterionSchema(schema.Schema):
    attname = schema.fields.String(
        required=True,
        load_from='name'
    )

    op = schema.fields.String(
        required=True,
        validate=[
            schema.validate.OneOf(list(Criterion._matching_ops.keys()))
        ],
        load_from='operator'
    )

    value = schema.fields.Field(
        required=True
    )

    def load(self, *args, **kwargs):
        params, errors = super(CriterionSchema, self).load(*args, **kwargs)
        if errors:
            return params, errors

        return Criterion(**params), errors


class RuleSchema(schema.Schema):
    return_to_sender = schema.fields.Boolean(
        required=False,
        missing=False
    )

    destinations = schema.fields.List(
        schema.fields.Field(),
        required=True
    )

    criterions = schema.fields.List(
        schema.fields.Nested(CriterionSchema),
        required=True,
        validate=[
            schema.validate.Length(min=1)
        ]
    )

    exclude = schema.fields.List(
        schema.fields.String(),
        required=False,
        default=list,
        missing=list
    )

    def load(self, *args, **kwargs):
        params, errors = super(RuleSchema, self).load(*args, **kwargs)
        if errors:
            return params, errors

        return (Rule(**params), errors)\
            if not self.many\
            else ([Rule(**x) for x in params], errors)
