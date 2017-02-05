from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest

from .models import Like


@login_required
def add_or_remove(request):

    if not request.is_ajax():
        return HttpResponseNotAllowed()

    user = request.user

    try:
        app_model = request.POST["target_model"]
        obj_id = int(request.POST["target_object_id"])
    except (KeyError, ValueError):
        return HttpResponseBadRequest()

    like = Like.objects.get_like(user, obj_id, model=app_model)

    if like is None:
        Like.objects.create(user, obj_id, app_model)
        status = 'added'
    else:
        like.delete()
        status = 'deleted'

    likeCount=Like.objects.for_object(obj_id, app_model).count()
    
    return HttpResponse(status+"|"+str(likeCount))

