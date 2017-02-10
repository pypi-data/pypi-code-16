# coding: utf-8

from rest_framework import serializers

from .models import BadgeAward


class BadgesSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    awarded_on = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BadgeAward
        fields = ('slug', 'level', 'points', 'awarded_on', 'name', 'description', 'image_url')

    def get_image_url(self, obj):
        return self.context['view'].request.build_absolute_uri(obj.image_url)
