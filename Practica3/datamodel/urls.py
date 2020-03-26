# Author: Andres
from django.urls import path
from datamodel import views

app_name = 'datamodel'

urlpatterns = [
    path('', views.index, name='index'),
]
