from django.db import models
from user_management.models import MyUser
from django.urls import reverse
from django.contrib.postgres.fields import JSONField

from subscriber_management.models import List
from template_management.models import Template

import uuid as UUID


class Campaign(models.Model):
    """Campaign"""

    # Relationships
    author = models.ForeignKey(MyUser)
    email_list = models.ForeignKey(List)
    using_template = models.ForeignKey(Template, blank=True, null=True)
    # Core info
    name = models.CharField(max_length=100, blank=True)
    email_subject = models.CharField(max_length=150)
    email_from_name = models.CharField(max_length=100)
    email_reply_to_email = models.CharField(max_length=100)
    email_from_email = models.CharField(max_length=100, blank=True) # populated from email_list.from_email
    schedule_send = models.DateTimeField(blank=True, null=True)
    html_email_for_editing = models.TextField()
    html_email_for_sending = models.TextField()
    text_email = models.TextField(blank=True, default='')
    placeholders_value = JSONField(null=True)
    # Status
    is_sent = models.BooleanField(default=False)
    recipient_count = models.PositiveIntegerField(blank=True, null=True)
    is_draft = models.BooleanField(default=True)
    is_composed = models.BooleanField(default=False)
    unsubscribe_count = models.PositiveIntegerField(default=0)
    # Metadata
    uuid = models.UUIDField(default=UUID.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    sent = models.DateTimeField(editable=False, null=True, blank=True)
    # Tracking relative to campaign
    utm_campaign = models.CharField(blank=True, max_length=140)
    utm_content = models.CharField(blank=True, max_length=140)
    utm_term = models.CharField(blank=True, max_length=100)


    def __str__(self):
        return self.email_subject

    def get_absolute_url(self):
        return reverse('campaign-choose-tmplt', kwargs={'pk': self.pk})
