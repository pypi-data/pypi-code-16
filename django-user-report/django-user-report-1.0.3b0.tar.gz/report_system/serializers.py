from report_system.conf import settings
from django.db import models
from rest_framework import serializers
from rest_framework.fields import empty

from report_system.models import Ticket, TicketType
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape
from django_comments import get_model as get_comment_model
# DEFAULT_REPORT_SLUG_MODEL_MAPPINGS = {
#     'user': 'customuser.myuser',
#     'comment': str(get_comment_model()._meta),
# }


class CreateTicketSerializer(serializers.ModelSerializer):
    types = serializers.ListField(write_only=True, child=serializers.IntegerField())
    comment = serializers.CharField(write_only=True, required=False, max_length=settings.REPORT_COMMENT_MAX_LENGTH)
    version = serializers.CharField(write_only=True, required=False, max_length=50)
    content_type = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        self.target_object = None
        super(CreateTicketSerializer, self).__init__(instance=instance, data=data, **kwargs)

    class Meta:
        model = Ticket
        fields = ('content_type', 'object_pk', 'comment', 'version', 'types')

    def validate_types(self, value):
        ticket_type = TicketType.objects.filter(pk__in=value)
        if not ticket_type:
            raise serializers.ValidationError("The type id does not exist.")
        return ticket_type

    def validate(self, data):
        content_type = data['content_type']
        object_pk = data['object_pk']

        if content_type in dict(settings.REPORT_SLUG_MODEL_MAPPINGS):
            content_type = dict(settings.REPORT_SLUG_MODEL_MAPPINGS)[content_type]
            app_label = content_type.split(".", 1)[0]
            model_name = content_type.split(".", 1)[1]
            data['content_type'] = ContentType.objects.get(app_label=app_label, model=model_name)
        else:
            raise serializers.ValidationError("The given content-type %s does not resolve to a valid model."
                                              % content_type)
        try:
            object_pk = int(object_pk)
            # model = models.get_model(*content_type.split(".", 1))
            # target = model._default_manage.get(pk=object_pk)
            target = data['content_type'].get_object_for_this_type(pk=object_pk)
        except ValueError:
            raise serializers.ValidationError("Invalid object id value: {0}".format(escape(object_pk)))
        except ObjectDoesNotExist:
            raise serializers.ValidationError("No object matching content-type %s with id %s exists." % (
                escape(data['content_type']), escape(object_pk)
            ))
        data['site_id'] = settings.SITE_ID
        self.target_object = target
        return data

    def create(self, validated_data):
        instance = super(CreateTicketSerializer, self).create(validated_data)
        if Ticket.objects.for_model(self.target_object).count() > settings.REPORT_HIGH_PRIORITY_TICKETS_NUM:
            instance.backend_status = instance.HIGH_PRIORITY
        instance.save()
        return instance

