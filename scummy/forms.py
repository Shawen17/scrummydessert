from .models import Order,User,Contact,Response,Vendor
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm,UserChangeForm,AuthenticationForm
from django import forms

class OrderForm(ModelForm):
    
    delivery_address=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Full Address'}))

    class Meta:
        model=Order
        fields=('contact_number','delivery_address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_number'].widget.attrs.update(size='40',title='phone number')
        

class SignupForm(UserCreationForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password Again'}))
    email = forms.EmailField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    first_name = forms.CharField(max_length= 100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}))
    last_name = forms.CharField(max_length= 100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}))
    
    
    
    class Meta:
        model=User
        fields=('first_name','last_name','email','password1','password2')



class CustomeUserChangeForm(UserChangeForm):
    
        

    class Meta:
        model = User
        exclude=('password1','password2')

class LoginForm(ModelForm):
    email = forms.EmailField(max_length=100,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))

    class Meta:
        model=User
        fields=('email','password')


class ContactForm(ModelForm):
     body=forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','placeholder':'Enter Text'}))

     class Meta:
        model=Contact
        fields=('body',)

class SendEmailForm(ModelForm):
    comment = forms.CharField(widget=forms.Textarea)

    class Meta:
        model=Response
        fields=('comment',)

class VendorForm(ModelForm):
    event_address=forms.CharField(widget=forms.Textarea)

    class Meta:
        model=Vendor
        fields=('event_address',)