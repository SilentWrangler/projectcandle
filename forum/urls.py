from django.urls import path

from . import views

urlpatterns = [
    path('post/new',views.make_post, name = 'newpost'),
    path('post/<int:pk>',views.view_post, name = 'showpost'),
    path('post/<int:pk>/reply',views.make_reply, name = 'reply'),
    path('categories',views.Categories.as_view(),name = 'cats'),
    path('category/<int:pk>', views.category, name = 'cat'),
]
