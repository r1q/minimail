from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(
        verbose_name=_('timezone'),
        max_length= 50,
        blank=True,
        null=True,
    )
