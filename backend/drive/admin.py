"""
Admin configuration for Drive app.
"""
from django.contrib import admin
from .models import DriveNode


@admin.register(DriveNode)
class DriveNodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_folder', 'size_formatted', 'mime_type', 'is_trashed', 'created_at']
    list_filter = ['is_folder', 'is_trashed', 'created_at', 'parent']
    search_fields = ['name']
    readonly_fields = ['size', 'mime_type', 'created_at', 'updated_at', 'trashed_at', 'file']
    ordering = ['-is_folder', 'name']
    list_per_page = 50

    def size_formatted(self, obj):
        if obj.size == 0:
            return '-'
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if obj.size < 1024:
                return f"{obj.size:.1f} {unit}"
            obj.size /= 1024
        return f"{obj.size:.1f} PB"
    size_formatted.short_description = 'Size'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')