from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
import hashlib
from django.conf import settings
from django.urls import reverse


class MyUserManager(BaseUserManager):
    def create_user(self, full_name, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        m = hashlib.md5()
        m.update(email.encode('utf-8'))

        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            md5_hash_email=str(m.hexdigest()),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email=email,
            password=password,
            full_name="admin"
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, unique=False)
    md5_hash_email = models.CharField(max_length=50, unique=False, blank=True)
    recover_id = models.CharField(max_length=50, unique=False, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.is_admin

    def recovery_link(self):
        return settings.BASE_URL+reverse('user_recovery', kwargs={'uuid':self.recover_id})
