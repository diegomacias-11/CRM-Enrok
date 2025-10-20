from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count, Max
from .models import DocumentoMaterialidad
from .forms import DocumentoMaterialidadForm
from clientes.models import Cliente


# --- LISTAR DOCUMENTOS AGRUPADOS POR CLIENTE ---
def materialidad_listar(request):
    cliente_id = request.GET.get("cliente")

    # --- Definimos los requerimientos por tipo ---
    DOCS_FISICA = {"csf", "ine", "domicilio", "generales"}
    DOCS_MORAL = {"acta_constitutiva", "poder", "identificacion_apoderado", "domicilio", "rfc", "opinion_cumplimiento", "csf"}

    # Todos los clientes (aunque no tengan documentos)
    clientes = Cliente.objects.all().order_by("nombre")

    # Contar documentos existentes por cliente
    documentos = DocumentoMaterialidad.objects.select_related("cliente")
    resumen_clientes = documentos.values("cliente__id").annotate(total=Count("id"))
    totales = {item["cliente__id"]: item["total"] for item in resumen_clientes}

    lista_clientes = []
    clientes_completos = 0  # contador de clientes con 100% de cumplimiento

    for cliente in clientes:
        docs_cliente = DocumentoMaterialidad.objects.filter(cliente=cliente).values_list("tipo_documento", flat=True)
        docs_set = set(docs_cliente)

        # Determinar tipo de persona y sus requerimientos
        if cliente.tipo_persona.lower().strip() in ["persona física", "fisica"]:
            requeridos = DOCS_FISICA
        else:
            requeridos = DOCS_MORAL

        # Evaluar cumplimiento
        cumple = requeridos.issubset(docs_set)
        if cumple:
            clientes_completos += 1

        lista_clientes.append({
            "id": cliente.id,
            "nombre": cliente.nombre,
            "tipo_persona": cliente.tipo_persona,
            "total_documentos": len(docs_set),
            "requeridos": len(requeridos),
            "cumple": cumple,
        })

    # Si hay filtro por cliente
    if cliente_id:
        lista_clientes = [c for c in lista_clientes if str(c["id"]) == str(cliente_id)]

    return render(request, "materialidad/listar.html", {
        "resumen_clientes": lista_clientes,
        "clientes": clientes,
        "cliente": cliente_id,
        "total_documentos": clientes_completos,  # 👈 este es el total con cumplimiento al 100%
    })


# --- DETALLE DE DOCUMENTOS POR CLIENTE ---
def materialidad_detalle(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)

    # Obtener la versión más reciente por tipo_documento
    documentos_recientes = (
        DocumentoMaterialidad.objects
        .filter(cliente=cliente)
        .values("tipo_documento")
        .annotate(ultima_fecha=Max("fecha_subida"))
    )

    # Obtener los registros completos de esas últimas versiones
    documentos = DocumentoMaterialidad.objects.filter(
        cliente=cliente,
        fecha_subida__in=[d["ultima_fecha"] for d in documentos_recientes],
        tipo_documento__in=[d["tipo_documento"] for d in documentos_recientes]
    ).order_by("tipo_documento")

    total_documentos = documentos.count()

    # --- Calcular cumplimiento (igual que antes) ---
    DOCS_FISICA = [
        "CSF",
        "INE",
        "Comprobante de Domicilio",
        "Datos Generales",
    ]
    DOCS_MORAL = [
        "Acta Constitutiva",
        "Poder",
        "Identificación del Apoderado",
        "Comprobante de Domicilio",
        "RFC",
        "Opinión de Cumplimiento de Obligaciones Fiscales",
        "CSF",
    ]
    tipo = cliente.tipo_persona.lower().strip()
    requeridos = DOCS_FISICA if tipo in ["persona física", "fisica"] else DOCS_MORAL

    def normalizar(texto):
        return texto.lower().strip() if texto else ""

    requeridos_normalizados = [normalizar(r) for r in requeridos]
    documentos_existentes = set(normalizar(d.tipo_documento) for d in documentos)
    completados = sum(1 for doc in requeridos_normalizados if doc in documentos_existentes)
    total_requeridos = len(requeridos_normalizados)
    porcentaje = round((completados / total_requeridos) * 100, 2) if total_requeridos else 0

    return render(request, "materialidad/detalle.html", {
        "cliente": cliente,
        "documentos": documentos,
        "total_documentos": total_documentos,
        "porcentaje": porcentaje,
        "completados": completados,
        "total_requeridos": total_requeridos,
    })


# --- AGREGAR NUEVO DOCUMENTO ---
def materialidad_agregar(request):
    next_url = request.GET.get("next")
    cliente_id = request.GET.get("cliente")
    cliente_obj = Cliente.objects.filter(id=cliente_id).first() if cliente_id else None

    if request.method == "POST":
        form = DocumentoMaterialidadForm(request.POST, request.FILES, initial={"cliente": cliente_obj})

        if form.is_valid():
            # 👇 Crear el documento sin guardar aún
            doc = form.save(commit=False)
            if cliente_obj:
                doc.cliente = cliente_obj  # Asignamos cliente manualmente
            doc.save()
            
            # Redirección
            if next_url:
                return redirect(next_url)
            elif cliente_obj:
                return redirect("materialidad_detalle", cliente_id=cliente_obj.id)
            return redirect("materialidad_listar")
        else:
            print("❌ Errores de validación:", form.errors)

    else:
        # 👉 Si venimos desde el detalle, preseleccionamos el cliente
        form = DocumentoMaterialidadForm(initial={"cliente": cliente_obj} if cliente_obj else None)

    return render(request, "materialidad/agregar.html", {
        "form": form,
        "next_url": next_url or reverse("materialidad_listar"),
    })


# --- EDITAR / ELIMINAR DOCUMENTO ---
def materialidad_editar(request, pk):
    doc = get_object_or_404(DocumentoMaterialidad, pk=pk)
    next_url = (
        request.POST.get('next')
        or request.GET.get('next')
        or reverse("materialidad_detalle", args=[doc.cliente.id])
    )

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return redirect(next_url)

        if 'delete' in request.POST:
            doc.delete()
            return redirect(next_url)

        form = DocumentoMaterialidadForm(request.POST, instance=doc)
        if form.is_valid():
            form.save()
            return redirect(next_url)
    else:
        form = DocumentoMaterialidadForm(instance=doc)

    return render(request, 'materialidad/editar.html', {
        'form': form,
        'documento': doc,
        'next_url': next_url,
    })

def materialidad_historial(request, cliente_id, tipo_documento):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    historial = DocumentoMaterialidad.objects.filter(
        cliente=cliente, tipo_documento=tipo_documento
    ).order_by("-fecha_subida")

    return render(request, "materialidad/historial.html", {
        "cliente": cliente,
        "tipo_documento": tipo_documento.replace("_", " ").capitalize(),
        "historial": historial,
    })