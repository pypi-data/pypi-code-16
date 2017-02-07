from yams.buildobjs import EntityType, Bytes, RelationDefinition


class Photo(EntityType):
    data = Bytes(required=True)


class Thumbnail(EntityType):
    data = Bytes(required=True)


class thumbnail(RelationDefinition):
    subject = 'Photo'
    object = 'Thumbnail'
    cardinality = '?1'
    composite = 'subject'


class picture(RelationDefinition):
    subject = 'CWUser'
    object = 'Photo'
    cardinality = '*?'
    composite = 'subject'


class EmailAlias(EntityType):
    pass


class use_email(RelationDefinition):
    subject = 'CWUser'
    object = 'EmailAlias'
    cardinality = '*1'
    composite = 'subject'
