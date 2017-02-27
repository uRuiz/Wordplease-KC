from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class File(models.Model):

    owner = models.ForeignKey(User)
    file = models.FileField(upload_to=settings.MEDIA_ROOT)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
