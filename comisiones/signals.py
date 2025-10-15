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
    # 👇 Agregar utilidad Enrok (solo una vez)
 # 👇 Crear la comisión de Enrok igual que las demás
    try:
        porcentaje_enrok = getattr(cliente, "utilidad_enrok", None)
        if porcentaje_enrok:
            porcentaje_decimal = Decimal(porcentaje_enrok) / 100
            monto = instance.comision * porcentaje_decimal

            Comision.objects.create(
                dispersion=instance,
                cliente=cliente,
                comisionista="Enrok",
                porcentaje=Decimal(porcentaje_enrok),
                monto=monto,
                estatus='Pendiente',
            )
            print(f"✅ Comisión creada para Enrok: {porcentaje_enrok}% → ${monto}")
    except Exception as e:
        print(f"⚠️ Error creando comisión Enrok: {e}")
        
@receiver(post_save, sender=Dispersion)
def actualizar_estatus_comisiones(sender, instance, **kwargs):
    """
    Cada vez que se guarda una dispersión (nueva o editada),
    se revisan todas las dispersiones del cliente en el mismo mes/año.
    Si todas están pagadas, se liberan las comisiones.
    Si alguna está pendiente, se reflejan los estatus reales.
    """
    cliente = instance.cliente
    mes = instance.fecha.month
    anio = instance.fecha.year

    # Traemos todas las dispersiones de ese cliente en el mismo mes/año
    todas_dispersiones = Dispersion.objects.filter(
        cliente=cliente,
        fecha__month=mes,
        fecha__year=anio
    )

    if not todas_dispersiones.exists():
        return

    # Si todas están en "Pagado", liberamos
    if all(d.estatus_pago == "Pagado" for d in todas_dispersiones):
        Comision.objects.filter(
            cliente=cliente,
            dispersion__fecha__month=mes,
            dispersion__fecha__year=anio
        ).update(estatus="Liberado")
    else:
        # Si hay alguna pendiente, reflejamos el estatus real
        for d in todas_dispersiones:
            Comision.objects.filter(dispersion=d).update(estatus=d.estatus_pago)