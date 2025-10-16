from django.shortcuts import render, get_object_or_404, redirect
from .models import Dispersion
from .forms import DispersionForm
from datetime import datetime
from clientes.models import Cliente
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.decorators import permission_required

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

@permission_required('dispersiones.view_dispersion', raise_exception=True)
def lista_dispersiones(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    now = datetime.now()
    cliente_id = request.GET.get('cliente')

    # 🔹 Si no vienen parámetros, redirigimos con mes/año actuales
    if not mes or not anio:
        return redirect(f"{request.path}?mes={now.month}&anio={now.year}&cliente={cliente_id or ''}")

    # 🔹 Normalizamos los parámetros
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

    # 🔹 Lista de años disponibles para el filtro
    anios = Dispersion.objects.dates('fecha', 'year')
    anios = [y.year for y in anios]
    if not anios:
        anios = [anio]  # 👈 Garantiza que siempre haya al menos un año visible

    # Query principal
    dispersiones = Dispersion.objects.filter(
        fecha__month=mes,
        fecha__year=anio
    ).order_by('fecha')

    # Filtro de cliente
    clientes = Cliente.objects.all()
    if cliente_id:
        dispersiones = dispersiones.filter(cliente_id=cliente_id)

    # Suma total del monto
    total_montos = dispersiones.aggregate(total=Sum('monto'))['total'] or 0

    # Render final
    return render(request, 'dispersiones/listar.html', {
        'dispersiones': dispersiones,
        'mes': str(mes),             # Mantener como string para comparación en el template
        'mes_nombre': mes_nombre,
        'anio': str(anio),
        'clientes': clientes,        # lista completa para el dropdown
        'cliente': cliente_id,       # cliente seleccionado
        'anios': anios,              # años disponibles
        'total_montos': total_montos,
    })

@permission_required('dispersiones.add_dispersion', raise_exception=True)
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
            dispersion.factura = dispersion.cliente.factura  # traer factura del cliente
            dispersion.save()
            return redirect(request.POST.get('next', '/dispersiones/listar/'))
    else:
        form = DispersionForm(mes=mes, anio=anio)

    return render(request, 'dispersiones/agregar.html', {
        'form': form,
        'titulo': 'Agregar Nueva Dispersión',
        'next_url': next_url,
    })


@permission_required('dispersiones.change_dispersion', raise_exception=True)
def editar_dispersion(request, pk):
    dispersion = get_object_or_404(Dispersion, pk=pk)

    # 👇 Capturamos primero los parámetros originales de la URL
    mes_str = request.GET.get('mes')
    anio_str = request.GET.get('anio')

    # 👇 Creamos la URL de retorno ANTES de convertir a int
    next_url = f'/dispersiones/listar/?mes={mes_str}&anio={anio_str}'

    # 👇 Ahora sí, convertimos a int para usar en el form
    mes = int(mes_str or datetime.now().month)
    anio = int(anio_str or datetime.now().year)

    if request.method == 'POST':
        form = DispersionForm(request.POST, instance=dispersion, mes=mes, anio=anio)
        if form.is_valid():
            form.save()
            # Redirigimos al next_url conservando el mes/año originales
            return redirect(request.POST.get('next', next_url))
    else:
        form = DispersionForm(instance=dispersion)

    return render(request, 'dispersiones/editar.html', {
        'form': form,
        'titulo': 'Editar Dispersión',
        'dispersion': dispersion,
        'next_url': next_url
    })

@permission_required('dispersiones.delete_dispersion', raise_exception=True)
def dispersiones_eliminar(request, pk):
    dispersion = get_object_or_404(Dispersion, pk=pk)
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/dispersiones/listar/'))
    dispersion.delete()
    return redirect(next_url)

@permission_required('dispersiones.actualizar_estatus_dispersion', raise_exception=True)
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