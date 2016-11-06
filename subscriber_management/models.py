from django.db import models
from user_management.models import MyUser
from localize import timezone
from django.urls import reverse
from django.conf import settings

import uuid as UUID


class List(models.Model):
    """List"""

    # Meta
    user = models.ForeignKey(MyUser)
    uuid = models.UUIDField(default=UUID.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    # Internal usage
    name = models.CharField(max_length=125, blank=True)
    # Visible to subscribers
    title = models.CharField(max_length=125, blank=True)
    from_email = models.CharField(max_length=125, blank=True)
    from_email_verified = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=4000, blank=True)
    image = models.ImageField(upload_to='subscribe_list/images/', null=True,
                              blank=True)
    token = models.CharField(default=UUID.uuid4, max_length=50,
                             blank=True, editable=False)

    # custom templates
    subscribe_template = models.TextField(blank=True)
    success_template = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def count_all_subscribers(self):
        """count_all_subscribers"""
        return Subscriber.objects.filter(list__id=self.id).count()

    def count_validated_subscribers(self):
        """count_validated_subscribers"""
        return Subscriber.objects.filter(list__id=self.id, validated=True).count()

    def signup_token(self):
        """signup_token"""
        t = str(self.uuid)+"_"+self.token
        return t.replace("-", "_", -1)


class Subscriber(models.Model):
    """Subscriber"""

    # Meta
    list = models.ForeignKey(List)
    uuid = models.UUIDField(default=UUID.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    token_subscribe = models.CharField(default=UUID.uuid4, max_length=50,
                                       blank=True, editable=False)
    token_unsubscribe = models.CharField(default=UUID.uuid4, max_length=50,
                                         blank=True, editable=False)
    validated = models.BooleanField(default=False, blank=True)

    email = models.EmailField(max_length=50)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    accept_language = models.TextField(blank=True, null=True)
    ip_subscribe = models.GenericIPAddressField(blank=True, null=True)
    ip_validate = models.GenericIPAddressField(blank=True, null=True)
    extra = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('list', 'email',)

    def __str__(self):
        return self.email

    def full_name(self):
        try:
            return self.first_name+" "+self.last_name
        except:
            return ""

    def validation_link(self):
        return settings.BASE_URL+reverse('subscriber-management-subscriber-validate', kwargs={'uuid':self.uuid, 'token':self.token_subscribe})

    def unsubscribe_link(self):
        return settings.BASE_URL+reverse('subscriber-management-subscriber-unsubscribe', kwargs={'uuid':self.uuid, 'token':self.token_unsubscribe})

    def human_tz(self):
        return timezone.human_timezone(self.timezone)
