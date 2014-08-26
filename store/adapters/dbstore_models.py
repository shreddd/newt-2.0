from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Store(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'store'

@receiver(pre_delete, sender=Store)
def pre_store_rm(sender, instance, using, **kwargs):
    instance.documents.all().delete()
    instance.perms.all().delete()
    instance.save()

class Document(models.Model):
    oid = models.PositiveIntegerField()
    data = models.TextField()
    store = models.ForeignKey(Store, related_name="documents")

    class Meta:
        app_label = 'store'

class Permission(models.Model):
    user = models.ForeignKey(User, related_name="store_perms")
    store = models.ForeignKey(Store, related_name='perms')
    type = models.CharField(max_length=100, default="r")

    class Meta:
        app_label = 'store'
