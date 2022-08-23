"""store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from  django.conf import settings
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from scummy import views
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('test/',views.test,name='testing'),
    path('admin/reply',views.reply_contact,name='reply-contact'),
    # path('accounts/', include('scummy.urls')),
    path('signup/',views.signupuser,name='signupuser'),
    path('login/',views.loginuser,name='loginuser'),
    path('login/partner',views.login_partner,name='login_partner'),
    path('partner/orders',views.display_order,name='display_order'),
    path('partner/dispatched',views.mark_dispatched,name='mark_dispatched'),
    path('order/',views.place_order,name='order'),
    path('logout/',views.logoutuser,name='logoutuser'),
    path('transaction/',views.initiate_payment,name='initiate-payment'),
    path('<str:ref>/transaction',views.verify_payment,name='verify-payment'),
    path('contactus/',views.contactus,name='contact'),
    path('book/event',views.book_event,name='booking'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'), 
    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path('accounts/', include('allauth.urls')),
    path('password_reset/', views.password_reset_request, name='password_reset'),
]


urlpatterns += static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)