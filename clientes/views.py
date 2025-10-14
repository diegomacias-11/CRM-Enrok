from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClienteForm
from .models import Cliente

# ==========================
# LISTAR CLIENTES
# ==========================
def listar_clientes(request):
    cliente_id = request.GET.get('cliente')
    clientes = Cliente.objects.all().order_by('nombre')
    
    if cliente_id:
        clientes = clientes.filter(id=cliente_id)
    
    return render(request, 'clientes/listar.html', {
        'clientes': clientes,
        'cliente_seleccionado': cliente_id
    })


# ==========================
# AGREGAR CLIENTE
# ==========================
def agregar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes_listar')  # Redirige directamente a la lista
    else:
        form = ClienteForm()
    
    return render(request, 'clientes/agregar.html', {'form': form})


# ==========================
# EDITAR CLIENTE
# ==========================
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes_listar')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/editar.html', {
        'form': form,
        'cliente': cliente
    })


# ==========================
# ELIMINAR CLIENTE
# ==========================
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    cliente.delete()
    return redirect('clientes_listar')