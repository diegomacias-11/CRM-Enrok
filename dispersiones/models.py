from django.db import models
from django.utils import timezone
from clientes.models import Cliente
from decimal import Decimal

class Dispersion(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    factura = models.CharField(max_length=100)
    num_factura = models.CharField(max_length=100, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    comision = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    num_factura_honorarios = models.CharField(max_length=100, blank=True, null=True)
    total_honorarios = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    estatus_proceso = models.CharField(max_length=50)
    comentarios = models.TextField(blank=True, null=True)
    num_periodo = models.CharField(max_length=50, blank=True, null=True)
    estatus_periodo = models.CharField(max_length=50)
    estatus_pago = models.CharField(max_length=50, default="Pendiente")
    comision_procom = models.DecimalField(max_digits=5, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Solo recalculamos si hay monto y cliente
        if self.cliente and self.monto is not None:
            self.comision_procom = Decimal(str(self.cliente.comision_procom))
            self.comision = (self.comision_procom / Decimal('100')) * self.monto
            self.total_honorarios = self.comision + (self.comision * Decimal('0.16'))
        
        # ¡No tocamos pagado_checkbox!
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cliente} - {self.factura}"

    @property
    def comisiones_pagadas(self):
        # Devuelve True si todas las comisiones asociadas están en 'Pagado'
        return self.comisiones.exists() and all(c.estatus == "Pagado" for c in self.comisiones.all())

    class Meta:
        permissions = [
            ("actualizar_estatus_dispersion", "Puede actualizar estatus de pago en dispersiones"),
        ]
