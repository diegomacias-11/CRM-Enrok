from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from clientes.models import Cliente
from django.contrib import messages

@login_required
def post_login_redirect(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'core/core.html',{
        'clientes': clientes,})

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