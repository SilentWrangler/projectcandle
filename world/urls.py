from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/getworld/<int:id>', views.getworld, name='getworld'),
]