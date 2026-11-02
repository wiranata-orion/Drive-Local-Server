"""
Drive models for file/folder management.
"""
from django.db import models
from django.conf import settings


def upload_to(instance, filename):
    """Generate upload path for files."""
    # Store files in a flat structure with UUID-like names to avoid conflicts
    import uuid
    ext = filename.split('.')[-1] if '.' in filename else ''
    name = f"{uuid.uuid4().hex}"
    if ext:
        name += f".{ext}"
    return f"uploads/{name}"


class DriveNode(models.Model):
    """
    Represents a file or folder in the drive.
    Uses a self-referential foreign key for folder hierarchy.
    """
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children'
    )
    is_folder = models.BooleanField(default=False)
    file = models.FileField(upload_to=upload_to, null=True, blank=True)
    size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    is_trashed = models.BooleanField(default=False)
    trashed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_folder', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_trashed']),
            models.Index(fields=['is_trashed']),
            models.Index(fields=['parent', 'is_folder', 'name']),
        ]

    def __str__(self):
        return f"{'📁' if self.is_folder else '📄'} {self.name}"

    @property
    def full_path(self):
        """Get full path from root."""
        path = []
        node = self
        while node:
            path.append(node.name)
            node = node.parent
        return '/' + '/'.join(reversed(path))

    @property
    def children_count(self):
        """Count of direct children (folders only)."""
        if self.is_folder:
            return self.children.filter(is_trashed=False).count()
        return 0

    def get_descendants(self):
        """Get all descendant nodes recursively."""
        descendants = []
        for child in self.children.filter(is_trashed=False):
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants

    def soft_delete(self):
        """Move to trash."""
        from django.utils import timezone
        self.is_trashed = True
        self.trashed_at = timezone.now()
        self.save(update_fields=['is_trashed', 'trashed_at', 'updated_at'])
        # Also trash all children
        for child in self.children.filter(is_trashed=False):
            child.soft_delete()

    def restore(self):
        """Restore from trash."""
        self.is_trashed = False
        self.trashed_at = None
        self.save(update_fields=['is_trashed', 'trashed_at', 'updated_at'])
        # Also restore all children
        for child in self.children.filter(is_trashed=True):
            child.restore()

    def permanent_delete(self):
        """Permanently delete file and database record."""
        if self.file:
            # Delete physical file
            try:
                self.file.delete(save=False)
            except Exception:
                pass
        self.delete()