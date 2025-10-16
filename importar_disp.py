import os
import django
import csv
from decimal import Decimal
from datetime import datetime

# --- Configuración para acceder al entorno Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # 👈 ajusta 'config' al nombre de tu proyecto
django.setup()

from dispersiones.models import Dispersion
from clientes.models import Cliente

# --- Ruta del archivo ---
CSV_PATH = r"C:\Users\diego\OneDrive\disp_sep.csv"

def importar_dispersiones():
    total = 0
    errores = 0

    try:
        with open(CSV_PATH, newline='', encoding='latin-1') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Cliente
                    nombre_cliente = row['cliente'].strip()
                    cliente = Cliente.objects.get(nombre__iexact=nombre_cliente)

                    # Fecha (ya viene limpia)
                    fecha_str = row['fecha'].strip()
                    if '/' in fecha_str:
                        fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
                    else:
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')

                    # Monto (ya limpio)
                    monto = Decimal(row['monto'].strip())

                    # Columnas adicionales
                    num_factura = row.get('num_factura', '').strip()
                    num_factura_honorarios = row.get('num_factura_honorarios', '').strip()
                    factura = row.get('factura', '').strip()
                    comentarios = row.get('comentarios', '').strip()
                    estatus = row.get('estatus', 'Pendiente').strip() or "Pendiente"
                    estatus_periodo = row.get('estatus_periodo', 'Activo').strip() or "Activo"

                    # Crear dispersión
                    dispersion = Dispersion(
                        fecha=fecha,
                        cliente=cliente,
                        factura=factura,
                        comentarios=comentarios,
                        num_factura=num_factura,
                        monto=monto,
                        num_factura_honorarios=num_factura_honorarios,
                        estatus=estatus,
                        estatus_periodo=estatus_periodo,
                        estatus_pago="Pendiente"
                    )
                    dispersion.save()  # 🔥 activa tus signals
                    total += 1
                    print(f"✅ Dispersión creada para {cliente} por ${monto}")

                except Cliente.DoesNotExist:
                    errores += 1
                    print(f"⚠️ Cliente no encontrado: {row['cliente']}")
                except Exception as e:
                    errores += 1
                    print(f"⚠️ Error con {row}: {e}")

        print(f"\n✅ Carga completada: {total} dispersiones creadas, {errores} con error.")

    except FileNotFoundError:
        print("❌ No se encontró el archivo CSV especificado.")

if __name__ == "__main__":
    importar_dispersiones()
