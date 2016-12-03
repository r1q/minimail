Loading development environment.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class PixouClickRate(models.Model):
    id = models.TextField(primary_key=True)
    list = models.TextField(blank=True, null=True)
    campaign = models.TextField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    uniq = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_click_rate'


class PixouOpenDate(models.Model):
    id = models.TextField(primary_key=True)
    list = models.TextField(blank=True, null=True)
    campaign = models.TextField(blank=True, null=True)
    hour_key = models.TextField(blank=True, null=True)
    hour = models.DateTimeField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_open_date'


class PixouOpenRate(models.Model):
    id = models.TextField(primary_key=True)
    list = models.TextField(blank=True, null=True)
    campaign = models.TextField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    uniq = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_open_rate'


class PixouSesRate(models.Model):
    id = models.TextField(primary_key=True)
    list = models.TextField(blank=True, null=True)
    campaign = models.TextField(blank=True, null=True)
    delivery = models.IntegerField(blank=True, null=True)
    bounce = models.IntegerField(blank=True, null=True)
    complaint = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pixou_ses_rate'
