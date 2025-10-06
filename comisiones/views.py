from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Comision, Pago, Dispersion
from datetime import datetime
from .forms import PagoForm
from urllib.parse import urlparse, parse_qs
from django.views.decorators.csrf import csrf_exempt

def listar_comisiones(request):
    mes = request.GET.get('mes')
    anio = request.GET.get('anio')
    comisionista_filtro = request.GET.get('comisionista')
    now = datetime.now()

    if not mes or not anio:
        return redirect(f"{request.path}?mes={now.month}&anio={now.year}")

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

    anios = Comision.objects.dates('dispersion__fecha', 'year')
    anios = [y.year for y in anios]

    # Query principal
    qs = Comision.objects.filter(
        dispersion__fecha__month=mes,
        dispersion__fecha__year=anio
    )

    # Aplicar filtro por comisionista si existe
    if comisionista_filtro:
        qs = qs.filter(comisionista=comisionista_filtro)

    comisionistas = qs.values('comisionista').annotate(total=Sum('monto')).order_by('comisionista')

    # Todos los comisionistas para el dropdown
    comisionistas_todos = Comision.objects.values('comisionista').distinct().order_by('comisionista')

    return render(request, 'comisiones/listar.html', {
        'comisionistas': comisionistas,
        'mes': str(mes),
        'anio': str(anio),
        'anios': anios,
        'comisionistas_todos': comisionistas_todos,  # <- para el dropdown
        'comisionista_filtro': comisionista_filtro,  # <- para mantener seleccionado
    })


def detalle_comisiones(request, comisionista):
    from urllib.parse import urlparse, parse_qs

    volver_url = request.GET.get('volver', '/comisiones/listar/')

    parsed = urlparse(volver_url)
    query = parse_qs(parsed.query)
    mes = int(query.get('mes', [datetime.now().month])[0])
    anio = int(query.get('anio', [datetime.now().year])[0])

    # Comisiones filtradas por mes y año
    detalle = Comision.objects.filter(
        comisionista=comisionista,
        dispersion__fecha__month=mes,
        dispersion__fecha__year=anio
    ).order_by('dispersion__fecha')

    # Abonos/pagos filtrados por mes y año
    abonos = Pago.objects.filter(
        comisionista=comisionista,
        mes=mes,
        anio=anio
    ).order_by('fecha_pago')

    # Calcular pendiente por pagar
    total_liberadas = detalle.filter(estatus='Liberado').aggregate(Sum('monto'))['monto__sum'] or 0
    total_abonos = abonos.aggregate(Sum('monto'))['monto__sum'] or 0
    pendiente_pagar = total_liberadas - total_abonos

    context = {
        'comisionista': comisionista,
        'detalle': detalle,
        'abonos': abonos,
        'next': request.get_full_path(),
        'volver_url': volver_url,
        'mes': mes,
        'anio': anio,
        'pendiente_pagar': pendiente_pagar,  # <-- NUEVO
    }

    return render(request, 'comisiones/detalle.html', context)


def registrar_pago(request, comisionista, pago_id=None):
    # URL de retorno
    next_url = request.GET.get('next', f'/comisiones/detalle/{comisionista}/')

    # Obtener el pago si es editar
    if pago_id:
        pago = get_object_or_404(Pago, pk=pago_id, comisionista=comisionista)
    else:
        pago = None

    # Extraer mes y año de la URL next para asignar al pago
    parsed = urlparse(next_url)
    query = parse_qs(parsed.query)
    mes = int(query.get('mes', [0])[0])
    anio = int(query.get('anio', [0])[0])

    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            pago_guardado = form.save(commit=False)
            pago_guardado.comisionista = comisionista

            # Si mes y año vienen de la URL next, los usamos
            if mes and anio:
                pago_guardado.mes = mes
                pago_guardado.anio = anio
            else:
                # Si no, los extraemos de la fecha del pago
                pago_guardado.mes = pago_guardado.fecha_pago.month
                pago_guardado.anio = pago_guardado.fecha_pago.year

            pago_guardado.save()
            return redirect(next_url)
    else:
        form = PagoForm(instance=pago)

    return render(request, 'comisiones/pago.html', {
        'form': form,
        'comisionista': comisionista,
        'pago': pago,
        'next_url': next_url,
        'mes': mes,
        'anio': anio,
    })


def editar_pago(request, comisionista, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id, comisionista=comisionista)
    next_url = request.GET.get('next', f'/comisiones/detalle/{comisionista}/')

    parsed = urlparse(next_url)
    query = parse_qs(parsed.query)
    mes = int(query.get('mes', [0])[0])
    anio = int(query.get('anio', [0])[0])

    if request.method == 'POST':
        if 'delete' in request.POST:
            pago.delete()
            return redirect(next_url)
        elif 'cancel' in request.POST:
            return redirect(next_url)
        else:
            # Guardar cambios
            form = PagoForm(request.POST, instance=pago)
            if form.is_valid():
                pago_guardado = form.save(commit=False)
                pago_guardado.comisionista = comisionista
                pago_guardado.mes = mes
                pago_guardado.anio = anio
                pago_guardado.save()
                return redirect(next_url)
    else:
        form = PagoForm(instance=pago)

    return render(request, 'comisiones/editar.html', {
        'form': form,
        'comisionista': comisionista,
        'pago': pago,
        'mes': mes,
        'anio': anio,
        'next_url': next_url,
    })

def actualizar_estatus_cliente_global(cliente, mes, anio):
    """
    Marca como 'Liberado' todas las comisiones de un cliente
    en el mismo mes y año si todas están en 'Pagado'.
    """
    comisiones_mes = Comision.objects.filter(
        cliente=cliente,
        dispersion__fecha__month=mes,
        dispersion__fecha__year=anio
    )

    if comisiones_mes.exists() and all(c.estatus == "Pagado" for c in comisiones_mes):
        comisiones_mes.update(estatus="Liberado")


def actualizar_estatus_dispersion(request):
    if request.method == "POST":
        try:
            dispersion_id = int(request.POST.get("id"))
            nuevo_estatus = request.POST.get("estatus_pago")
            
            dispersion = Dispersion.objects.get(id=dispersion_id)
            dispersion.estatus_pago = nuevo_estatus
            dispersion.save(update_fields=["estatus_pago"])
            
            cliente = dispersion.cliente
            mes = dispersion.fecha.month
            anio = dispersion.fecha.year

            # Actualizamos la comisión de esta dispersión según su estatus
            Comision.objects.filter(dispersion=dispersion).update(estatus=nuevo_estatus)

            # Revisamos todas las dispersiónes del cliente en ese mes
            todas_dispersiones = Dispersion.objects.filter(
                cliente=cliente,
                fecha__month=mes,
                fecha__year=anio
            )

            # Si todas están pagadas → liberamos todas las comisiones
            if todas_dispersiones.exists() and all(d.estatus_pago == "Pagado" for d in todas_dispersiones):
                Comision.objects.filter(
                    cliente=cliente,
                    dispersion__fecha__month=mes,
                    dispersion__fecha__year=anio
                ).update(estatus="Liberado")
            else:
                # Si alguna no está pagada → regresamos a estatus real (Pendiente o Pagado)
                for d in todas_dispersiones:
                    Comision.objects.filter(dispersion=d).update(estatus=d.estatus_pago)

            return redirect(request.META.get('HTTP_REFERER', '/dispersiones/listar/'))
        
        except Exception as e:
            return redirect('/dispersiones/listar/')
    
    return redirect('/dispersiones/listar/')