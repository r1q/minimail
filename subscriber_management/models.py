import uuid
from django.db import models
from django.contrib.auth.models import User
from strgen import StringGenerator
from localize import timezone


def _gen_token():
    """_gen_token"""
    return StringGenerator(r'[a-z0-9]{16}').render()


class List(models.Model):
    """List"""

    # Meta
    user = models.ForeignKey(User)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    # Internal usage
    name = models.CharField(max_length=125, blank=True)
    # Visible to subscribers
    title = models.CharField(max_length=125, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=4000, blank=True)
    image = models.ImageField(upload_to='subscribe_list/images/', null=True,
                              blank=True)
    token = models.CharField(default=_gen_token, max_length=17,
                                       blank=True)

    # custom templates
    subscribe_template = models.TextField(blank=True)
    success_template = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def count_subscribers(self):
        """count_subscribers"""
        return Subscriber.objects.filter(list__id=self.id).count()

    def signup_token(self):
        t = str(self.uuid)+"_"+self.token
        return t.replace("-","_", -1)


class Subscriber(models.Model):
    """Subscriber"""

    # Meta
    list = models.ForeignKey(List)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    token_subscribe = models.CharField(default=_gen_token, max_length=17,
                                       blank=True)
    token_unsubscribe = models.CharField(default=_gen_token, max_length=17,
                                         blank=True)
    validated = models.BooleanField(default=False, blank=True)

    email = models.EmailField(max_length=50, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    validated = models.BooleanField(blank=True, default=False)
    timezone = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    user_agent = models.TextField(blank=True)
    accept_language = models.TextField(blank=True)
    ip_subscribe = models.GenericIPAddressField(blank=True, null=True)
    ip_validate = models.GenericIPAddressField(blank=True, null=True)
    extra = models.TextField(blank=True)

    class Meta:
        unique_together = ('list', 'email',)

    def __str__(self):
        return self.email

    def full_name(self):
        return self.first_name+" "+self.last_name

    def validation_link(self):
        return 'http://minimail.fullweb.io/subscribers/subscriber/{}/validate/{}'.format(self.uuid, self.token_subscribe)

    def human_tz(self):
        return timezone.human_timezone(self.timezone)
