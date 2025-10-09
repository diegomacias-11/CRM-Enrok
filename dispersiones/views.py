from django.shortcuts import render, get_object_or_404, redirect
from .models import Dispersion
from .forms import DispersionForm
from datetime import datetime
from clientes.models import Cliente
from django.db.models import Sum
from datetime import datetime

MESES_ES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

def lista_dispersiones(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    now = datetime.now()
    cliente_id = request.GET.get('cliente')

    # Si no vienen parámetros o vienen vacíos, redirigimos con mes/año actuales
    if not mes or not anio:
        return redirect(f"{request.path}?mes={now.month}&anio={now.year}")

    # Normalizamos
    try:
        mes = int(mes)
        if mes < 1 or mes > 12:
            mes = now.month
    except (TypeError, ValueError):
        mes = now.month

    try:
        anio = int(anio)
    except (TypeError, ValueError):
        anio = now.year

    mes_nombre = MESES_ES.get(mes, "")
    # Lista de años disponibles para filtro
    anios = Dispersion.objects.dates('fecha', 'year')
    anios = [y.year for y in anios]

    # Filtro principal
    dispersiones = Dispersion.objects.all().order_by('fecha')
    dispersiones = dispersiones.filter(fecha__month=mes, fecha__year=anio)

    # Lista de clientes y filtrado
    clientes = Cliente.objects.all()
    if cliente_id:
        dispersiones = dispersiones.filter(cliente_id=cliente_id)

    #Suma de dispersiones 
    total_montos = dispersiones.aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'dispersiones/listar.html', {
        'dispersiones': dispersiones,
        'mes': str(mes),
        'mes_nombre': mes_nombre,
        'anio': str(anio),
        'clientes': clientes,       # lista completa para el dropdown
        'cliente': cliente_id,      # cliente seleccionado
        'anios': anios,
        'total_montos': total_montos,
    })

def agregar_dispersion(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    next_url = f'/dispersiones/listar/?mes={mes}&anio={anio}'
    mes = int(request.GET.get('mes', datetime.now().month))
    anio = int(request.GET.get('anio', datetime.now().year))

    if request.method == 'POST':
        form = DispersionForm(request.POST, mes=mes, anio=anio)
        if form.is_valid():
            dispersion = form.save(commit=False)
            dispersion.factura = dispersion.cliente.factura  # ✅ traer factura del cliente
            dispersion.save()
            return redirect(request.POST.get('next', '/dispersiones/listar/'))
    else:
        form = DispersionForm(mes=mes, anio=anio)

    return render(request, 'dispersiones/agregar.html', {
        'form': form,
        'titulo': 'Agregar Nueva Dispersión',
        'next_url': next_url,
    })


def editar_dispersion(request, pk):
    dispersion = get_object_or_404(Dispersion, pk=pk)
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/dispersiones/listar/'))

    if request.method == 'POST':
        form = DispersionForm(request.POST, instance=dispersion)
        if form.is_valid():
            form.save()
            return redirect(request.POST.get('next', '/dispersiones/listar/'))
    else:
        form = DispersionForm(instance=dispersion)
    
    return render(request, 'dispersiones/editar.html', {
        'form': form,
        'titulo': 'Editar Dispersión',
        'dispersion': dispersion,
        'next_url': next_url
    })


def dispersiones_exito(request):
    return render(request, 'dispersiones/exito.html')


def dispersiones_eliminar(request, pk):
    dispersion = get_object_or_404(Dispersion, pk=pk)
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/dispersiones/listar/'))
    dispersion.delete()
    return redirect(next_url)

def actualizar_estatus_dispersion(request):
    if request.method == "POST":
        dispersion_id = int(request.POST.get("id"))
        nuevo_estatus = request.POST.get("estatus_pago")
        
        dispersion = get_object_or_404(Dispersion, id=dispersion_id)
        dispersion.estatus_pago = nuevo_estatus
        dispersion.save()

        # Obtener los parámetros GET originales para mantener el filtro
        referer = request.META.get('HTTP_REFERER', '')
        if '?' in referer:
            return redirect(referer)
        else:
            return redirect('/dispersiones/listar/')
    
    return redirect('/dispersiones/listar/')