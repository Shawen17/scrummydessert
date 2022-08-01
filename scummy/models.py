from __future__ import unicode_literals

from django.contrib.postgres.fields import JSONField 
from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from datetime import datetime,date
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager
from .paystack import PayStack
from store.settings import STATIC_ROOT
from django.utils import timezone
import os
import pandas as pd
import secrets

com_list=(
    ('event planner','Event planner'),
    ('enquiry','Enquiry'),
    ('complaint','Complaint'),
    ('report','Report'),
    ('others','Others')
)

file_path = os.path.join(STATIC_ROOT,'scummy\\state.xlsx')
df = pd.read_excel(file_path)
df1= zip(df.value,df.representation)
states=[]
for i,j in df1:
    states.append((i,j))


class User(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(_('email address'),unique=True)
    first_name=models.CharField(_('first name'),max_length=50,blank=True)
    last_name=models.CharField(_('last name'),max_length=50,blank=True)
    date_joined=models.DateTimeField(_('date joined'),null=True,blank=True)
    is_active=models.BooleanField(_('active'),default=True)
    is_staff=models.BooleanField(_('staff'),default=False)
    is_superuser=models.BooleanField(_('superuser'),default=False)
    vendor=models.BooleanField(_('vendor'),default=False)

    objects=UserManager()

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    class Meta:
        verbose_name=_('user')
        verbose_name_plural=_('users')


    def __str__(self):
        return self.email

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name



class Order(models.Model):
    item=models.JSONField(default=dict,null=True)
    ordered_by=models.CharField(max_length=130,null=True)
    ordered_on=models.DateTimeField(auto_now_add=True)
    delivery_date=models.DateField(null=True)
    delivery_address=models.TextField()
    contact_number=models.BigIntegerField()
    amount=models.IntegerField(null=True)
    paid=models.BooleanField(default=False)
    packed=models.BooleanField(default=False)
    delivered=models.BooleanField(default=False)

    def __str__(self):
        return self.item

class Vendor(models.Model):
    event_date=models.DateField()
    order=models.TextField(null=True)
    event_address=models.TextField()
    planner_contact=models.BigIntegerField()
    state=models.CharField(max_length=50,null=True)
    total_amount=models.IntegerField(null=True)
    amount_paid=models.IntegerField(null=True,blank=True)
    

    def __str__(self):
        return self.event_address

    



class Charge(models.Model):
    size=models.CharField(max_length=50)
    charge=models.IntegerField()

    def __str__(self):
        return self.size


class DestinationCharge(models.Model):
    city=models.CharField(max_length=300)
    charge=models.IntegerField()

    def __str__(self):
        return self.city

class Transaction(models.Model):
    ref = models.CharField( max_length=200,blank=True,null=True)
    email=models.EmailField(default='')
    made_on = models.DateTimeField(auto_now_add=True)
    items=models.JSONField(default=dict,null=True)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    verified=models.BooleanField(default=False)
    

    def __str__(self):
        return self.ref

    def save(self, *args, **kwargs):
        while not self.ref:
            ref = secrets.token_urlsafe(16)
            object_with_similar_ref = Transaction.objects.filter(ref=ref)
            if not object_with_similar_ref:
                self.ref=ref
        super().save(*args, **kwargs)

    def amount_value(self):
        return self.amount * 100

    def verify_payment(self):
        paystack =PayStack()
        status,result = paystack.verify_payment(self.ref,self.amount)
        if status:
            self.verified =True
            self.save()
        if self.verified:
            return True
        return False

class Contact(models.Model):
    subject= models.CharField(max_length=20,choices=com_list)
    email= models.EmailField(max_length=150)
    body=models.TextField()
    date=models.DateTimeField(auto_now_add=True)
    status=models.BooleanField(default=False)


    def __str__(self):
        return self.subject
        
class Response(models.Model):
    email=models.EmailField(default='')
    comment=models.TextField()
    replied_on=models.DateTimeField(auto_now_add=True)
    replied_by=models.CharField(max_length=50)
