from rest_framework import viewsets

from joda_core.documents.views import DocumentsViewSet
from joda_misc.models import MiscDocument, MiscType
from joda_misc.serializers import MiscDocumentSerializer, MiscTypeSerializer


class MiscDocumentsViewSet(DocumentsViewSet):
    serializer_class = MiscDocumentSerializer
    filter_fields = ('misc_type', 'tags', 'public', 'verified')

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return MiscDocument.objects.filter(public=True).order_by('-pk')
        return MiscDocument.objects.order_by('-pk')


class MiscTypesViewSet(viewsets.ModelViewSet):
    queryset = MiscType.objects.all().order_by('name')
    serializer_class = MiscTypeSerializer
