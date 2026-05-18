import json

from rest_framework import views, status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from django.db import transaction

from server.wsgi import registry

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


# -------------------------
# ViewSets
# -------------------------

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

                # deactivate other statuses for same algorithm
                MLAlgorithmStatus.objects.filter(
                    parent_mlalgorithm=instance.parent_mlalgorithm,
                    active=True
                ).exclude(id=instance.id).update(active=False)

        except Exception as e:
            raise APIException(str(e))


class MLRequestViewSet(viewsets.ModelViewSet):
    queryset = MLRequest.objects.all()
    serializer_class = MLRequestSerializer


# -------------------------
# Predict API
# -------------------------

class PredictView(views.APIView):

    def post(self, request, endpoint_name, format=None):

        algorithm_status = request.query_params.get("status", "production")
        algorithm_version = request.query_params.get("version")

        # Step 1: get correct algorithm
        algs = MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name,
            status__active=True,
            status__status=algorithm_status
        ).distinct()

        if algorithm_version:
            algs = algs.filter(version=algorithm_version)

        # Step 2: validation
        if not algs.exists():
            return Response(
                {
                    "status": "Error",
                    "message": f"No ML algorithm found for endpoint '{endpoint_name}'"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if algs.count() > 1 and algorithm_status != "ab_testing":
            return Response(
                {
                    "status": "Error",
                    "message": "ML algorithm selection is ambiguous"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        algorithm = algs.first()

        # Step 3: run model
        try:
            algorithm_object = registry.endpoints[algorithm.id]
            prediction = algorithm_object.compute_prediction(request.data)

            # Step 4: save request (THIS FIXES request_id)
            ml_request = MLRequest.objects.create(
                input_data=json.dumps(request.data),
                full_response=json.dumps(prediction),
                response=json.dumps({
                    "probability": prediction.get("probability"),
                    "label": prediction.get("label")
                }),
                parent_mlalgorithm=algorithm
            )

            # Step 5: return response with request_id
            return Response({
                **prediction,
                "status": "OK",
                "request_id": ml_request.id
            })

        except Exception as e:
            return Response(
                {
                    "status": "Error",
                    "message": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )