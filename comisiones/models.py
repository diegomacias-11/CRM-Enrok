from django.db import models
from dispersiones.models import Dispersion
from clientes.models import Cliente

class Comision(models.Model):
    dispersion = models.ForeignKey(Dispersion, on_delete=models.CASCADE, related_name="comisiones")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    comisionista = models.CharField(max_length=255)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estatus = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f"{self.comisionista} - {self.monto}"

    @property
    def cliente_liberado(self):
        # Obtenemos todas las comisiones del mismo cliente en el mismo mes/año
        comisiones_mes = Comision.objects.filter(
            cliente=self.cliente,
            fecha__month=self.fecha.month,
            fecha__year=self.fecha.year
        )
        # Si todas están pagadas, devolvemos True
        return comisiones_mes.exists() and all(c.estatus == "Pagado" for c in comisiones_mes)

class Pago(models.Model):
    comisionista = models.CharField(max_length=255)
    mes = models.IntegerField()
    anio = models.IntegerField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateField()
    creado = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.comisionista} - {self.monto} ({self.fecha_pago})"