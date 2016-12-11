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

class ClickRate(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    unique_count = models.IntegerField(blank=True)
    total_count = models.IntegerField(blank=True)

class SesRate(models.Model):
    id = models.CharField(primary_key=True, max_length=125)
    list = models.ForeignKey(List)
    campaign = models.ForeignKey(Campaign)
    delivery_count = models.IntegerField(blank=True)
    bounce_count = models.IntegerField(blank=True)
    complaint_count = models.IntegerField(blank=True)
