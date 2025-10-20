from django.db import models

class Cliente(models.Model):
    servicio = models.CharField(max_length=100)
    comision_procom = models.FloatField(blank=True, null=True)
    factura = models.CharField(blank=True, null=True)
    nombre = models.CharField(max_length=150)
    tipo_persona = models.CharField(max_length=50)
    utilidad_enrok = models.FloatField(blank=True, null=True)
    # Campos para comisionistas y sus porcentajes
    comisionista_1 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_1 = models.FloatField(blank=True, null=True)

    comisionista_2 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_2 = models.FloatField(blank=True, null=True)

    comisionista_3 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_3 = models.FloatField(blank=True, null=True)

    comisionista_4 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_4 = models.FloatField(blank=True, null=True)

    comisionista_5 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_5 = models.FloatField(blank=True, null=True)

    comisionista_6 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_6 = models.FloatField(blank=True, null=True)

    comisionista_7 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_7 = models.FloatField(blank=True, null=True)

    comisionista_8 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_8 = models.FloatField(blank=True, null=True)

    comisionista_9 = models.CharField(max_length=100, blank=True, null=True)
    porcentaje_9 = models.FloatField(blank=True, null=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.servicio}"
