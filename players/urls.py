from django.urls import path, include

from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('accounts/signup/',views.signup, name = 'signup'),
    path('accounts/activate/<uid>/<token>',views.activate,name = 'activate'),
    path('accounts/activationsent/',views.asnt,name = 'activation_sent'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name = 'profile'),
    path('accounts/reset_token/',views.reset_token, name = 'reset_token'),
    path('characters/<int:charid>', views.char_profile, name = 'char_profile'),
    ]