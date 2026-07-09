from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
    )
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return self.title