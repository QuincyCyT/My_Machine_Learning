from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import (
    EndpointViewSet,
    MLAlgorithmViewSet,
    MLAlgorithmStatusViewSet,
    MLRequestViewSet,
    PredictView,
)

router = DefaultRouter()

router.register(r'endpoints', EndpointViewSet, basename='endpoints')
router.register(r'ml-algorithms', MLAlgorithmViewSet, basename='ml-algorithms')
router.register(r'ml-statuses', MLAlgorithmStatusViewSet, basename='ml-statuses')
router.register(r'ml-requests', MLRequestViewSet, basename='ml-requests')

urlpatterns = [
    path('', include(router.urls)),

    path('predict/<str:endpoint_name>/', PredictView.as_view()),
]