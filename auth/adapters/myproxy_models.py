from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cred(models.Model):
    class Meta:
        app_label = 'auth'
    cert = models.TextField()
    key = models.TextField()
    calist = models.TextField()
    user = models.ForeignKey(User)

