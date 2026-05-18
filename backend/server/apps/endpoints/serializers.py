from rest_framework import serializers
from apps.endpoints.models import Endpoint, MLAlgorithm, MLAlgorithmStatus, MLRequest


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ("id", "name", "owner", "created_at")
        read_only_fields = fields


class MLAlgorithmSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField()

    def get_current_status(self, mlalgorithm):
        status_obj = MLAlgorithmStatus.objects.filter(
            parent_mlalgorithm=mlalgorithm
        ).order_by('-created_at').first()

        return status_obj.status if status_obj else None

    class Meta:
        model = MLAlgorithm
        fields = (
            "id", "name", "description", "code",
            "version", "owner", "created_at",
            "parent_endpoint", "current_status"
        )
        read_only_fields = fields


class MLAlgorithmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLAlgorithmStatus
        fields = (
            "id",
            "status",
            "active",
            "created_by",
            "created_at",
            "parent_mlalgorithm",
        )
        read_only_fields = ("id", "active")


class MLRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLRequest
        fields = (
            "id",
            "input_data",
            "full_response",
            "response",
            "feedback",
            "created_at",
            "parent_mlalgorithm",
        )
        read_only_fields = (
            "id",
            "input_data",
            "full_response",
            "response",
            "created_at",
            "parent_mlalgorithm",
        )