from django.db import models

from django.contrib.auth.models import User

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.CharField(max_length=20, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return self.file.url
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_type = self.file.name.split('.')[-1].lower()
            self.file_size = self._get_file_size()
        super().save(*args, **kwargs)
    
    def _get_file_size(self):
        size = self.file.size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{round(size/1024, 1)} KB"
        else:
            return f"{round(size/(1024*1024), 1)} MB"