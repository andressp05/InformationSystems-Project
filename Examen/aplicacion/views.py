from django.shortcuts import render

from django.http import HttpResponse
from aplicacion.models import medico,paciente,receta

def index(request):
    return HttpResponse("Rango says hey there partner!")

def receta_select(request):
    recetas = receta.objects.order_by('-id')[:3]
    context_dict = {'recetas': recetas}
    return render(request, "aplicacion/receta.html", context_dict)
