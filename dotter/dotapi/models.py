from django.db import models
from django.contrib.auth.models import User

class Graph(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    dot = models.CharField(max_length=255)
    png = models.CharField(max_length=255)
    public_link = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['created_on']
