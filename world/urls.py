from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='map'),
    path('api/getworld/<int:id>', views.getworld, name='getworld'),
    path('api/generate/', views.create_world, name='create_world'),
    path('api/getcell', views.get_cell_info, name = 'get_cell_info'),
    path('api/pop/<int:id>',views.get_pop_info, name = 'get_pop_info'),
    path('api/citylist/<int:worldid>',views.get_world_cities, name = 'citylist'),
    path('api/addresources/<int:worldid>', views.world_populate_res, name='add_res'),
    path('api/rmresources/<int:worldid>', views.strip_resources, name='rm_res'),
]