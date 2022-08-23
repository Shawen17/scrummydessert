from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations=True
    now = timezone.now()
    def _create_user(self,email,password,**extra_fields):
        if not email:
            raise ValueError('the given email must be set')
        email=self.normalize_email(email)
        user=self.model(email=email,
        is_active=True,last_login=timezone.now(),
        date_joined=timezone.now(),**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_staff',False)
        return self._create_user(email,password,**extra_fields)

    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email,password,**extra_fields)


class LowercaseEmailField(models.EmailField):
    def to_python(self,value):
        value=super(LowercaseEmailField,self).to_python(value)
        if isinstance(value,str):
            return value.lower()
        return value