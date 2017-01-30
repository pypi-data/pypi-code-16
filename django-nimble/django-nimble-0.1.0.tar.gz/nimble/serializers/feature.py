from rest_framework import serializers, viewsets

from nimble.models.feature import Feature
from .user import UserSerializer


class FeatureSerializer(serializers.HyperlinkedModelSerializer):

    author = UserSerializer(
        read_only=True,
        default=serializers.CreateOnlyDefault('Junk')
    )

    class Meta:
        model = Feature
        fields = Feature.api_keys()

    def validate_author(self, value):
        """
        This will force the author when a new debt is created via the API.
        """
        return self.context['request'].user


# ViewSets define the view behavior.
class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
