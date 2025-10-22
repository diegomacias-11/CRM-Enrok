from django.db import models
from clientes.models import Cliente
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
import os


def ruta_activacion(instance, filename):
    """
    Guarda los archivos en:
    Cliente/activacion/tipo_documento_fecha.ext
    """
    carpeta_cliente = instance.cliente.nombre
    carpeta_modulo = "activacion"
    tipo_doc = instance.tipo_documento.replace(" ", "_").lower()
    fecha = timezone.now().strftime("%Y%m%d-%H%M")

    nombre, extension = os.path.splitext(filename)
    nuevo_nombre = f"{tipo_doc}_{fecha}{extension}"

    return os.path.join(carpeta_cliente, carpeta_modulo, nuevo_nombre)


class DocumentoActivacion(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='documentos_activacion'
    )
    tipo_documento = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to=ruta_activacion)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.tipo_documento}"

    class Meta:
        verbose_name = "Documento de Activación"
        verbose_name_plural = "Documentos de Activación"
        ordering = ['cliente__nombre', 'tipo_documento']


@receiver(post_delete, sender=DocumentoActivacion)
def eliminar_archivo_activacion(sender, instance, **kwargs):
    """Elimina el archivo físico del disco cuando se borra el registro."""
    if instance.archivo:
        try:
            instance.archivo.delete(save=False)
        except Exception as e:
            print(f"⚠️ No se pudo eliminar el archivo: {e}")
