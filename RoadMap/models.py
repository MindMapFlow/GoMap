from django.db import models
from django.contrib.auth.models import User

class Major(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='roadmap_majors')

    def __str__(self):
        return self.name