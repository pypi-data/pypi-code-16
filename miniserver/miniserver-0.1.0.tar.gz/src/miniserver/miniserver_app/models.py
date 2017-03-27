from miniserver.models import MODEL_REGISTRY, REGISTERED_MODELS
from miniserver.models import create_django_model

models_ns = globals()
DJANGO_MODELS_REGISTRY = {}


for model in MODEL_REGISTRY:
    if model not in REGISTERED_MODELS:
        models_ns[model.__name__] = dj_model = create_django_model(model)
        REGISTERED_MODELS.append(model)
        DJANGO_MODELS_REGISTRY[model] = dj_model