from django.shortcuts import render,get_object_or_404, redirect
from .models import User,Order,Transaction,Vendor,Charge,DestinationCharge,states
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django import template
from django.contrib.auth.forms import AuthenticationForm
from .forms import OrderForm,SignupForm,LoginForm,ContactForm,SendEmailForm,VendorForm
from django.http import HttpResponseRedirect,HttpResponse
from datetime import date


def home(request):
    hostname=request.get_host().split('//')[0]
    subdomain=hostname.split('.')[0]
    request.session['subdomain']=subdomain
    if subdomain=='merchant':
        if request.user.is_authenticated:
            return redirect('display_order')

        return render(request,'scummy/merchant_home.html')
        
    return render(request,'scummy/home.html')

def signupuser(request):
    
    if request.method == 'POST':
        form = SignupForm()
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.error(request,'Email Already Exist')
                return redirect('signupuser')
                
            else:
                first_name=request.POST['first_name']
                last_name=request.POST['last_name']
                email=request.POST['email']
                password=request.POST['password1']
                data={
                    'first_name':first_name,
                    'last_name':last_name,
                    'email':email,
                    'password':password
                }
                  
                user=User.objects.create_user(**data)
                user1= authenticate(email=email,password=password)
                login(request,user)
                messages.success(request,f'first time customer!! {user.first_name}, you will never be disapointed for your patronage')
                return redirect('order')
                                
        else:
            messages.error(request,'Password does not match')
            return redirect('signupuser')
            
    else:
        form = SignupForm()
        return render(request, 'scummy/signup.html')


def loginuser(request):
    
    if request.session.get('subdomain')=='merchant':
        if request.method=="GET":
            return render(request,'scummy/merchant_login.html')
        user= authenticate(request, email=request.POST['email'],password=request.POST['password'])
        check=User.objects.get(email=user).last_login
        partner=User.objects.get(email=user).vendor
        if partner==True:
            login(request,user)
            orders=Order.objects.filter(packed=True)
            return render(request,'scummy/dispatch.html',{'orders':orders})
        else:
            message.error(request,'you are not a registered partner')
            return redirect('home')

    if request.method=="GET":
        return render(request,'scummy/login.html')
    user= authenticate(request, email=request.POST['email'],password=request.POST['password'])
    check=User.objects.get(email=user).last_login
    if user is None:
        messages.error(request,'Username or Password Incorrect')
        return redirect('loginuser')
            
    else:
        login(request,user)
        if check:
            return redirect('order')
        messages.success(request,f'first time customer!! {user.first_name}, you will never be disapointed for your patronage')
        return redirect('order')

def login_partner(request):
    if request.method=="GET":
        return render(request,'scummy/merchant_login.html')
    user= authenticate(request, email=request.POST['email'],password=request.POST['password'])
    partner=User.objects.get(email=user).vendor
    
    if request.session.get('subdomain')=='merchant':
        if partner==True:
            login(request,user)
            return redirect('display_order') 
        else:
            message.error(request,'you are not a registered partner')
            return render(request,'scummy/merchant_login.html')


@login_required(login_url='/login/')
def display_order(request):
    orders=Order.objects.filter(packed=True,delivered=False)
    return render(request,'scummy/dispatch.html',{'orders':orders})


@login_required(login_url='/login/')
def logoutuser(request):
    logout(request)
    return redirect('home')

@login_required(login_url='/login/')
def place_order(request):
    user=request.user
    today=date.today()
    destination=DestinationCharge.objects.all()
    unit_price=Charge.objects.all()
    if request.method=='GET':
        return render(request,'scummy/order.html',{'form':OrderForm(),'destination':destination})
    form=OrderForm(request.POST)
    city=request.POST.get('city',1)
    delivery_date=request.POST.get('delivery_date',1)
    
    if city==1:
        return HttpResponse('kindly go back and fill all required fields')
    destination_charge=DestinationCharge.objects.get(city=city).charge
    picks=request.POST.getlist('chkbox')
    quantity=request.POST.getlist('quant')
    quantity=[int(i) for i in quantity if i!='']
    if len(picks)!=len(quantity):
        return HttpResponse('choose size for the corresponding quantity')
    item_dict=dict(zip(picks,quantity))
    cost=0
    for i,j in item_dict.items():
        d=unit_price.get(size=i).charge*j
        cost+=d
    amount=cost+destination_charge
    request.session['cost']=cost
    cart_items=sum(quantity)
    items=[]
    for i,j in  enumerate(list(item_dict),1):
        a=f'{i}.  {j}-{item_dict[j]}'
        items.append(a)
    if form.is_valid():
        new_order=form.save(commit=False)
        new_order.item=item_dict
        new_order.amount=amount
        new_order.delivery_date=delivery_date
        new_order.ordered_by=user
        new_order.save()
        
        return render(request,'scummy/checkout.html',{'dispatch':destination_charge,'cost':cost,'total':amount,'items':items,'cart_items':cart_items,'today':today})
    else:
        return HttpResponse('error processing form')

