from django.urls import path, include

from . import views


urlpatterns = [
    path('',views.home,name='home'),
    path('accounts/signup/',views.signup, name = 'signup'),
    path('accounts/activate/<uid>/<token>',views.activate,name = 'activate'),
    path('accounts/activationsent/',views.asnt,name = 'activation_sent'),
    path('accounts/',include('django.contrib.auth.urls')),
    path('accounts/profile/', views.profile, name = 'profile'),
    path('accounts/<int:pk>/', views.PlayerPage.as_view(), name = 'player_page'),
    path('accounts/reset_token/',views.reset_token, name = 'reset_token'),
    path('characters/<int:charid>', views.char_profile, name = 'char_profile'),
    path('characters/<int:charid>/rename/', views.request_rename, name = 'char_rename'),
    path('characters/makeimage/',views.char_image,name = 'char_image'),
    path('characters/change/',views.PickChar.as_view(), name = 'char_change'),
    path('characters/new/',views.MakeChar.as_view(), name = 'char_new'),
    path('characters/renames/',views.Renames.as_view(), name = 'char_renames'),
    path('characters/renames/<int:pk>/',views.RenameDetail.as_view(), name = 'char_renames_details'),
    path('characters/renames/<int:id>/approve/',views.rename_approve, name = 'char_renames_approve'),
    path('characters/renames/<int:id>/reject/',views.rename_reject, name = 'char_renames_reject'),
    ]