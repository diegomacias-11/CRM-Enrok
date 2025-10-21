from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from clientes.models import Cliente
from django.contrib import messages
from django.db.models import Sum, Q
from django.db.models.functions import ExtractMonth, ExtractYear
from dispersiones.models import Dispersion


# ---------------------------
# 🏠 DASHBOARD INTERNO (Enrok)
# ---------------------------
@login_required
def post_login_redirect(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'core/core.html', {'clientes': clientes})


# ---------------------------
# 👤 EDITAR PERFIL DE USUARIO
# ---------------------------
def editar_usuario(request):
    usuario = request.user  # obtiene al usuario actual logueado

    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', '')
        usuario.last_name = request.POST.get('last_name', '')
        usuario.email = request.POST.get('email', '')
        usuario.save()
        messages.success(request, 'Tu perfil se actualizó correctamente.')
        return redirect('enrok')

    return render(request, 'usuario.html', {'usuario': request.user})


# ---------------------------
# 📅 Diccionario de meses en español
# ---------------------------
MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


# ---------------------------
# 📊 REPORTE MENSUAL
# ---------------------------
def reporte_dispersiones(request):
    """
    Reporte mensual que muestra totales globales:
    - Total Dispersado (monto)
    - Total Facturado (total_honorarios)
    - Total Pendiente (honorarios de facturas no pagadas)
    """

    resumen = (
        Dispersion.objects
        .annotate(
            mes=ExtractMonth('fecha'),
            anio=ExtractYear('fecha'),
        )
        .values('mes', 'anio')
        .annotate(
            total_dispersiones=Sum('monto'),
            total_facturado=Sum('total_honorarios'),
            total_pendiente=Sum('total_honorarios', filter=~Q(estatus_pago="Pagado")),
        )
        .order_by('-anio', '-mes')
    )

    # Agregar nombre de mes en español
    for r in resumen:
        r["mes_nombre"] = MESES_ES.get(r["mes"], "")

    # ✅ Calcular totales globales para el encabezado
    total_dispersiones = sum(r["total_dispersiones"] or 0 for r in resumen)
    total_facturado = sum(r["total_facturado"] or 0 for r in resumen)
    total_pendiente = sum(r["total_pendiente"] or 0 for r in resumen)

    return render(request, 'reporte/reporte.html', {
        'resumen': resumen,
        'total_dispersiones': total_dispersiones,
        'total_facturado': total_facturado,
        'total_pendiente': total_pendiente,
    })


# ---------------------------
# 📄 DETALLE POR MES
# ---------------------------
def reporte_detalle_dispersiones(request):
    """
    Muestra los clientes con honorarios pendientes o parciales
    para un mes y año seleccionados.
    """
    mes = int(request.GET.get('mes'))
    anio = int(request.GET.get('anio'))

    dispersiones = Dispersion.objects.filter(
        fecha__month=mes,
        fecha__year=anio,
        estatus_pago__in=["Pendiente", "Parcial"]
    ).order_by('cliente__nombre')

    mes_nombre = MESES_ES.get(mes, "")
    total_pendiente = dispersiones.aggregate(total=Sum('total_honorarios'))['total'] or 0

    return render(request, 'reporte/reporte_detalle.html', {
        'dispersiones': dispersiones,
        'mes': mes,
        'anio': anio,
        'mes_nombre': mes_nombre,
        'total_pendiente': total_pendiente,
    })


# ---------------------------
# 🧑‍💼 PANEL CLIENTE
# ---------------------------
@login_required
def panel_cliente(request):
    """
    Vista principal del panel para los usuarios del grupo 'Cliente'.
    """
    cliente = getattr(request.user, 'cliente_asociado', None)
    return render(request, 'clientes/panel_cliente.html', {'cliente': cliente})

@login_required
def dispersiones_cliente(request):
    """
    Reporte mensual exclusivo para el cliente logueado.
    Muestra solo sus dispersiones agrupadas por mes y año,
    con los totales calculados individualmente.
    """
    cliente = getattr(request.user, 'cliente_asociado', None)
    if not cliente:
        return redirect('panel_cliente')

    resumen = (
        Dispersion.objects
        .filter(cliente=cliente)
        .annotate(
            mes=ExtractMonth('fecha'),
            anio=ExtractYear('fecha'),
        )
        .values('mes', 'anio')
        .annotate(
            total_dispersiones=Sum('monto'),
            total_facturado=Sum('total_honorarios'),
            total_pendiente=Sum('total_honorarios', filter=~Q(estatus_pago="Pagado")),
        )
        .order_by('-anio', '-mes')
    )

    # Agregar nombre de mes en español
    for r in resumen:
        r["mes_nombre"] = MESES_ES.get(r["mes"], "")

    # Totales del cliente logueado
    total_dispersiones = sum(r["total_dispersiones"] or 0 for r in resumen)
    total_facturado = sum(r["total_facturado"] or 0 for r in resumen)
    total_pendiente = sum(r["total_pendiente"] or 0 for r in resumen)

    return render(request, 'clientes/reporte_dispersiones.html', {
        'resumen': resumen,
        'total_dispersiones': total_dispersiones,
        'total_facturado': total_facturado,
        'total_pendiente': total_pendiente,
        'cliente': cliente,
    })

@login_required
def reporte_detalle_cliente(request):
    """
    Muestra las dispersiones del cliente logueado
    para un mes y año seleccionados.
    """
    cliente = getattr(request.user, 'cliente_asociado', None)
    if not cliente:
        return redirect('panel_cliente')

    mes = int(request.GET.get('mes'))
    anio = int(request.GET.get('anio'))

    dispersiones = Dispersion.objects.filter(
        cliente=cliente,
        fecha__month=mes,
        fecha__year=anio
    ).order_by('fecha')

    mes_nombre = MESES_ES.get(mes, "")
    total_pendiente = dispersiones.aggregate(total=Sum('total_honorarios'))['total'] or 0

    return render(request, 'clientes/detalle_cliente.html', {
        'cliente': cliente,
        'dispersiones': dispersiones,
        'mes': mes,
        'anio': anio,
        'mes_nombre': mes_nombre,
        'total_pendiente': total_pendiente,
    })
