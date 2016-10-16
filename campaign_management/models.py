from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

from subscriber_management.models import List


class Campaign(models.Model):
    """Campaign"""

    # Relationships
    author = models.ForeignKey(User)
    email_list = models.ForeignKey(List)
    # Core info
    name = models.CharField(max_length=100, blank=True)
    email_subject = models.CharField(max_length=150)
    email_from_name = models.CharField(max_length=100)
    email_reply_to_email = models.CharField(max_length=100)
    email_from_email = models.CharField(max_length=100, blank=True) # populated from email_list.from_email
    schedule_send = models.DateTimeField(blank=True, null=True)
    # No foreign key for these, as the template may change
#    html_email_for_editing = models.TextField()
#    html_email_for_sending = models.TextField()
    html_email = models.TextField()
    text_email = models.TextField(blank=True, default='')
    # Status
    is_sent = models.BooleanField(default=False)
    recipient_count = models.PositiveIntegerField(blank=True, null=True)
    is_draft = models.BooleanField(default=True)
    # Metadata
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('campaign-compose-email', kwargs={'pk': self.pk})
