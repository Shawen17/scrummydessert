from django.contrib import admin
from .models import User,Order,DestinationCharge,Charge,Vendor,Transaction,Contact,Response,DispatcherperDestination
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomeUserChangeForm,SignupForm,SendEmailForm
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
import csv
from django.http import HttpResponse



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','vendor')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    form = CustomeUserChangeForm
    add_form = SignupForm
    
    
    list_display=['email','first_name','last_name','vendor','is_staff']
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display=['ref','item','ordered_by','ordered_on','delivery_date','delivery_address','contact_number','amount','paid','packed','dispatch_partner','delivered']
    ordering=('-delivery_date','-ordered_on')
    actions=['mark_packed','export_order']

    def mark_packed(self,request,queryset):
        queryset.update(packed=True)

    def export_order(self,request,queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow(['Ref','Items','Customer','Delivery Date','Address','Phone Number','Dispatch Partner'])
        orders = queryset.values_list('ref','item','ordered_by','delivery_date','delivery_address','contact_number','dispatch_partner')
        for order in orders:
            writer.writerow(order)
        return response

    export_order.short_description = 'Export Orders'
    mark_packed.short_description = "Mark as Packed"


@admin.register(Vendor)
class VendorAdmin(ModelAdmin):
    list_display=['event_date','order','event_address','planner_contact','state','total_amount','amount_paid','balance']
    ordering=('event_date',)
    search_fields=('planner_contact',)
    readonly_fields=('balance',)
    fields=('event_date','order','event_address','planner_contact','state','total_amount','amount_paid','balance')

    def balance(self,obj):
        if obj.total_amount and obj.amount_paid:
            return obj.total_amount - obj.amount_paid


@admin.register(Charge)
class ChargeAdmin(ModelAdmin):
    list_display=['size','charge','image']

@admin.register(DestinationCharge)
class DestinationChargeAdmin(ModelAdmin):
    list_display=['city','charge']

@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display=['ref','email','made_on','items','amount','verified']

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display =('subject','email','date','body','status')
    ordering =('-date','subject',)
    search_fields = ('email',)
    actions=['send_email']


    def send_email(self, request, queryset):
        selected=[]
        queryset.update(status=True)
        for i in queryset:

            selected.append(i.email)
        request.session['selected'] = selected
        form = SendEmailForm(initial={'users': queryset})
        return render(request, 'scummy/send_email.html', {'form': form})

    send_email.short_description = "Reply Message"


@admin.register(Response)
class ResponseAdmin(ModelAdmin):
    list_display=('email','comment','replied_on','replied_by')
    ordering=('-replied_on',)
    search_fields=('email','replied_by')
    

@admin.register(DispatcherperDestination)
class DispatcherperDestinationAdmin(ModelAdmin):
    list_display=('name','email','location')
    ordering=('name',)
    search_fields=('email',)






# admin.site.unregister(User)
# admin.site.register(User,UserAdmin)