from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db.models import Model
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
try:
    from django.utils.module_loading import import_string as importer
except ImportError:
    from django.utils.module_loading import import_by_path as importer
from django.conf import settings

# Ensure request context processor is active. Handle all styles of the setting.
try:
    tcp = settings.TEMPLATES[0]["OPTIONS"]["context_processors"]
except (AttributeError, KeyError):
    try:
        tcp = settings.TEMPLATE_CONTEXT_PROCESSORS
    except AttributeError:
        tcp = []

if ("django.core.context_processors.request" not in tcp) \
    and ("django.template.context_processors.request" not in tcp):
    raise RuntimeError(
        "django.template.context_processors.request is required"
    )

import ultracache.monkey


try:
    purger = importer(settings.ULTRACACHE["purge"]["method"])
except (AttributeError, KeyError):
    purger = None


try:
    invalidate = settings.ULTRACACHE["invalidate"]
except (AttributeError, KeyError):
    invalidate = True


@receiver(post_save)
def on_post_save(sender, **kwargs):
    """Expire ultracache cache keys affected by this object
    """
    if not invalidate:
        return
    if kwargs.get("raw", False):
        return
    if issubclass(sender, Model):
        obj = kwargs["instance"]
        if isinstance(obj, Model):
            # get_for_model itself is cached
            try:
                ct = ContentType.objects.get_for_model(sender)
            except RuntimeError:
                # This happens when ultracache is being used by another product
                # during a test run.
                return

            if kwargs.get("created", False):
                # Expire cache keys that contain objects of this content type
                key = "ucache-ct-%s" % ct.id
                to_delete = cache.get(key, [])
                if to_delete:
                    try:
                        cache.delete_many(to_delete)
                    except NotImplementedError:
                        for k in to_delete:
                            cache.delete(k)
                cache.delete(key)

                # Purge paths in reverse caching proxy that contain objects of
                # this content type.
                key = "ucache-ct-pth-%s" % ct.id
                if purger is not None:
                    for path in cache.get(key, []):
                        purger(path)
                cache.delete(key)

            else:
                # Expire cache keys
                key = "ucache-%s-%s" % (ct.id, obj.pk)
                to_delete = cache.get(key, [])
                if to_delete:
                    try:
                        cache.delete_many(to_delete)
                    except NotImplementedError:
                        for k in to_delete:
                            cache.delete(k)
                cache.delete(key)

                # Purge paths in reverse caching proxy
                key = "ucache-pth-%s-%s" % (ct.id, obj.pk)
                if purger is not None:
                    for path in cache.get(key, []):
                        purger(path)
                cache.delete(key)


@receiver(post_delete)
def on_post_delete(sender, **kwargs):
    """Expire ultracache cache keys affected by this object
    """
    if not invalidate:
        return
    if issubclass(sender, Model):
        obj = kwargs["instance"]
        if isinstance(obj, Model):
            # get_for_model itself is cached
            try:
                ct = ContentType.objects.get_for_model(sender)
            except RuntimeError:
                # This happens when ultracache is being used by another product
                # during a test run.
                return

            # Expire cache keys
            key = "ucache-%s-%s" % (ct.id, obj.pk)
            to_delete = cache.get(key, [])
            if to_delete:
                try:
                    cache.delete_many(to_delete)
                except NotImplementedError:
                    for k in to_delete:
                        cache.delete(k)
            cache.delete(key)

            # Invalidate paths in reverse caching proxy
            key = "ucache-pth-%s-%s" % (ct.id, obj.pk)
            if purger is not None:
                for path in cache.get(key, []):
                    purger(path)
            cache.delete(key)
