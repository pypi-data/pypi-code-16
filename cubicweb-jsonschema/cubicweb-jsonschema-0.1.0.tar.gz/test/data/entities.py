from jsl.fields import NumberField

from cubicweb.predicates import match_kwargs

from cubicweb_jsonschema.entities.mappers import ETypeMapper


class PhotoETypeMapper(ETypeMapper):
    __select__ = ETypeMapper.__select__ & match_kwargs({'etype': 'Photo'})
    fields = (
        ('data', {'required': False}),
        ('latitude', NumberField(required=True)),
        ('longitude', NumberField()),
    )
