from django.db import models
from subscriber_management.models import List
from campaign_management.models import Campaign


class OpenRate(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    unique_count = models.IntegerField(blank=True)
    total_count = models.IntegerField(blank=True)


class OpenRateHourly(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    date = models.DateTimeField(blank=True)
    unique_count = models.IntegerField(blank=True)
    total_count = models.IntegerField(blank=True)

class OpenCountry(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    country = models.CharField(max_length=50,blank=True)
    unique_count = models.IntegerField(blank=True)
    total_count = models.IntegerField(blank=True)


class ClickRate(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    uri = models.TextField(blank=True)
    unique_count = models.IntegerField(blank=True)
    total_count = models.IntegerField(blank=True)

class SesDeliveryStats(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    total_count = models.IntegerField(blank=False, null=False)
    first = models.DateTimeField(blank=False, null=False)
    last = models.DateTimeField(blank=False, null=False)

class SesComplaintStats(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    total_count = models.IntegerField(blank=False, null=False)

class SesBounceStats(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    soft_count = models.IntegerField(blank=False, null=False)
    hard_count = models.IntegerField(blank=False, null=False)

class SesBounceSoft(models.Model):

    BOUNCE_TYPES = (
        ("undefinded", "undefinded"),
        ("ooto", "ooto"),
        ("mailboxfull", "mailboxfull"),
        ("messagetoolarge", "messagetoolarge"),
        ("contentrejected", "contentrejected"),
        ("attachmentrejected", "attachmentrejected"),
    )

    id = models.CharField(primary_key=True, max_length=125)
    bounce_type = models.CharField(max_length=125, choices=BOUNCE_TYPES)
    list_uuid = models.CharField(max_length=125)
    campaign_uuid = models.CharField(max_length=125)
    subscriber_uuid = models.CharField(max_length=125)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
