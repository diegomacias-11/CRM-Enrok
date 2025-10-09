from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Comision, Pago, Dispersion
from datetime import datetime
from .forms import PagoForm
from urllib.parse import urlparse, parse_qs, unquote
from datetime import date

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

def listar_comisiones(request):
    liberar_comisiones_mes_anterior()

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

    mes_nombre = MESES_ES.get(mes, "")

    # 🔹 Lista de años disponibles
    anios = Comision.objects.dates('dispersion__fecha', 'year')
    anios = [y.year for y in anios]
    if not anios:
        anios = [anio]

    # 🔹 Query principal de comisiones
    qs = Comision.objects.filter(
        dispersion__fecha__month=mes,
        dispersion__fecha__year=anio
    )

    if comisionista_filtro:
        qs = qs.filter(comisionista=comisionista_filtro)

    comisionistas = qs.values('comisionista').annotate(total=Sum('monto')).order_by('comisionista')

    total_comisiones = qs.aggregate(total=Sum('monto'))['total'] or 0
    total_liberado = qs.filter(estatus='Liberado').aggregate(total=Sum('monto'))['total'] or 0

    # 🔹 🔥 Restar solo los pagos correspondientes al periodo de la URL (no a la fecha real)
    abonos = Pago.objects.filter(
        mes=mes,  # periodo contable del pago
        anio=anio
    )

    if comisionista_filtro:
        abonos = abonos.filter(comisionista=comisionista_filtro)

    total_abonos = abonos.aggregate(total=Sum('monto'))['total'] or 0

    total_comisiones -= total_abonos
    total_liberado -= total_abonos

    # 🔹 Comisionistas totales
    comisionistas_todos = Comision.objects.values('comisionista').distinct().order_by('comisionista')

    return render(request, 'comisiones/listar.html', {
        'comisionistas': comisionistas,
        'mes': str(mes),
        'mes_nombre': mes_nombre,
        'anio': str(anio),
        'anios': anios,
        'comisionistas_todos': comisionistas_todos,
        'comisionista_filtro': comisionista_filtro,
        'total_comisiones': total_comisiones,
        'total_liberado': total_liberado,
    })

def detalle_comisiones(request, comisionista):
    from urllib.parse import urlparse, parse_qs
    volver_url = request.GET.get('volver', '/comisiones/listar/')

    parsed = urlparse(volver_url)
    query = parse_qs(parsed.query)
    mes = int(query.get('mes', [datetime.now().month])[0])
    mes_nombre = MESES_ES.get(mes, "")
    anio = int(query.get('anio', [datetime.now().year])[0])

    # Mostrar comisiones del mismo mes seleccionado
    detalle = Comision.objects.filter(
        comisionista=comisionista,
        dispersion__fecha__month=mes,
        dispersion__fecha__year=anio
    )

    abonos = Pago.objects.filter(
        comisionista=comisionista,
        mes=mes,
        anio=anio
    ).order_by('fecha_pago')

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
        'mes_nombre': mes_nombre,
        'anio': anio,
        'pendiente_pagar': pendiente_pagar,
    }

    return render(request, 'comisiones/detalle.html', context)