@login_required(login_url='/login/')
def initiate_payment(request):
    
    email=request.user
    order=Order.objects.filter(ordered_by=email).last()
    items=order.item
    cost=request.session.get('cost')
    amount=order.amount
    vat=0.075*cost
    if amount>=2500:
        paystack_charge=100 + (0.015*amount)
    else:
        paystack_charge=(0.015*amount)
    paystack_charge=round(paystack_charge,2)
    total=paystack_charge+amount+vat

    data={
        'email':email,
        'items':items,
        'amount':total
    }
    transaction=Transaction.objects.create(**data)
    return render(request,'scummy/make_payment.html',{'transaction':transaction,'paystack_public_key':settings.PAYSTACK_PUBLIC_KEY,
    'amount':amount,'vat':vat,'charge':paystack_charge,'total':total})

@login_required(login_url='/login/')
def verify_payment(request,ref):
    
    payment = get_object_or_404(Transaction,ref=ref)
    verified = payment.verify_payment()
    
    if verified:
        payment.verified=True
        payment.save(update_fields=['verified'])
        order=Order.objects.filter(ordered_by=request.user).last()
        order.paid=True
        order.save(update_fields=['paid'])
        messages.success(request, 'Payment Successful,you will be contacted soon for delivery')
    else:
        messages.error(request,"Payment Failed.")
    return redirect('home')


def contactus(request):
    user=request.user
    com_list=['event planner','enquiry','complaint','report','others']
    if request.method=='GET':
        return render(request,'scummy/contact.html',{'form':ContactForm(),'com_list':com_list})
    form=ContactForm(request.POST)
    if user.is_authenticated:
        email=user
    else:
        email=request.POST.get('email',1)
    subject=request.POST.get('com_list')
    body=request.POST.get('body')
    if form.is_valid():
        new_contact=form.save(commit=False)
        new_contact.email=email
        new_contact.subject=subject
        new_contact.body=body
        new_contact.save()
        messages.success(request,'we will get back to you soon')
        return redirect('home')
    else:
        return HttpResponse('bad request')


@login_required(login_url='/login/')
def reply_contact(request):

    shape=request.session.get('selected')

    if request.method=='POST':
        form=SendEmailForm(request.POST)
        if form.is_valid:
            new_form=form.save(commit=False)
            new_form.email=shape[0]
            new_form.replied_by=request.user.first_name
            new_form.comment=form.cleaned_data.get('comment')
            new_form.save()

            if len(shape)>1:
                comment=form.cleaned_data.get('comment')
                for i in shape[1:]:
                    data={
                        'email':i,
                        'comment':comment,
                        'replied_by':request.user.first_name
                    }
                    response=Response.objects.create(**data)

            
            msg=EmailMultiAlternatives('Scrummy Dessert',form.cleaned_data.get('comment'),'customercare@scrummy.com',bcc=shape)
            msg.send()
            messages.success(request,'reply sent')
            del request.session['selected']
            return redirect('/admin/scummy/contact')

def book_event(request):
    regions=['lagos','ogun','oyo']
    if request.method=='GET':
        return render(request,'scummy/vendor.html',{'form':VendorForm(),'regions':regions})
    form=VendorForm(request.POST)
    event_date=request.POST.get('event_date')
    event_address=request.POST.get('event_address')
    planner_contact=request.POST.get('planner_contact')
    state=request.POST.get('state',1)
    if state==1:
        return HttpResponse('Kindly go back and choose state of event')
    if form.is_valid():
        new_booking=form.save(commit=False)
        new_booking.event_date=event_date
        new_booking.event_address=event_address
        new_booking.planner_contact=planner_contact
        new_booking.state=state
        
        new_booking.save()
        messages.success(request,'we will get back to you soon')
        return redirect('home')
    messages.error(request,'fill form properly')
    return redirect('booking')


def mark_dispatched(request):
    check_ids=request.POST.getlist("chk[]")
    check_ids=[int(i) for i in check_ids]
    orders=Order.objects.filter(id__in=check_ids).update(delivered=True)
    return redirect('display_order')