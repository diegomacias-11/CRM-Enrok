from django.db import models
from clientes.models import Cliente
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings


def ruta_materialidad(instance, filename):
    import os
    from django.utils import timezone

    carpeta_cliente = instance.cliente.nombre
    tipo_doc = instance.tipo_documento.replace(" ", "_").lower()

    # Fecha en formato YYYYMMDD-HHMM
    fecha = timezone.now().strftime("%Y%m%d-%H%M")

    # Nueva ruta con formato: Cliente/tipo_documento_fecha.extensión
    nombre, extension = os.path.splitext(filename)
    nuevo_nombre = f"{tipo_doc}_{fecha}{extension}"

    return os.path.join(carpeta_cliente, nuevo_nombre)

class DocumentoMaterialidad(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='documentos_materialidad'
    )
    tipo_documento = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to=ruta_materialidad)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.tipo_documento}"

    class Meta:
        verbose_name = "Documento de Materialidad"
        verbose_name_plural = "Documentos de Materialidad"
        ordering = ['cliente__nombre', 'tipo_documento']


@receiver(post_delete, sender=DocumentoMaterialidad)
def eliminar_archivo_materialidad(sender, instance, **kwargs):
    """Elimina el archivo físico del disco cuando se borra el registro."""
    if instance.archivo:
        try:
            instance.archivo.delete(save=False)
        except Exception as e:
            print(f"⚠️ No se pudo eliminar el archivo: {e}")
