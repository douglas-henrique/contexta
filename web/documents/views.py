import logging

from django.conf import settings
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Document
from .serializers import DocumentSerializer
from .services import trigger_ingestion

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """Create document and trigger ingestion."""
        document = serializer.save(owner=self.request.user)

        # Update status to processing
        document.status = "processing"
        document.save()

        # Get file path
        file_path = document.file.path if document.file else None

        if not file_path:
            logger.error(f"Document {document.id} has no file path")
            document.status = "failed"
            document.save()
            return

        # Build callback URL for status updates
        django_base_url = settings.DJANGO_BASE_URL
        callback_url = f"{django_base_url}/api/documents/{document.id}/ingest-callback/"

        # Trigger ingestion in background
        # Using threading for now (can be replaced with Celery later)
        import threading

        def ingest_in_background():
            try:
                success = trigger_ingestion(
                    document_id=document.id,
                    file_path=file_path,
                    user_id=self.request.user.id,
                    metadata={
                        "title": document.title,
                        "created_at": (document.created_at.isoformat() if document.created_at else None),
                    },
                    callback_url=callback_url,
                )

                if not success:
                    document.status = "failed"
                    document.save()
            except Exception as e:
                logger.error(
                    f"Error in background ingestion for document {document.id}: {e}",
                    exc_info=True,
                )
                document.status = "failed"
                document.save()

        thread = threading.Thread(target=ingest_in_background)
        thread.daemon = True
        thread.start()

        logger.info(f"Document {document.id} created, ingestion triggered")


@api_view(["POST"])
@permission_classes([])  # No authentication required for callback
def ingest_callback(request, pk):
    """
    Callback endpoint for ingest service to update document status.
    This endpoint is called by the ingest service when ingestion completes.
    """
    try:
        document = Document.objects.get(pk=pk)
        status_value = request.data.get("status")

        if status_value == "completed":
            document.status = "completed"
            document.save()
            logger.info(f"Document {document.id} status updated to completed via callback")
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        elif status_value == "failed":
            document.status = "failed"
            document.save()
            logger.warning(f"Document {document.id} status updated to failed via callback")
            return Response({"status": "ok"}, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Invalid status value in callback: {status_value}")
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

    except Document.DoesNotExist:
        logger.error(f"Document {pk} not found for callback")
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error processing callback for document {pk}: {e}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
