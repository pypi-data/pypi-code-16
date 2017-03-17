import json

from django.apps import apps
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def update(request):
    if "data" not in request.POST:
        return HttpResponseBadRequest()
    if "HTTP_AUTHORIZATION" not in request.META:
        return HttpResponseForbidden()

    auth = request.META["HTTP_AUTHORIZATION"]
    required_auth = "Bearer {}".format(settings.GLOSSARY_SERVICE_TOKEN)
    if auth != required_auth:
        return JsonResponse({"error": "Неверный токен"}, status=403)

    data = json.loads(request.POST["data"])
    models = apps.get_app_config("glossary").get_models()
    models = sorted(models, key=lambda m: m.get_foreign_key_count())
    for model in models:
        records = data[model._meta.model_name]
        for record in records:
            uuid = record["uuid"]
            try:
                obj_data = model.clean_dump_data(record)

                try:
                    model.all_objects.get(uuid=uuid)
                    model.all_objects.filter(uuid=uuid).update(**obj_data)
                except model.DoesNotExist:
                    model.all_objects.create(**obj_data)
            except BaseException as e:
                return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse()
