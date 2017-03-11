from ea.cqrs.command.command.options import CommandOptions
import ea.schema


class CommandMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(CommandMeta, cls).__new__
        if name in ('NewBase', 'Command'):
            return super_new(cls, name, bases, attrs)

        declared_meta = attrs.pop('Meta', None)
        meta = CommandOptions(declared_meta, name)

        # Loop over all fields and add them to the options
        # instance. This is used to perform various logical
        # operations related to validation, ordering, comparison,
        # etc.
        fields = []
        for attname in list(attrs.keys()):
            is_field = issubclass(type(attrs[attname]), ea.schema.fields.Field)
            if not is_field:
                continue
            fields.append([attname, attrs.pop(attname)])

        meta.add_fields(sorted(fields, key=lambda x: x[1]._creation_index))

        new_class = super_new(cls, name, bases, attrs)
        meta.contribute_to_class('meta', new_class)

        return new_class
