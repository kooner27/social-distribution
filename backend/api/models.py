from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Author(models.Model):
    display_name = models.CharField(max_length=255)