# documents/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet, ingest_callback

router = DefaultRouter()
router.register(r"", DocumentViewSet, basename="document")

urlpatterns = [
    *router.urls,
    path("<int:pk>/ingest-callback/", ingest_callback, name="document-ingest-callback"),
]
