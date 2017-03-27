from django.db import models

MODEL_REGISTRY = []
REGISTERED_MODELS = []


class ModelMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        try:
            if cls is not Model:
                MODEL_REGISTRY.append(cls)
        except NameError:
            pass


class Model(metaclass=ModelMeta):
    """
    Represents an element in the database.
    """


class field(property):
    index = 0

    def __init__(self, cls, **kwargs):
        self.type = cls
        self.index = field.index + 1
        field.index = self.index
        self.kwargs = kwargs


def create_django_model(model):
    # Prepare type parameters
    name = model.__name__
    bases = tuple(base for base in model.__bases__ if base is not Model)
    bases += (models.Model,)
    namespace = dict(vars(model))

    # Populate namespace with fields
    fields = [(k, v) for k, v in vars(model).items() if isinstance(v, field)]
    fields.sort(key=lambda x: x[1].index)
    for field_name, field_object in fields:
        namespace[field_name] = field_to_django(field_object)

    namespace['__module__'] = 'miniserver.miniserver_app.models'
    return type(name, bases, namespace)


def field_to_django(field):
    if field.type is str:
        return models.CharField(max_length=200)
    elif field.type is int:
        return models.IntegerField()
    else:
        raise ValueError('invalid field type: %r' % field)
