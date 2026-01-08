# documents/serializers.py

from django.conf import settings
from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "file", "status", "created_at"]
        read_only_fields = ["id", "created_at"]

    def to_representation(self, instance):
        """Override to return absolute URL for file field."""
        representation = super().to_representation(instance)
        if instance.file:
            request = self.context.get("request")
            if request:
                representation["file"] = request.build_absolute_uri(instance.file.url)
            else:
                # Fallback: use settings if request is not available
                representation["file"] = f"{settings.DJANGO_BASE_URL}{instance.file.url}"
        return representation
