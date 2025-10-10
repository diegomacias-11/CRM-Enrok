from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from clientes.models import Cliente

@login_required
def post_login_redirect(request):
    clientes = Cliente.objects.all().order_by('nombre')
    return render(request, 'core/core.html',{
        'clientes': clientes,})