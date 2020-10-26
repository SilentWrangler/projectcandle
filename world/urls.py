from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/getworld/<int:id>', views.getworld, name='getworld'),
    path('api/generate/', views.create_world, name='create_world'),
    path('api/getcell', views.get_cell_info, name = 'get_cell_info'),
    path('api/pop/<int:id>',views.get_pop_info, name = 'get_pop_info')
]