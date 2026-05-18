from django.db import transaction
from rest_framework import viewsets
from rest_framework.exceptions import APIException

from apps.endpoints.models import (
    Endpoint,
    MLAlgorithm,
    MLAlgorithmStatus,
    MLRequest
)

from apps.endpoints.serializers import (
    EndpointSerializer,
    MLAlgorithmSerializer,
    MLAlgorithmStatusSerializer,
    MLRequestSerializer
)


class EndpointViewSet(viewsets.ModelViewSet):
    queryset = Endpoint.objects.all()
    serializer_class = EndpointSerializer


class MLAlgorithmViewSet(viewsets.ModelViewSet):
    queryset = MLAlgorithm.objects.all()
    serializer_class = MLAlgorithmSerializer


class MLAlgorithmStatusViewSet(viewsets.ModelViewSet):
    queryset = MLAlgorithmStatus.objects.all()
    serializer_class = MLAlgorithmStatusSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)

                MLAlgorithmStatus.objects.filter(
                    parent_mlalgorithm=instance.parent_mlalgorithm,
                    active=True
                ).exclude(id=instance.id).update(active=False)

        except Exception as e:
            raise APIException(str(e))


class MLRequestViewSet(viewsets.ModelViewSet):
    queryset = MLRequest.objects.all()
    serializer_class = MLRequestSerializer