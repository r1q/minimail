# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class PixouClickRate(models.Model):
    list = models.TextField(primary_key=True)
    campaign = models.TextField(primary_key=True)
    uri = models.TextField(primary_key=True)
    total = models.IntegerField(blank=True, null=True)
    uniq = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_click_rate'
        unique_together = (('list', 'campaign', 'uri'),)


class PixouOpenDate(models.Model):
    list = models.TextField(primary_key=True)
    campaign = models.TextField(primary_key=True)
    hour_key = models.TextField(primary_key=True)
    hour = models.DateTimeField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_open_date'
        unique_together = (('list', 'campaign', 'hour_key'),)


class PixouOpenRate(models.Model):
    list = models.TextField(primary_key=True)
    campaign = models.TextField(primary_key=True)
    total = models.IntegerField(blank=True, null=True)
    uniq = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_open_rate'
        unique_together = (('list', 'campaign'),)


class PixouOpenSubscriber(models.Model):
    list = models.TextField(primary_key=True)
    campaign = models.TextField(primary_key=True)
    subscriber = models.TextField(primary_key=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_open_subscriber'
        unique_together = (('list', 'campaign', 'subscriber'),)


class PixouSesRate(models.Model):
    list = models.TextField(primary_key=True)
    campaign = models.TextField(primary_key=True)
    delivery = models.IntegerField(blank=True, null=True)
    bounce = models.IntegerField(blank=True, null=True)
    complaint = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_ses_rate'
        unique_together = (('list', 'campaign'),)
