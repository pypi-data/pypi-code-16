# -*- coding: utf-8 -*-
from bir_api.serializers import CompanySerializer
from congo.utils.types import str2bool
from rest_framework.response import Response
from rest_framework.decorators import api_view
from bir_api.classes import Company

@api_view(['GET'])
def company(request):
    vat_no = request.GET.get('vat_no')
    regon = request.GET.get('regon')
    krs = request.GET.get('krs')
    detailed = str2bool(request.GET.get('detailed', ''))

    data = []

    if any([vat_no, regon, krs]):
        company = Company.get_from_bir(vat_no, regon, krs, detailed)
        if company:
            serializer = CompanySerializer(company)
            data = serializer.data

    return Response(data)
