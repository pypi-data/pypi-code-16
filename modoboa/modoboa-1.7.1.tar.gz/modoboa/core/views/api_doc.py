"""API documentation views."""

from rest_framework import permissions, renderers, response, schemas
from rest_framework.decorators import (
    api_view, permission_classes, renderer_classes)
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer


@api_view()
@renderer_classes([
    SwaggerUIRenderer, OpenAPIRenderer, renderers.CoreJSONRenderer])
@permission_classes([permissions.AllowAny])
def schema_view(request):
    generator = schemas.SchemaGenerator(
        title="Modoboa API documentation")
    return response.Response(generator.get_schema())
