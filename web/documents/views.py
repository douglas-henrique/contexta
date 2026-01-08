import logging

from rest_framework import permissions, viewsets

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
        document.status = 'processing'
        document.save()

        # Get file path
        file_path = document.file.path if document.file else None

        if not file_path:
            logger.error(f"Document {document.id} has no file path")
            document.status = 'failed'
            document.save()
            return

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
                        "created_at": document.created_at.isoformat() if document.created_at else None,
                    }
                )

                if success:
                    document.status = 'processing'
                else:
                    document.status = 'failed'
                document.save()
            except Exception as e:
                logger.error(f"Error in background ingestion for document {document.id}: {e}", exc_info=True)
                document.status = 'failed'
                document.save()

        thread = threading.Thread(target=ingest_in_background)
        thread.daemon = True
        thread.start()

        logger.info(f"Document {document.id} created, ingestion triggered")
