from django.db import models
from django.contrib.auth.models import User

class Bookmark(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=255)

    url = models.URLField()

    content = models.TextField()

    summary = models.TextField(blank=True)

    tags = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
    embedding = models.JSONField(
       null=True,
       blank=True
    )