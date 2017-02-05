from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.apps import apps


def _get_content_type_and_obj(obj, model=None):
    if isinstance(model, str):
        model = apps.get_model(*model.split("."))

    if isinstance(obj, (int, int)):
        obj = model.objects.get(pk=obj)

    return ContentType.objects.get_for_model(type(obj)), obj


class LikeManager(models.Manager):
    """
    A Manager for Like objects
    """
    from django import VERSION
    if VERSION > (1,8):
        def get_query_set(self):
            return self.get_queryset()

    def for_user(self, user, model=None):
        """
        Returns a Like objects queryset for a given user.

        If a model params is provided, it returns only the
        liked objects of that model class

        Usage:

            Like.objects.for_user(user)
            Like.objects.for_user(user, model=Song)
            Like.objects.for_user(user, model="music.song")
        """

        qs = self.get_query_set().filter(user=user)

        if model:
            if isinstance(model, str):
                model = apps.get_model(*model.split("."))

            content_type = ContentType.objects.get_for_model(model)
            qs = qs.filter(target_content_type=content_type)

        return qs.order_by("-timestamp")

    def for_model(self, model):
        """
        Returns a Like objects queryset for a given model.
        `model` may be a django model class or an string representing
        a model in module-notation, ie: "auth.User"

        Usage:

            Like.objects.for_model(Song)
            Like.objects.for_model("music.Song")
        """

        # if model is an app_label.model string make it a Model class
        if isinstance(model, str):
            model = apps.get_model(*model.split("."))

        content_type = ContentType.objects.get_for_model(model)

        qs = self.get_query_set().filter(
            target_content_type=content_type
        )

        return qs.order_by("-timestamp")

    def for_object(self, obj, model=None):
        """
        Returns a Like objects queryset for a given object

        Usage:
            Like.objects.for_object(1, "music.Song")
            Like.objects.for_object(1, Song)

        or given a music app with a Song model:

            song = Song.objects.get(pk=1)
            Like.objects.for_object(song)
        """

        content_type, obj = _get_content_type_and_obj(obj, model)

        qs = self.get_query_set().filter(
            target_content_type=content_type,
            target_object_id=obj.pk
        )

        return qs.order_by("-timestamp")

    def get_like(self, user, obj, model=None):
        """
        Returns a Like instance if the `user` has liked
        the given object `obj`. Otherwise returns None

        Usage:
            Like.objects.get_like(user, 1, "music.Song")
            Like.objects.get_like(user, 1, Song)

        or given a music app with a Song model:

            song = Song.objects.get(pk=1)
            Like.objects.get_like(user, song)
        """

        content_type, obj = _get_content_type_and_obj(obj, model)

        try:
            return self.get_query_set().get(
                user=user,
                target_content_type=content_type,
                target_object_id=obj.id
            )
        except self.model.DoesNotExist:
            return None

    def create(self, user, obj, model=None):
        """
        Creates and returns a new Like obj for the given user and obj
        """

        content_type, content_object = _get_content_type_and_obj(obj, model)
        like = super(LikeManager, self).create(
            user=user,
            target_content_type=content_type,
            target_object_id=content_object.pk,
            target=content_object
        )

        return like
