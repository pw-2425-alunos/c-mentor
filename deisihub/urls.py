
from django.urls import path
from . import views


urlpatterns = [
    path('', views.identifica_view, name = 'identifica'),
    path('presencas/', views.presencas_view, name = 'presencas'),
]



