import os
import django
import csv

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from clientes.models import Cliente

# Ruta completa de tu CSV
ruta_csv = r"C:\Users\diego\OneDrive\Procom.csv"

# Función para convertir valores a float y multiplicar por 100
def porcentaje_a_entero(valor):
    if not valor or valor.strip() == '':
        return None
    return float(valor) * 100  # Multiplica por 100 al importar

with open(ruta_csv, newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    
    for fila in reader:
        # Limpiar espacios invisibles en los encabezados y valores
        fila = {k.strip(): (v.strip() if v else v) for k, v in fila.items()}

        Cliente.objects.create(
            servicio=fila.get('servicio'),
            comision_procom=porcentaje_a_entero(fila.get('comision_procom')),
            nombre=fila.get('nombre'),
            utilidad_enrok=porcentaje_a_entero(fila.get('utilidad_enrok')),
            comisionista_1=fila.get('comisionista_1'),
            porcentaje_1=porcentaje_a_entero(fila.get('porcentaje_1')),
            comisionista_2=fila.get('comisionista_2'),
            porcentaje_2=porcentaje_a_entero(fila.get('porcentaje_2')),
            comisionista_3=fila.get('comisionista_3'),
            porcentaje_3=porcentaje_a_entero(fila.get('porcentaje_3')),
            comisionista_4=fila.get('comisionista_4'),
            porcentaje_4=porcentaje_a_entero(fila.get('porcentaje_4')),
            comisionista_5=fila.get('comisionista_5'),
            porcentaje_5=porcentaje_a_entero(fila.get('porcentaje_5')),
            comisionista_6=fila.get('comisionista_6'),
            porcentaje_6=porcentaje_a_entero(fila.get('porcentaje_6')),
            comisionista_7=fila.get('comisionista_7'),
            porcentaje_7=porcentaje_a_entero(fila.get('porcentaje_7')),
            comisionista_8=fila.get('comisionista_8'),
            porcentaje_8=porcentaje_a_entero(fila.get('porcentaje_8')),
            comisionista_9=fila.get('comisionista_9'),
            porcentaje_9=porcentaje_a_entero(fila.get('porcentaje_9')),
        )

print("¡Importación completada!")
