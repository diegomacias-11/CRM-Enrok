from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Max
from .models import DocumentoMaterialidad
from .forms import DocumentoMaterialidadForm
from clientes.models import Cliente


# --- LISTAR ---
def materialidad_listar(request):
    if request.user.groups.filter(name="Cliente").exists():
        cliente = Cliente.objects.filter(usuario=request.user).first()
        if cliente:
            return redirect("materialidad_detalle", cliente_id=cliente.id)

    cliente_id = request.GET.get("cliente")

    DOCS_FISICA = {"csf", "ine", "domicilio", "generales"}
    DOCS_MORAL = {"acta_constitutiva", "poder", "identificacion_apoderado",
                  "domicilio", "rfc", "opinion_cumplimiento", "csf"}

    clientes = Cliente.objects.all().order_by("nombre")
    lista_clientes = []
    clientes_completos = 0

    for cliente in clientes:
        docs = DocumentoMaterialidad.objects.filter(cliente=cliente).values_list("tipo_documento", flat=True)
        docs_set = set(docs)
        requeridos = DOCS_FISICA if cliente.tipo_persona.lower().strip() in ["persona física", "fisica"] else DOCS_MORAL
        cumple = requeridos.issubset(docs_set)
        if cumple:
            clientes_completos += 1
        lista_clientes.append({
            "id": cliente.id,
            "nombre": cliente.nombre,
            "total_documentos": len(docs_set),
            "requeridos": len(requeridos),
            "cumple": cumple,
        })

    if cliente_id:
        lista_clientes = [c for c in lista_clientes if str(c["id"]) == str(cliente_id)]

    return render(request, "materialidad/listar.html", {
        "resumen_clientes": lista_clientes,
        "clientes": clientes,
        "cliente": cliente_id,
        "total_documentos": clientes_completos,
    })


# --- DETALLE ---
def materialidad_detalle(request, cliente_id=None):
    es_cliente = request.user.groups.filter(name="Cliente").exists()

    if es_cliente:
        cliente = get_object_or_404(Cliente, usuario=request.user)
    else:
        cliente = get_object_or_404(Cliente, id=cliente_id)

    documentos_recientes = (
        DocumentoMaterialidad.objects
        .filter(cliente=cliente)
        .values("tipo_documento")
        .annotate(ultima_fecha=Max("fecha_subida"))
    )

    documentos = DocumentoMaterialidad.objects.filter(
        cliente=cliente,
        fecha_subida__in=[d["ultima_fecha"] for d in documentos_recientes],
        tipo_documento__in=[d["tipo_documento"] for d in documentos_recientes]
    ).order_by("tipo_documento")

    DOCS_FISICA = ["CSF", "INE", "Comprobante de Domicilio", "Datos Generales"]
    DOCS_MORAL = ["Acta Constitutiva", "Poder", "Identificación del Apoderado",
                  "Comprobante de Domicilio", "RFC",
                  "Opinión de Cumplimiento de Obligaciones Fiscales", "CSF"]

    tipo = cliente.tipo_persona.lower().strip()
    requeridos = DOCS_FISICA if tipo in ["persona física", "fisica"] else DOCS_MORAL

    normalizar = lambda t: t.lower().strip() if t else ""
    requeridos_normalizados = [normalizar(r) for r in requeridos]
    existentes = set(normalizar(d.tipo_documento) for d in documentos)
    completados = sum(1 for doc in requeridos_normalizados if doc in existentes)
    porcentaje = round((completados / len(requeridos_normalizados)) * 100, 2)

    return render(request, "materialidad/detalle.html", {
        "cliente": cliente,
        "documentos": documentos,
        "porcentaje": porcentaje,
        "completados": completados,
        "total_requeridos": len(requeridos_normalizados),
        "es_cliente": es_cliente,
    })


# --- AGREGAR ---
def materialidad_agregar(request):
    next_url = request.GET.get("next")
    cliente_id = request.GET.get("cliente")

    # Detectar cliente (según usuario o URL)
    if request.user.groups.filter(name="Cliente").exists():
        cliente_obj = Cliente.objects.filter(usuario=request.user).first()
    else:
        cliente_obj = Cliente.objects.filter(id=cliente_id).first()

    if not cliente_obj:
        return redirect("materialidad_listar")

    if request.method == "POST":
        # 👇 Aquí se pasa el cliente en initial, igual que en GET
        form = DocumentoMaterialidadForm(request.POST, request.FILES, initial={"cliente": cliente_obj})
        if form.is_valid():
            doc = form.save(commit=False)
            doc.cliente = cliente_obj
            doc.save()
            return redirect("materialidad_detalle", cliente_id=cliente_obj.id)
        else:
            print("❌ Errores de validación:", form.errors)
    else:
        form = DocumentoMaterialidadForm(initial={"cliente": cliente_obj})

    return render(request, "materialidad/agregar.html", {
        "form": form,
        "next_url": next_url or reverse("materialidad_detalle", args=[cliente_obj.id]),
    })


# --- EDITAR ---
def materialidad_editar(request, pk):
    doc = get_object_or_404(DocumentoMaterialidad, pk=pk)
    next_url = (
        request.POST.get('next') or request.GET.get('next')
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


# --- HISTORIAL ---
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
