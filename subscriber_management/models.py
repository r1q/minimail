from django.db import models
from django.contrib.auth.models import User
import uuid


class List(models.Model):

    # Meta
    user = models.ForeignKey(User)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=125, blank=True)
    title = models.CharField(max_length=125, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=4000, blank=True)

    # custom templates
    subscribe_template = models.TextField(blank=True)
    success_template = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def count_susbscribers(self):
        return Subscriber.objects.filter(list__id=self.id).count()


class Subscriber(models.Model):

    # Meta
    class Meta:
        unique_together = ('list', 'email',)
        
    list = models.ForeignKey(List)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    email = models.EmailField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.email
