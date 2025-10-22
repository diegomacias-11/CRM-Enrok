from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Max
from .models import DocumentoActivacion
from .forms import DocumentoActivacionForm
from clientes.models import Cliente


# --- LISTAR ---
def activacion_listar(request):
    # Si el usuario es cliente, redirigir a su propio detalle
    if request.user.groups.filter(name="Cliente").exists():
        cliente = Cliente.objects.filter(usuario=request.user).first()
        if cliente:
            return redirect("activacion_detalle", cliente_id=cliente.id)

    cliente_id = request.GET.get("cliente")

    # Todos los clientes (solo para operativos/admin)
    clientes = Cliente.objects.all().order_by("nombre")
    lista_clientes = []
    clientes_completos = 0

    DOCS_REQUERIDOS = {
        'Carta de afiliación CONFEDIN',
        'Contrato de futura representación CONDEFIN',
        'Escrito de presentación del programa STPS',
        'Carátula del programa especial de productividad y competitividad',
        'Solicitud del análisis para la implementación del programa de productividad',
        'Convocatoria para la celebración de una asamblea en la CMPCA',
        'Notificación de asamblea',
        'Notificación de asamblea a trabajadores',
        '1er Asamblea del programa del productividad en la CMPCA',
        '2da Asamblea del programa del productividad en la CMPCA',
        'Dictamen de factibilidad',
        'Avocamiento programa de productividad',
        'Avocamiento programa de productividad STPS',
    }

    for cliente in clientes:
        docs = DocumentoActivacion.objects.filter(cliente=cliente).values_list("tipo_documento", flat=True)
        docs_set = set(docs)
        cumple = DOCS_REQUERIDOS.issubset(docs_set)
        if cumple:
            clientes_completos += 1
        lista_clientes.append({
            "id": cliente.id,
            "nombre": cliente.nombre,
            "total_documentos": len(docs_set),
            "requeridos": len(DOCS_REQUERIDOS),
            "cumple": cumple,
        })

    if cliente_id:
        lista_clientes = [c for c in lista_clientes if str(c["id"]) == str(cliente_id)]

    return render(request, "activacion/listar.html", {
        "resumen_clientes": lista_clientes,
        "clientes": clientes,
        "cliente": cliente_id,
        "total_documentos": clientes_completos,
    })


# --- DETALLE ---
def activacion_detalle(request, cliente_id=None):
    es_cliente = request.user.groups.filter(name="Cliente").exists()

    if es_cliente:
        cliente = get_object_or_404(Cliente, usuario=request.user)
    else:
        cliente = get_object_or_404(Cliente, id=cliente_id)

    documentos_recientes = (
        DocumentoActivacion.objects
        .filter(cliente=cliente)
        .values("tipo_documento")
        .annotate(ultima_fecha=Max("fecha_subida"))
    )

    documentos = DocumentoActivacion.objects.filter(
        cliente=cliente,
        fecha_subida__in=[d["ultima_fecha"] for d in documentos_recientes],
        tipo_documento__in=[d["tipo_documento"] for d in documentos_recientes]
    ).order_by("tipo_documento")

    DOCS_REQUERIDOS = [
        'Carta de afiliación CONFEDIN',
        'Contrato de futura representación CONDEFIN',
        'Escrito de presentación del programa STPS',
        'Carátula del programa especial de productividad y competitividad',
        'Solicitud del análisis para la implementación del programa de productividad',
        'Convocatoria para la celebración de una asamblea en la CMPCA',
        'Notificación de asamblea',
        'Notificación de asamblea a trabajadores',
        '1er Asamblea del programa del productividad en la CMPCA',
        '2da Asamblea del programa del productividad en la CMPCA',
        'Dictamen de factibilidad',
        'Avocamiento programa de productividad',
    ]

    normalizar = lambda t: t.lower().strip() if t else ""
    requeridos_normalizados = [normalizar(r) for r in DOCS_REQUERIDOS]
    existentes = set(normalizar(d.tipo_documento) for d in documentos)
    completados = sum(1 for doc in requeridos_normalizados if doc in existentes)
    porcentaje = round((completados / len(requeridos_normalizados)) * 100, 2)

    return render(request, "activacion/detalle.html", {
        "cliente": cliente,
        "documentos": documentos,
        "porcentaje": porcentaje,
        "completados": completados,
        "total_requeridos": len(requeridos_normalizados),
        "es_cliente": es_cliente,
    })


# --- AGREGAR ---
def activacion_agregar(request):
    next_url = request.GET.get("next")
    cliente_id = request.GET.get("cliente")

    if request.user.groups.filter(name="Cliente").exists():
        cliente_obj = Cliente.objects.filter(usuario=request.user).first()
    else:
        cliente_obj = Cliente.objects.filter(id=cliente_id).first()

    if not cliente_obj:
        return redirect("activacion_listar")

    if request.method == "POST":
        form = DocumentoActivacionForm(request.POST, request.FILES, initial={"cliente": cliente_obj})
        if form.is_valid():
            doc = form.save(commit=False)
            doc.cliente = cliente_obj
            doc.save()
            return redirect("activacion_detalle", cliente_id=cliente_obj.id)
        else:
            print("❌ Errores de validación:", form.errors)
    else:
        form = DocumentoActivacionForm(initial={"cliente": cliente_obj})

    return render(request, "activacion/agregar.html", {
        "form": form,
        "next_url": next_url or reverse("activacion_detalle", args=[cliente_obj.id]),
    })


# --- EDITAR ---
def activacion_editar(request, pk):
    doc = get_object_or_404(DocumentoActivacion, pk=pk)
    next_url = (
        request.POST.get('next') or request.GET.get('next')
        or reverse("activacion_detalle", args=[doc.cliente.id])
    )

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(next_url)
        if 'delete' in request.POST:
            doc.delete()
            return redirect(next_url)

        form = DocumentoActivacionForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = DocumentoActivacionForm(instance=doc)

    return render(request, 'activacion/editar.html', {
        'form': form,
        'documento': doc,
        'next_url': next_url,
    })


# --- HISTORIAL ---
def activacion_historial(request, cliente_id, tipo_documento):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    historial = DocumentoActivacion.objects.filter(
        cliente=cliente, tipo_documento=tipo_documento
    ).order_by("-fecha_subida")

    return render(request, "activacion/historial.html", {
        "cliente": cliente,
        "tipo_documento": tipo_documento.replace("_", " ").capitalize(),
        "historial": historial,
    })
