from rest_framework import serializers, viewsets

from nimble.models.debt import Debt
from .user import UserSerializer


class DebtSerializer(serializers.HyperlinkedModelSerializer):

    author = UserSerializer(
        read_only=True,
        default=serializers.CreateOnlyDefault('Junk')
    )

    class Meta:
        model = Debt
        fields = Debt.api_keys()

    def validate_author(self, value):
        """
        This will force the author when a new debt is created via the API.
        """
        return self.context['request'].user


# ViewSets define the view behavior.
class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer
