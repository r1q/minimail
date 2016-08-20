from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):

  # Relationships
  author = models.ForeignKey(User)
  # Core info
  name = models.CharField(max_length=100)
  html_template = models.TextField()
  text_template = models.TextField()
  # Metadata
  created = models.DateTimeField(auto_now_add=True)
  edited = models.DateTimeField(auto_now=True)


  def __str__(self):
    return self.name
