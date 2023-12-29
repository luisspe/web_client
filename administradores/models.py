from django.db import models

# Create your models here.
class adminNotification(models.Model):
    texto = models.CharField(max_length=10)