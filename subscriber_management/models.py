from django.db import models
from user_management.models import MyUser
from localize import timezone
from django.urls import reverse
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.utils.text import slugify

import uuid as UUID


LANG_CHOICES = (\
('en', 'English'),
('fr', 'Français'),
('zh', '中文'),
('es', 'Español'),
('ja', '日本語'),
('ar', 'العربية'),
('az', 'Azərbaycanca'),
('bg', 'Български'),
('nan', 'Bân-lâm-gú / Hō-ló-oē'),
('be', 'Беларуская (Акадэмічная)'),
('ca', 'Català'),
('cs', 'Čeština'),
('da', 'Dansk'),
('de', 'Deutsch'),
('et', 'Eesti'),
('el', 'Ελληνικά'),
('eo', 'Esperanto'),
('eu', 'Euskara'),
('fa', 'فارسی'),
('gl', 'Galego'),
('ko', '한국어'),
('hy', 'Հայերեն'),
('hi', 'हिन्दी'),
('hr', 'Hrvatski'),
('id', 'Bahasa Indonesia'),
('it', 'Italiano'),
('he', 'עברית'),
('ka', 'ქართული'),
('la', 'Latina'),
('lt', 'Lietuvių'),
('hu', 'Magyar'),
('ms', 'Bahasa Melayu'),
('min', 'Bahaso Minangkabau'),
('nl', 'Nederlands'),
('no', 'Norsk (Bokmål)'),
('nn', 'Norsk (Nynorsk)'),
('ce', 'Нохчийн'),
('uz', 'Oʻzbekcha / Ўзбекча'),
('pl', 'Polski'),
('pt', 'Português'),
('kk', 'Қазақша / Qazaqşa / قازاقشا'),
('ro', 'Română'),
('ru', 'Русский'),
('ceb', 'Sinugboanong Binisaya'),
('sk', 'Slovenčina'),
('sl', 'Slovenščina'),
('sr', 'Српски / Srpski'),
('sh', 'Srpskohrvatski / Српскохрватски'),
('fi', 'Suomi'),
('sv', 'Svenska'),
('th', 'ภาษาไทย'),
('tr', 'Türkçe'),
('uk', 'Українська'),
('ur', 'اردو'),
('vi', 'Tiếng Việt'),
('vo', 'Volapük'),
('war', 'Winaray'),
)


class List(models.Model):
    """List"""

    # Meta
    user = models.ForeignKey(MyUser)
    uuid = models.UUIDField(default=UUID.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    language = models.CharField(choices=LANG_CHOICES, blank=True,
                                max_length=50, default='en')
    # UTM settings
    is_utm_activated = models.BooleanField(default=True)
    utm_medium = models.CharField(blank=True, max_length=50, default='email')
    utm_source = models.CharField(blank=True, max_length=50)
    # Internal usage
    name = models.CharField(max_length=125, blank=True)
    # Visible to subscribers
    title = models.CharField(max_length=125, blank=True)
    from_email = models.CharField(max_length=125, blank=True)
    from_email_verified = models.BooleanField(default=False, blank=True)
    description = models.TextField(blank=True, max_length=550)
    url = models.URLField(max_length=4000, blank=True)
    image = models.ImageField(upload_to='static/uploads/', null=True,
                              blank=True)
    token = models.CharField(default=UUID.uuid4, max_length=50,
                             blank=True, editable=False)

    # custom templates
    subscribe_template = models.TextField(blank=True, max_length=550)
    success_template = models.TextField(blank=True, max_length=550)

    def save(self, *args, **kwargs):
        # Set utm_source when we first created the list
        if self.pk is None:
            self.utm_source = slugify(self.title)
        super(List, self).save(*args, **kwargs)

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

    # Relationship
    list = models.ForeignKey(List)
    # Meta info
    uuid = models.UUIDField(default=UUID.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    validated = models.BooleanField(default=False, blank=True)
    imported = models.BooleanField(default=False, blank=True)
    token_subscribe = models.CharField(default=UUID.uuid4, max_length=50,
                                       blank=True, editable=False)
    token_unsubscribe = models.CharField(default=UUID.uuid4, max_length=50,
                                         blank=True, editable=False)
    # Core info
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    accept_language = models.TextField(blank=True, null=True)
    ip_subscribe = models.GenericIPAddressField(blank=True, null=True)
    ip_validate = models.GenericIPAddressField(blank=True, null=True)
    extra = JSONField(blank=True, null=True)
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
        return settings.BASE_URL+reverse('subscriber-management-subscriber-validate',
                                         kwargs={'uuid':self.uuid,
                                                 'token':self.token_subscribe})

    def unsubscribe_link(self):
        return settings.BASE_URL+reverse('subscriber-management-subscriber-unsubscribe',
                                         kwargs={'uuid':self.uuid,
                                                 'token':self.token_unsubscribe})

    def human_tz(self):
        return timezone.human_timezone(self.timezone)
