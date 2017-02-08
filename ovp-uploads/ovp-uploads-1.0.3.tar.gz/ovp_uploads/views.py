from ovp_uploads.models import UploadedImage
from ovp_uploads.serializers import UploadedImageSerializer

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status

class UploadedImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
  queryset = UploadedImage.objects.all()
  serializer_class = UploadedImageSerializer

  def create(self, request, *args, **kwargs):
    upload_data = {}

    if request.data.get('image', None):
      upload_data['image'] = request.data.get('image')

    upload_header = request.META.get('HTTP_X_UNAUTHENTICATED_UPLOAD', None)
    is_authenticated = request.user.is_authenticated()

    if is_authenticated or upload_header:
      if upload_header:
        upload_data['user'] = None

      if is_authenticated:
        upload_data['user'] = request.user.id

      serializer = self.get_serializer(data=upload_data)

      if serializer.is_valid():
        self.object = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

      return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return response.Response(status=status.HTTP_401_UNAUTHORIZED)
