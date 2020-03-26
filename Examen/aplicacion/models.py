from django.db import models

class paciente(models.Model):
    nombreP = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.nombreP


class medico(models.Model):
    nombreM = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.nombreM

class receta(models.Model):
    medico = models.ForeignKey(medico, on_delete=models.CASCADE)
    paciente = models.ForeignKey(paciente, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.id) + "\t" + str(self.medico)+ "\t" + str(self.paciente)
