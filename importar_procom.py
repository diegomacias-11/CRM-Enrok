import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # 👈 o prueba 'CRM.config.settings' si vuelve a fallar
import django
django.setup()

from django.contrib.auth.models import User
from clientes.models import Cliente
import csv

ruta_csv = r"C:\Users\diego\OneDrive\Procom.csv"

def porcentaje_a_entero(valor):
    if not valor or valor.strip() == '':
        return None
    try:
        return float(valor) * 100
    except ValueError:
        return None

def importar_clientes():
    with open(ruta_csv, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for fila in reader:
            fila = {k.strip(): (v.strip() if v else v) for k, v in fila.items()}

            username = fila.get('user')
            if not username:
                print("⚠️ Cliente sin nombre de usuario, omitido.")
                continue

            username = username.lower().replace(" ", "_")
            email = f"{username}@clientes.com"
            password = "Enrok2025*"

            user, created = User.objects.get_or_create(username=username, defaults={'email': email})
            if created:
                user.set_password(password)
                user.save()

            Cliente.objects.create(
                servicio=fila.get('servicio'),
                comision_procom=porcentaje_a_entero(fila.get('comision_procom')),
                nombre=fila.get('nombre'),
                tipo_persona=fila.get('tipo_persona'),
                factura=fila.get('factura'),
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
                usuario=user
            )

            print(f"✅ Cliente creado: {fila.get('nombre')} (usuario: {username})")

    print("🎉 Importación completada.")

if __name__ == "__main__":
    importar_clientes()
