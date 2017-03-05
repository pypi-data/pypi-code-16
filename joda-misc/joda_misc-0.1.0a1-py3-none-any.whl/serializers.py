from rest_framework_json_api import serializers

from joda_core.documents.serializers import DocumentSerializer
from joda_misc.models import MiscDocument, MiscType


class MiscDocumentSerializer(DocumentSerializer):

    class Meta(DocumentSerializer.Meta):
        model = MiscDocument


class MiscTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = MiscType
        fields = ('id', 'name')
