from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from subscriber_management.models import List
from template_management.models import Template


class Campaign(models.Model):
    """Campaign"""

    # Relationships
    author = models.ForeignKey(User)
    email_list = models.ForeignKey(List)
    email_template = models.ForeignKey(Template)
    # Core info
    name = models.CharField(max_length=100)
    email_subject = models.CharField(max_length=150)
    email_from_name = models.CharField(max_length=100)
    email_from_email = models.CharField(max_length=100)
    schedule_send = models.DateTimeField(blank=True, null=True)
    # Status
    is_sent = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    # Metadata
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('campaign-review', kwargs={'pk': self.pk})
