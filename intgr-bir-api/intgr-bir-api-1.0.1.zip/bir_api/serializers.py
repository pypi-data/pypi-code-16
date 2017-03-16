# -*- coding: utf-8 -*-
from rest_framework import serializers

class CompanySerializer(serializers.Serializer):
    name = serializers.CharField(max_length = 255)
    vat_no = serializers.IntegerField()
    regon = serializers.IntegerField()
    street = serializers.CharField(max_length = 255)
    zip_code = serializers.CharField(max_length = 255)
    city = serializers.CharField(max_length = 255)
    country = serializers.CharField(max_length = 255)
    voivodeship = serializers.CharField(max_length = 255)
    county = serializers.CharField(max_length = 255)
    community = serializers.CharField(max_length = 255)
    type = serializers.CharField(max_length = 255)
