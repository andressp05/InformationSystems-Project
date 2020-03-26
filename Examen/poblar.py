import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'proyecto.settings')

django.setup()
from aplicacion.models import paciente, medico, receta


def poblar():
    m1 = medico(nombreM = 'medico1')
    m2 = medico(nombreM = 'medico2')
    m3 = medico(nombreM = 'medico3')
    m4 = medico(nombreM = 'medico4')
    m1.save()
    m2.save()
    m3.save()
    m4.save()

    p1 = paciente(nombreP = 'paciente1')
    p2 = paciente(nombreP = 'paciente2')
    p1.save()
    p2.save()

    r1 = receta(medico = m1, paciente = p1)
    r2 = receta(medico = m2, paciente = p1)
    r3 = receta(medico = m1, paciente = p2)
    r4 = receta(medico = m2, paciente = p2)
    r5 = receta(medico = m3, paciente = p2)
    r1.save()
    r2.save()
    r3.save()
    r4.save()
    r5.save()


# Start execution here!
if __name__ == '__main__':
    print('Iniciando el script de Poblar Aplicacion...')
    poblar()