def registrar_pago(request, comisionista, pago_id=None):
    # URL de retorno
    next_url = request.GET.get('next', f'/comisiones/detalle/{comisionista}/')
    volver_url = request.GET.get('volver', None)

    # Extraer mes y año del contexto (desde la URL principal o el volver codificado)
    parsed = urlparse(next_url)
    query = parse_qs(parsed.query)
    mes = int(query.get('mes', [0])[0])
    anio = int(query.get('anio', [0])[0])

    # Si no los encuentra, intenta obtenerlos desde 'volver'
    if not mes or not anio:
        volver_url = query.get('volver', [None])[0]
        if volver_url:
            volver_decodificado = unquote(volver_url)
            parsed_volver = urlparse(volver_decodificado)
            query_volver = parse_qs(parsed_volver.query)
            mes = int(query_volver.get('mes', [0])[0])
            anio = int(query_volver.get('anio', [0])[0])

    # Obtener el pago si es edición
    pago = get_object_or_404(Pago, pk=pago_id, comisionista=comisionista) if pago_id else None

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(next_url)

        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            pago_guardado = form.save(commit=False)
            pago_guardado.comisionista = comisionista

            # 🔹 Asignar periodo contable (mes/año del filtro)
            if mes and anio:
                pago_guardado.mes = mes
                pago_guardado.anio = anio
            else:
                # fallback si no hay parámetros
                pago_guardado.mes = pago_guardado.fecha_pago.month
                pago_guardado.anio = pago_guardado.fecha_pago.year

            # 🔹 Guardar (esto actualizará mes_real/anio_real automáticamente)
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

    # Intentar obtener también del volver si no están directos
    if not mes or not anio:
        volver_url = query.get('volver', [None])[0]
        if volver_url:
            volver_decodificado = unquote(volver_url)
            parsed_volver = urlparse(volver_decodificado)
            query_volver = parse_qs(parsed_volver.query)
            mes = int(query_volver.get('mes', [0])[0])
            anio = int(query_volver.get('anio', [0])[0])

    if request.method == 'POST':
        if 'delete' in request.POST:
            pago.delete()
            return redirect(next_url)
        elif 'cancel' in request.POST:
            return redirect(next_url)
        else:
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

            # Actualizamos la comisión de esta dispersión según su estatus actual
            Comision.objects.filter(dispersion=dispersion).update(estatus=nuevo_estatus)

            # Revisamos todas las dispersiones del cliente en ese mes
            todas_dispersiones = Dispersion.objects.filter(
                cliente=cliente,
                fecha__month=mes,
                fecha__year=anio
            )

            # Si todas están pagadas → liberamos solo si ya es el siguiente mes
            if todas_dispersiones.exists() and all(d.estatus_pago == "Pagado" for d in todas_dispersiones):
                hoy = date.today()
                if (hoy.year > anio) or (hoy.year == anio and hoy.month > mes):
                    Comision.objects.filter(
                        cliente=cliente,
                        dispersion__fecha__month=mes,
                        dispersion__fecha__year=anio
                    ).update(estatus="Liberado")
                else:
                    Comision.objects.filter(
                        cliente=cliente,
                        dispersion__fecha__month=mes,
                        dispersion__fecha__year=anio
                    ).update(estatus="Pagado")
            else:
                # Alguna dispersión no está pagada → reflejar estatus real
                for d in todas_dispersiones:
                    Comision.objects.filter(dispersion=d).update(estatus=d.estatus_pago)

            return redirect(request.META.get('HTTP_REFERER', '/dispersiones/listar/'))
        
        except Exception as e:
            return redirect('/dispersiones/listar/')
    
    return redirect('/dispersiones/listar/')

def liberar_comisiones_mes_anterior():
    """
    Revisa todas las comisiones y marca como 'Liberado'
    aquellas cuyo mes ya pasó y todas las dispersiónes están pagadas.
    """
    hoy = date.today()

    # Tomamos todos los meses y años de dispersión que tengan comisiones
    meses_a_revisar = Comision.objects.values_list(
        'dispersion__fecha__month',
        'dispersion__fecha__year',
        'cliente'
    ).distinct()

    for mes, anio, cliente_id in meses_a_revisar:
        # Si ya estamos en el siguiente mes o año
        if (hoy.year > anio) or (hoy.year == anio and hoy.month > mes):
            # Traemos todas las dispersiónes del cliente en ese mes
            todas_dispersiones = Dispersion.objects.filter(
                cliente_id=cliente_id,
                fecha__month=mes,
                fecha__year=anio
            )

            if todas_dispersiones.exists() and all(d.estatus_pago == "Pagado" for d in todas_dispersiones):
                # Liberamos todas las comisiones de ese mes
                Comision.objects.filter(
                    cliente_id=cliente_id,
                    dispersion__fecha__month=mes,
                    dispersion__fecha__year=anio
                ).update(estatus="Liberado")
            else:
                # Alguna dispersión no está pagada → mantenemos estatus real
                for d in todas_dispersiones:
                    Comision.objects.filter(dispersion=d).update(estatus=d.estatus_pago)