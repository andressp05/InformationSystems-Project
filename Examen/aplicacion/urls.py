from django.urls import path
from aplicacion import views

app_name = 'aplicacion'

urlpatterns = [
    path('', views.index, name='index'),
    path('receta', views.receta_select, name='receta'),
]
