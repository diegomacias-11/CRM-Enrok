from django.db.models.signals import post_save
from django.dispatch import receiver
from dispersiones.models import Dispersion
from .models import Comision
from decimal import Decimal


@receiver(post_save, sender=Dispersion)
def crear_comisiones(sender, instance, created, **kwargs):
    """
    Cada vez que se crea una dispersión,
    se generan automáticamente las comisiones según los comisionistas del cliente.
    """
    if not created:  # Solo cuando es un nuevo registro
        return

    cliente = instance.cliente  

    # Recorremos los 9 posibles comisionistas
    for i in range(1, 10):
        comisionista = getattr(cliente, f"comisionista_{i}", None)
        porcentaje = getattr(cliente, f"porcentaje_{i}", None)

        if comisionista and porcentaje:
            try:
                porcentaje_decimal = Decimal(porcentaje) / 100
                monto = instance.comision * porcentaje_decimal

                Comision.objects.create(
                    dispersion=instance,
                    cliente=cliente,
                    comisionista=comisionista,
                    porcentaje=porcentaje,
                    monto=monto,
                    estatus='Pendiente',
                )
            except Exception as e:
                print(f"⚠️ Error creando comisión para {comisionista}: {e}")
