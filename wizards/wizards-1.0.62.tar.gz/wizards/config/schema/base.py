from ea.lib.datastructures import DTO
import ea.schema


class BaseConfigSchema(ea.schema.Schema):
    dto_class = DTO

    @classmethod
    def defaults(cls):
        """Return a DTO holding the defaults for this
        schema.
        """
        schema = cls()
        params, errors = schema.load({})
        assert not errors, "Defaults must not produce errors."
        return params


