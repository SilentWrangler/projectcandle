from django.urls import path

from . import views

urlpatterns = [
    path('post/new',views.make_post, name = 'newpost'),
    path('post/<int:pk>',views.view_post, name = 'showpost'),
    path('post/<int:pk>/reply',views.view_post, name = 'reply'),
]
