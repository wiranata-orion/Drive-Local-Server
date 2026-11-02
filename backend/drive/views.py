"""
Drive API Views.
"""
import os
import mimetypes
from django.http import FileResponse, Http404
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import DriveNode
from .serializers import (
    DriveNodeSerializer,
    DriveNodeCreateSerializer,
    FileUploadSerializer,
    DriveNodeUpdateSerializer,
    FolderTreeSerializer,
    SearchResultSerializer,
    StatsSerializer,
    AuthLoginSerializer,
    AuthStatusSerializer,
)
from .utils import detect_mime_type, generate_thumbnail, format_file_size


# Authentication Views

@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    """Login with shared password."""
    serializer = AuthLoginSerializer(data=request.data)
    if serializer.is_valid():
        # Password validated in serializer
        return Response({
            'success': True,
            'message': 'Authentication successful',
            'token': request.data.get('password'),  # Return password as token for client
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def auth_status(request):
    """Check authentication status."""
    return Response({
        'authenticated': True,
        'message': 'Authenticated',
    })


# File/Folder Views

class DriveNodeViewSet(viewsets.ModelViewSet):
    """ViewSet for file/folder operations."""
    queryset = DriveNode.objects.all()
    serializer_class = DriveNodeSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        """Filter by parent and trash status."""
        queryset = DriveNode.objects.filter(is_trashed=False)

        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            if parent_id == '0' or parent_id == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        else:
            # Default to root level
            queryset = queryset.filter(parent__isnull=True)

        # Search filter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.select_related('parent')

    def get_serializer_class(self):
        if self.action == 'create':
            # Check if it's a folder creation or file upload
            if self.request.data.get('is_folder') or not self.request.FILES:
                return DriveNodeCreateSerializer
            return FileUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return DriveNodeUpdateSerializer
        return DriveNodeSerializer

    def create(self, request, *args, **kwargs):
        """Create folder or upload file."""
        is_folder_val = request.data.get('is_folder', False)
        is_folder = str(is_folder_val).lower() == 'true'

        if is_folder:
            serializer = DriveNodeCreateSerializer(data=request.data, context={'request': request})
        else:
            serializer = FileUploadSerializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        # Return full serialized object
        output_serializer = DriveNodeSerializer(instance, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Soft delete (move to trash)."""
        instance = self.get_object()
        instance.soft_delete()
        return Response({'success': True, 'message': 'Moved to trash'})

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download file."""
        instance = self.get_object()
        if instance.is_folder:
            return Response({'error': 'Cannot download folder'}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.file:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            response = FileResponse(
                instance.file.open('rb'),
                as_attachment=True,
                filename=instance.name
            )
            response['Content-Length'] = instance.size
            return response
        except FileNotFoundError:
            return Response({'error': 'File not found on disk'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Preview file (inline)."""
        instance = self.get_object()
        if instance.is_folder:
            return Response({'error': 'Cannot preview folder'}, status=status.HTTP_400_BAD_REQUEST)

        if not instance.file:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # For images, PDFs, text - serve inline
            response = FileResponse(
                instance.file.open('rb'),
                as_attachment=False,
                filename=instance.name
            )
            response['Content-Length'] = instance.size
            response['Content-Type'] = instance.mime_type or 'application/octet-stream'
            # Allow embedding in iframe
            response['X-Frame-Options'] = 'SAMEORIGIN'
            return response
        except FileNotFoundError:
            return Response({'error': 'File not found on disk'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get folder tree for sidebar."""
        # Get root folders (no parent, not trashed)
        roots = DriveNode.objects.filter(parent__isnull=True, is_folder=True, is_trashed=False)
        serializer = FolderTreeSerializer(roots, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search files and folders."""
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response([])

        results = DriveNode.objects.filter(
            Q(name__icontains=query) & Q(is_trashed=False)
        )[:100]  # Limit results

        serializer = SearchResultSerializer(results, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get storage statistics."""
        # Active files/folders
        active = DriveNode.objects.filter(is_trashed=False)
        total_files = active.filter(is_folder=False).count()
        total_folders = active.filter(is_folder=True).count()
        total_size = active.filter(is_folder=False).aggregate(Sum('size'))['size__sum'] or 0

        # Trashed
        trashed = DriveNode.objects.filter(is_trashed=True)
        trashed_files = trashed.filter(is_folder=False).count()
        trashed_size = trashed.filter(is_folder=False).aggregate(Sum('size'))['size__sum'] or 0

        # Storage info
        storage_path = os.environ.get('STORAGE_ROOT', '/media/files')
        try:
            stat = os.statvfs(storage_path)
            storage_total = stat.f_blocks * stat.f_frsize
            storage_free = stat.f_bavail * stat.f_frsize
            storage_used = storage_total - storage_free
        except Exception:
            storage_total = total_size
            storage_used = total_size

        data = {
            'total_files': total_files,
            'total_folders': total_folders,
            'total_size': total_size,
            'total_size_formatted': format_file_size(total_size),
            'trashed_files': trashed_files,
            'trashed_size': trashed_size,
            'trashed_size_formatted': format_file_size(trashed_size),
            'storage_used': storage_used,
            'storage_used_formatted': format_file_size(storage_used),
            'storage_total': storage_total,
            'storage_total_formatted': format_file_size(storage_total),
        }
        serializer = StatsSerializer(data)
        return Response(serializer.data)


# Trash Views

class TrashViewSet(viewsets.ViewSet):
    """ViewSet for trash operations."""

    def list(self, request):
        """List trashed items."""
        trashed = DriveNode.objects.filter(is_trashed=True).select_related('parent')
        serializer = DriveNodeSerializer(trashed, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore item from trash."""
        try:
            item = DriveNode.objects.get(pk=pk, is_trashed=True)
            item.restore()
            serializer = DriveNodeSerializer(item, context={'request': request})
            return Response(serializer.data)
        except DriveNode.DoesNotExist:
            return Response({'error': 'Item not found in trash'}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Permanently delete item."""
        try:
            item = DriveNode.objects.get(pk=pk, is_trashed=True)
            item.permanent_delete()
            return Response({'success': True, 'message': 'Permanently deleted'})
        except DriveNode.DoesNotExist:
            return Response({'error': 'Item not found in trash'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def empty(self, request):
        """Empty trash permanently."""
        trashed_items = DriveNode.objects.filter(is_trashed=True)
        count = trashed_items.count()
        for item in trashed_items:
            item.permanent_delete()
        return Response({'success': True, 'message': f'Permanently deleted {count} items'})