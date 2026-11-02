"""
Serializers for Drive API.
"""
from rest_framework import serializers
from .models import DriveNode
from django.conf import settings


class DriveNodeSerializer(serializers.ModelSerializer):
    """Serializer for file/folder listing and detail."""
    download_url = serializers.SerializerMethodField()
    preview_url = serializers.SerializerMethodField()
    children_count = serializers.IntegerField(read_only=True)
    size_formatted = serializers.SerializerMethodField()
    path = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)

    class Meta:
        model = DriveNode
        fields = [
            'id', 'name', 'parent', 'parent_name', 'is_folder',
            'file', 'size', 'size_formatted', 'mime_type',
            'is_trashed', 'trashed_at', 'created_at', 'updated_at',
            'download_url', 'preview_url', 'children_count', 'path',
        ]
        read_only_fields = [
            'id', 'size', 'mime_type', 'is_trashed', 'trashed_at',
            'created_at', 'updated_at', 'download_url', 'preview_url',
            'children_count', 'path',
        ]

    def get_download_url(self, obj):
        if not obj.is_folder and obj.file:
            request = self.context.get('request')
            url = f'/api/files/{obj.id}/download/'
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_preview_url(self, obj):
        if not obj.is_folder and obj.file:
            request = self.context.get('request')
            url = f'/api/files/{obj.id}/preview/'
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_size_formatted(self, obj):
        if obj.size == 0:
            return '-'
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if obj.size < 1024:
                return f"{obj.size:.1f} {unit}"
            obj.size /= 1024
        return f"{obj.size:.1f} PB"

    def get_path(self, obj):
        return obj.full_path


class DriveNodeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating folders."""
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = DriveNode
        fields = ['id', 'name', 'parent_id', 'is_folder']
        read_only_fields = ['id', 'is_folder']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        # Check for invalid characters
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in value:
                raise serializers.ValidationError(f"Name cannot contain '{char}'")
        return value.strip()

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id:
            try:
                parent = DriveNode.objects.get(id=parent_id, is_folder=True, is_trashed=False)
                validated_data['parent'] = parent
            except DriveNode.DoesNotExist:
                raise serializers.ValidationError("Parent folder not found")

        validated_data['is_folder'] = True
        return super().create(validated_data)


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload."""
    file = serializers.FileField(write_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = DriveNode
        fields = ['id', 'name', 'file', 'parent_id', 'size', 'mime_type']
        read_only_fields = ['id', 'size', 'mime_type']

    def validate_file(self, value):
        # Check file size (max 100MB for now)
        max_size = 100 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"File size exceeds maximum allowed ({max_size / (1024*1024)}MB)")
        return value

    def create(self, validated_data):
        uploaded_file = validated_data.pop('file')
        parent_id = validated_data.pop('parent_id', None)

        if parent_id:
            try:
                parent = DriveNode.objects.get(id=parent_id, is_folder=True, is_trashed=False)
                validated_data['parent'] = parent
            except DriveNode.DoesNotExist:
                raise serializers.ValidationError("Parent folder not found")

        # Set file metadata
        validated_data['is_folder'] = False
        validated_data['size'] = uploaded_file.size
        validated_data['mime_type'] = getattr(uploaded_file, 'content_type', '') or 'application/octet-stream'
        validated_data['file'] = uploaded_file

        # Use original filename if name not provided
        if not validated_data.get('name'):
            validated_data['name'] = uploaded_file.name

        return super().create(validated_data)


class DriveNodeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating file/folder (rename, move)."""
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = DriveNode
        fields = ['id', 'name', 'parent_id']
        read_only_fields = ['id']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty")
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            if char in value:
                raise serializers.ValidationError(f"Name cannot contain '{char}'")
        return value.strip()

    def update(self, instance, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        if parent_id is not None:
            if parent_id == 0:
                instance.parent = None
            else:
                try:
                    parent = DriveNode.objects.get(id=parent_id, is_folder=True, is_trashed=False)
                    # Prevent moving into self or descendant
                    if parent == instance or instance in parent.get_descendants():
                        raise serializers.ValidationError("Cannot move folder into itself or its descendant")
                    instance.parent = parent
                except DriveNode.DoesNotExist:
                    raise serializers.ValidationError("Parent folder not found")

        return super().update(instance, validated_data)


class FolderTreeSerializer(serializers.ModelSerializer):
    """Serializer for folder tree (recursive)."""
    children = serializers.SerializerMethodField()

    class Meta:
        model = DriveNode
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        # Only include non-trashed folders
        children = obj.children.filter(is_folder=True, is_trashed=False)
        return FolderTreeSerializer(children, many=True, context=self.context).data


class SearchResultSerializer(serializers.ModelSerializer):
    """Serializer for search results."""
    path = serializers.SerializerMethodField()
    size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = DriveNode
        fields = ['id', 'name', 'is_folder', 'size', 'size_formatted', 'mime_type', 'path', 'created_at', 'updated_at']

    def get_path(self, obj):
        return obj.full_path

    def get_size_formatted(self, obj):
        if obj.size == 0:
            return '-'
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if obj.size < 1024:
                return f"{obj.size:.1f} {unit}"
            obj.size /= 1024
        return f"{obj.size:.1f} PB"


class StatsSerializer(serializers.Serializer):
    """Serializer for storage statistics."""
    total_files = serializers.IntegerField()
    total_folders = serializers.IntegerField()
    total_size = serializers.IntegerField()
    total_size_formatted = serializers.CharField()
    trashed_files = serializers.IntegerField()
    trashed_size = serializers.IntegerField()
    trashed_size_formatted = serializers.CharField()
    storage_used = serializers.IntegerField()
    storage_used_formatted = serializers.CharField()


class AuthLoginSerializer(serializers.Serializer):
    """Serializer for login."""
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        from django.conf import settings
        shared_password = getattr(settings, 'SHARED_PASSWORD', None)
        if not shared_password:
            raise serializers.ValidationError("Server not configured")
        if value != shared_password:
            raise serializers.ValidationError("Invalid password")
        return value


class AuthStatusSerializer(serializers.Serializer):
    """Serializer for auth status."""
    authenticated = serializers.BooleanField()
    message = serializers.CharField()