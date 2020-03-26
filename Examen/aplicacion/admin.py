from django.contrib import admin
from aplicacion.models import paciente, medico, receta

admin.site.register(paciente)
admin.site.register(medico)
admin.site.register(receta)
