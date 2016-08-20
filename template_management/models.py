from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.urls import reverse


class Template(models.Model):

  # Relationships
  author = models.ForeignKey(User)
  # Core info
  name = models.CharField(max_length=100)
  html_template = models.TextField()
  text_template = models.TextField(blank=True)
  # Metadata
  created = models.DateTimeField(auto_now_add=True)
  edited = models.DateTimeField(auto_now=True)

  def __str__(self):
    return self.name

  def get_absolute_url(self):
    return reverse('template-detail', kwargs={'pk': self.pk})
