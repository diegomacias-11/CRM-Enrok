from django.urls import path
from . import views

urlpatterns = [
    path('agregar/', views.agregar_cliente, name='clientes_agregar'),
    path('listar/', views.listar_clientes, name='clientes_listar'),
    path('editar/<int:id>/', views.editar_cliente, name='clientes_editar'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='clientes_eliminar'),
]